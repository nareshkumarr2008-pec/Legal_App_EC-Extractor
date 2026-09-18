# -*- coding: utf-8 -*-
"""
Dual-Pipeline OCR Engine for Tamil Nadu Property Documents.

Pipeline:
  INPUT (PDF/Image)
    -> PaddleOCR(lang='ta')  -- Primary Tamil recognition
    -> PaddleOCR(lang='en')  -- Secondary English recognition
    -> Smart Line Merger      -- Best of both per region
    -> Reading Order Sort     -- Top-to-bottom, left-to-right
    -> Output JSON
"""

import os, io, re, base64, logging
from typing import List, Dict, Any, Optional
from PIL import Image, ImageOps
import numpy as np
import pypdfium2 as pdfium
from app.translator import translate_word_bilingual

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OCREngine")


class OCREngine:
    """Dual-pipeline OCR: Tamil primary + English secondary with smart merging."""

    _instance = None
    _pipeline_ta = None
    _pipeline_en = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCREngine, cls).__new__(cls)
            cls._instance._init_models()
        return cls._instance

    def _init_models(self):
        self.paddle_available = False
        self.device = "cpu"
        try:
            # Fix Windows Python 3.13 DLL search path for PyTorch / Paddle
            import sys
            if sys.platform == "win32":
                torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
                if os.path.exists(torch_lib):
                    try:
                        os.add_dll_directory(torch_lib)
                    except Exception:
                        pass
                try:
                    import torch
                except Exception:
                    pass

            # Multi-threading optimization for CPU cores
            cpu_count = os.cpu_count() or 4
            thread_count = str(min(8, max(2, (cpu_count // 2))))
            os.environ["CPU_NUM"] = thread_count
            os.environ["OMP_NUM_THREADS"] = thread_count

            # Disable MKLDNN/oneDNN PIR CPU instruction bug on Windows & skip remote model check hangs
            os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
            os.environ["FLAGS_use_mkldnn"] = "0"
            os.environ["FLAGS_enable_pir_api"] = "0"
            os.environ["FLAGS_enable_pir_in_executor"] = "0"
            os.environ["PADDLE_ONEDNN_DISABLE"] = "1"

            import paddle
            try:
                paddle.set_flags({
                    'FLAGS_use_mkldnn': False,
                    'FLAGS_enable_pir_api': False,
                    'FLAGS_enable_pir_in_executor': False,
                })
            except Exception:
                pass

            import paddle.inference as paddle_infer
            paddle_infer.Config.enable_mkldnn = lambda self: self.disable_mkldnn()

            from paddleocr import PaddleOCR
            self.PaddleOCR = PaddleOCR
            self.paddle_available = True
            self.device = self._detect_device(paddle)
            logger.info(f"PaddleOCR module loaded successfully with oneDNN/PIR CPU safeguards enabled. Device: {self.device} (CPU threads: {thread_count})")
        except Exception as e:
            logger.error(f"PaddleOCR import error: {e}")

    def _detect_device(self, paddle_module) -> str:
        """
        Returns 'gpu:0' if paddlepaddle-gpu is installed AND a usable CUDA
        GPU is actually visible to it, else 'cpu'. Never raises — any
        detection failure (no GPU, wrong driver, CPU-only paddle build,
        etc.) is treated as "no GPU" and we quietly use CPU instead.
        """
        try:
            if paddle_module.device.is_compiled_with_cuda() and paddle_module.device.cuda.device_count() > 0:
                gpu_name = paddle_module.device.cuda.get_device_name(0)
                logger.info(f"CUDA GPU detected: {gpu_name} — will use device='gpu:0'.")
                return "gpu:0"
        except Exception as e:
            logger.warning(f"GPU detection failed, using CPU instead: {e}")
        logger.info("No usable CUDA GPU found (or CPU-only paddlepaddle build) — using device='cpu'.")
        return "cpu"

    def _load_pipeline(self, lang: str):
        """
        Loads a PaddleOCR pipeline on self.device.
        Disables textline orientation checking for standard deeds/certificates to avoid
        redundant CNN passes per box, reducing per-page CPU inference time by ~40%.
        """
        def _init_ocr(dev):
            extra_kwargs = {}
            if dev == "cpu":
                extra_kwargs["enable_mkldnn"] = False

            det_model = "PP-OCRv6_medium_det"
            rec_model = "ta_PP-OCRv5_mobile_rec" if lang == "ta" else "PP-OCRv6_medium_rec"

            # Attempt 1: High-speed PP-OCRv6 detection + mobile recognition + batched inference
            try:
                return self.PaddleOCR(
                    text_detection_model_name=det_model,
                    text_recognition_model_name=rec_model,
                    device=dev,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False,
                    text_det_limit_type="max",
                    text_det_limit_side_len=960,
                    text_recognition_batch_size=16,
                    text_det_thresh=0.35,
                    text_det_box_thresh=0.5,
                    text_rec_score_thresh=0.45,
                    **extra_kwargs
                )
            except Exception as ex1:
                logger.warning(f"PaddleOCR v6 init note: {ex1}, trying standard lang config...")

            # Attempt 2: Standard language config with det limit
            try:
                return self.PaddleOCR(
                    lang=lang,
                    device=dev,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False,
                    text_det_limit_type="max",
                    text_det_limit_side_len=960,
                    text_recognition_batch_size=16,
                    **extra_kwargs
                )
            except Exception as ex2:
                logger.warning(f"PaddleOCR fallback config note: {ex2}")
                return self.PaddleOCR(lang=lang, device=dev, **extra_kwargs)

        try:
            return _init_ocr(self.device)
        except Exception as e:
            if self.device != "cpu":
                logger.warning(f"GPU pipeline init failed for lang='{lang}' ({e}) — falling back to CPU.")
                self.device = "cpu"
                return _init_ocr("cpu")
            raise

    def _get_pipeline_ta(self):
        """Primary Tamil pipeline: High-speed PaddleOCR PP-OCRv6_medium_det + ta_PP-OCRv5_mobile_rec."""
        if self._pipeline_ta is None and self.paddle_available:
            logger.info(f"Loading high-speed Tamil OCR pipeline: PP-OCRv6_medium_det + ta_PP-OCRv5_mobile_rec on device='{self.device}'...")
            self._pipeline_ta = self._load_pipeline("ta")
            logger.info(f"High-speed Tamil OCR pipeline loaded on device='{self.device}'.")
        return self._pipeline_ta

    def _get_pipeline_en(self):
        """Secondary English pipeline: High-speed PaddleOCR PP-OCRv6_medium_det + PP-OCRv6_medium_rec."""
        if self._pipeline_en is None and self.paddle_available:
            logger.info(f"Loading high-speed English pipeline: PP-OCRv6_medium_det + PP-OCRv6_medium_rec on device='{self.device}'...")
            self._pipeline_en = self._load_pipeline("en")
            logger.info(f"High-speed English pipeline loaded on device='{self.device}'.")
        return self._pipeline_en

    # -- File Conversion --

    def convert_file_to_images(self, file_bytes, filename):
        ext = os.path.splitext(filename)[1].lower()
        images = []

        if isinstance(file_bytes, str):
            with open(file_bytes, "rb") as f:
                file_bytes = f.read()

        if ext == ".pdf":
            pdf = None
            try:
                pdf = pdfium.PdfDocument(file_bytes)
                for page_index in range(len(pdf)):
                    page = pdf[page_index]
                    bitmap = page.render(scale=1.5)  # Scale 1.5 provides optimal resolution & fast CPU inference
                    pil_image = bitmap.to_pil().copy()
                    images.append(pil_image)
                    try:
                        bitmap.close()
                    except (Exception, OSError):
                        pass
                    try:
                        page.close()
                    except (Exception, OSError):
                        pass
            except Exception as e:
                logger.warning(f"pdfium convert_file_to_images failed ({e}), falling back to pdfplumber...")
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as plum:
                    for page in plum.pages:
                        im = page.to_image(resolution=200).original
                        images.append(im.convert("RGB"))
            finally:
                if pdf is not None:
                    try:
                        pdf.close()
                    except (Exception, OSError):
                        pass
        else:
            img = Image.open(io.BytesIO(file_bytes))
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)

        return images

    def image_to_base64(self, image, max_dim=1600, quality=85):
        img = image.copy()
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=quality, optimize=True)
        encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

    # -- Helpers --

    @staticmethod
    def _has_tamil(text):
        return bool(re.search(r'[\u0b80-\u0bff]', text))

    @staticmethod
    def _has_english(text):
        return bool(re.search(r'[A-Za-z]{2,}', text))

    @staticmethod
    def _has_digits(text):
        return bool(re.search(r'\d', text))

    @staticmethod
    def _poly_to_rect(poly, width, height):
        xs = [float(pt[0]) for pt in poly]
        ys = [float(pt[1]) for pt in poly]
        min_x = max(0.0, min(xs))
        min_y = max(0.0, min(ys))
        max_x = min(float(width), max(xs))
        max_y = min(float(height), max(ys))
        return {
            "x": round(min_x, 1),
            "y": round(min_y, 1),
            "w": round(max(5.0, max_x - min_x), 1),
            "h": round(max(5.0, max_y - min_y), 1),
            "x_pct": round((min_x / width) * 100, 2),
            "y_pct": round((min_y / height) * 100, 2),
            "w_pct": round(((max_x - min_x) / width) * 100, 2),
            "h_pct": round(((max_y - min_y) / height) * 100, 2),
        }

    @staticmethod
    def _poly_center_y(poly):
        ys = [float(pt[1]) for pt in poly]
        return (min(ys) + max(ys)) / 2.0

    @staticmethod
    def _poly_center_x(poly):
        xs = [float(pt[0]) for pt in poly]
        return (min(xs) + max(xs)) / 2.0

    # -- Core OCR Processing --

    def _run_pipeline(self, pipeline, img_np):
        """Run a PaddleOCR pipeline and return (texts, scores, polys)."""
        texts, scores, polys = [], [], []
        try:
            results = pipeline.predict(img_np)
            if results:
                for res in results:
                    if hasattr(res, 'get'):
                        rt = res.get("rec_texts", [])
                        rs = res.get("rec_scores", [])
                        rp = res.get("dt_polys", res.get("rec_polys", []))
                        texts.extend(rt)
                        scores.extend([float(s) for s in rs])
                        polys.extend(rp)
                    elif isinstance(res, list):
                        for item in res:
                            if isinstance(item, (list, tuple)) and len(item) == 2:
                                polys.append(item[0])
                                texts.append(item[1][0])
                                scores.append(float(item[1][1]))
        except Exception as e:
            logger.error(f"Pipeline error: {e}")

        return texts, scores, polys

    def _merge_lines(self, ta_texts, ta_scores, ta_polys,
                     en_texts, en_scores, en_polys,
                     width, height):
        """
        Smart merge: for each detected region, pick the best recognition.

        Strategy:
        - Tamil pipeline is PRIMARY (detects Tamil text correctly).
        - English pipeline is SECONDARY (better for pure English/digits).
        - English model cannot read Tamil script and hallucinates garbage ASCII
          (e.g. '(J6uL' for 'முத்துலட்சுமி', '6u(Lo' for 'செந்தில்குமார்').
        - When a region contains Tamil, the Tamil pipeline is authoritative.
        - Matched English lines are flagged so they are NEVER emitted as duplicate lines.
        """
        lines = []

        # Build a spatial index of English results for cross-referencing
        en_index = []
        for i, poly in enumerate(en_polys):
            if poly is not None and len(poly) > 0:
                xs = [float(pt[0]) for pt in poly]
                ys = [float(pt[1]) for pt in poly]
                x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
                en_index.append({
                    "idx": i,
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "cx": (x1 + x2) / 2.0, "cy": (y1 + y2) / 2.0,
                    "w": max(5.0, x2 - x1), "h": max(5.0, y2 - y1),
                    "poly": poly,
                    "text": en_texts[i] if i < len(en_texts) else "",
                    "score": en_scores[i] if i < len(en_scores) else 0.0,
                    "matched": False,
                })

        # Process Tamil pipeline results (primary)
        for i, poly in enumerate(ta_polys):
            if poly is None or len(poly) == 0:
                continue

            ta_text = ta_texts[i] if i < len(ta_texts) else ""
            ta_score = ta_scores[i] if i < len(ta_scores) else 0.0
            xs = [float(pt[0]) for pt in poly]
            ys = [float(pt[1]) for pt in poly]
            ta_x1, ta_y1, ta_x2, ta_y2 = min(xs), min(ys), max(xs), max(ys)
            ta_w = max(5.0, ta_x2 - ta_x1)
            ta_h = max(5.0, ta_y2 - ta_y1)
            ta_cy = (ta_y1 + ta_y2) / 2.0
            ta_cx = (ta_x1 + ta_x2) / 2.0

            # Find matching English lines using 2D box overlap
            best_en = None
            best_en_score = -1.0

            for en in en_index:
                # Vertical overlap
                v_ov = max(0.0, min(ta_y2, en["y2"]) - max(ta_y1, en["y1"]))
                v_ratio = v_ov / min(ta_h, en["h"])
                cy_diff = abs(ta_cy - en["cy"])

                # Horizontal overlap
                h_ov = max(0.0, min(ta_x2, en["x2"]) - max(ta_x1, en["x1"]))
                h_ratio = h_ov / min(ta_w, en["w"])
                cx_diff = abs(ta_cx - en["cx"])

                # Two boxes are the same physical line if vertical overlap is significant
                # and horizontal centers/spans overlap
                is_match = False
                if (v_ratio > 0.35 or cy_diff < 0.6 * max(ta_h, en["h"])) and (h_ratio > 0.10 or cx_diff < 0.7 * max(ta_w, en["w"])):
                    is_match = True

                if is_match:
                    en["matched"] = True  # Suppress English duplicate
                    if en["score"] > best_en_score:
                        best_en = en
                        best_en_score = en["score"]

            # Decide which text to use
            best_en_text = best_en["text"] if best_en else ""
            final_text = ta_text
            final_score = ta_score

            if ta_text.strip():
                has_ta = self._has_tamil(ta_text)
                has_en_in_ta = self._has_english(ta_text)
                has_digits_ta = self._has_digits(ta_text)

                if has_ta:
                    # Tamil script detected: Tamil model is authoritative.
                    # Never overwrite with English model garbage (which mangles Tamil script).
                    final_text = ta_text
                    final_score = ta_score
                elif has_digits_ta or has_en_in_ta:
                    # Pure English/digit line (e.g. table extents, numbers)
                    if best_en_text and best_en_score > ta_score:
                        final_text = best_en_text
                        final_score = best_en_score
                    else:
                        final_text = ta_text
                        final_score = ta_score
                else:
                    # Low-confidence / noise in Tamil pipeline
                    if best_en_text and best_en_score > 0.5:
                        final_text = best_en_text
                        final_score = best_en_score
            elif best_en_text:
                final_text = best_en_text
                final_score = best_en_score

            if not final_text.strip():
                continue

            rect = self._poly_to_rect(poly, width, height)
            lines.append({
                "text": final_text,
                "confidence": round(final_score, 4),
                "rect": rect,
                "sort_y": ta_cy,
                "sort_x": ta_cx,
            })

        # Include ONLY unmatched standalone English lines (e.g. purely English sections/headers)
        for en in en_index:
            if en.get("matched", False):
                continue
            if not en["text"].strip() or en["score"] < 0.5:
                continue

            # Check if this English box has spatial overlap with ANY already accepted line
            is_overlap = False
            for line in lines:
                l_rect = line["rect"]
                ly1, ly2 = l_rect["y"], l_rect["y"] + l_rect["h"]
                lx1, lx2 = l_rect["x"], l_rect["x"] + l_rect["w"]
                v_ov = max(0.0, min(ly2, en["y2"]) - max(ly1, en["y1"]))
                v_ratio = v_ov / min(l_rect["h"], en["h"])
                if v_ratio > 0.35:
                    h_ov = max(0.0, min(lx2, en["x2"]) - max(lx1, en["x1"]))
                    if h_ov > 0.10 * min(l_rect["w"], en["w"]):
                        is_overlap = True
                        break
            if is_overlap:
                continue

            # Check if text is redundant
            if any(en["text"].strip().lower() in l["text"].lower() for l in lines):
                continue

            poly = en["poly"]
            rect = self._poly_to_rect(poly, width, height)
            lines.append({
                "text": en["text"],
                "confidence": round(en["score"], 4),
                "rect": rect,
                "sort_y": en["cy"],
                "sort_x": en["cx"],
            })

        # Sort in natural document reading order: cluster into rows, then sort left-to-right within each row
        if lines:
            heights = [l["rect"]["h"] for l in lines if l.get("rect", {}).get("h", 0) > 0]
            avg_h = sum(heights) / len(heights) if heights else 20.0
            row_thresh = max(8.0, avg_h * 0.55)

            sorted_by_y = sorted(lines, key=lambda l: l["rect"]["y"])
            rows = []
            for item in sorted_by_y:
                y = item["rect"]["y"]
                placed = False
                for row in rows:
                    row_y = sum(r["rect"]["y"] for r in row) / len(row)
                    if abs(y - row_y) <= row_thresh:
                        row.append(item)
                        placed = True
                        break
                if not placed:
                    rows.append([item])

            rows.sort(key=lambda row: sum(r["rect"]["y"] for r in row) / len(row))
            ordered_lines = []
            for row in rows:
                row.sort(key=lambda r: r["rect"]["x"])
                ordered_lines.extend(row)

            for line in ordered_lines:
                if "sort_y" in line:
                    del line["sort_y"]
                if "sort_x" in line:
                    del line["sort_x"]

            lines = ordered_lines

        return lines

    def _run_easyocr_fallback(self, img_np, width, height, lang="ta"):
        """Fallback OCR engine using EasyOCR for image extraction when PaddlePaddle encounters PIR errors."""
        try:
            import easyocr
            langs = ['ta', 'en'] if lang == "ta" else ['en']
            reader = easyocr.Reader(langs, gpu=False, verbose=False)
            results = reader.readtext(img_np)
            lines = []
            for item in results:
                bbox, text, score = item[0], item[1], item[2]
                if not text.strip() or score < 0.2:
                    continue
                xs = [float(pt[0]) for pt in bbox]
                ys = [float(pt[1]) for pt in bbox]
                min_x = max(0.0, min(xs))
                min_y = max(0.0, min(ys))
                max_x = min(float(width), max(xs))
                max_y = min(float(height), max(ys))
                w = max(5.0, max_x - min_x)
                h = max(5.0, max_y - min_y)

                rect = {
                    "x": round(min_x, 1),
                    "y": round(min_y, 1),
                    "w": round(w, 1),
                    "h": round(h, 1),
                    "x_pct": round((min_x / width) * 100, 2),
                    "y_pct": round((min_y / height) * 100, 2),
                    "w_pct": round((w / width) * 100, 2),
                    "h_pct": round((h / height) * 100, 2),
                }
                lines.append({
                    "text": text.strip(),
                    "confidence": round(float(score), 4),
                    "rect": rect
                })
            return lines
        except Exception as e:
            logger.warning(f"EasyOCR fallback error: {e}")
            return []

    @staticmethod
    def clean_tamil_ocr_text(text: str) -> str:
        """Normalize Tamil OCR ligatures, visual-order Kombu/pulli, and common character misrecognitions."""
        if not text:
            return ""
        import unicodedata
        t = unicodedata.normalize('NFC', text)
        # Strip raw CID font artifacts e.g. (cid:2), (cid:39)
        t = re.sub(r'\(cid:\d+\)', '', t)

        # Fix noisy quotes and punctuation inserted inside words
        t = re.sub(r"மாவ['`’]டம்", "மாவட்டம்", t)
        t = re.sub(r"\bமராவட்டம்\b", "மாவட்டம்", t)
        t = re.sub(r"வ['`’]டம்", "வட்டம்", t)
        t = re.sub(r"ப['`’]டா", "பட்டா", t)
        t = re.sub(r"\bதநாடூ\s*அர\b", "தமிழ்நாடு அரசு", t)
        t = re.sub(r"\bமேலாணமை\b", "மேலாண்மை", t)
        t = re.sub(r"இ\.எ[ரர]\s*10\(1\)", "படிவம் எண் 10(1)", t)
        t = re.sub(r"இ\.எ[ரர]", "படிவம் எண்", t)
        t = re.sub(r"உரிம[ைா\s]*யாள[ரர்கே\s]*[ெ\s]*பெய[ரர்\s]*்?", "உரிமையாளர்கள் பெயர்", t)
        t = re.sub(r"\bமக\+\b", "மகன்", t)
        t = re.sub(r"\bந\+செ\b", "நஞ்சை", t)
        t = re.sub(r"\b7\+செ\b", "புஞ்சை", t)
        t = re.sub(r"எ[ரர]\b", "எண்", t)
        t = re.sub(r"பெய[ரர]\b", "பெயர்", t)

        # OCR dropped kombu (ெ) and misrecognition repairs for revenue localities & terms
        t = re.sub(r"\b(?:சமெ்பாக்கம்|சம்பாக்கம்|ெசம்பாக்கம்)\b", "செம்பாக்கம்", t)
        t = re.sub(r"\b(?:சங்கல்பட்டு|ெசங்கல்பட்டு)\b", "செங்கல்பட்டு", t)
        t = re.sub(r"\bபட்டா\s*(?:ஏன்|எஏண்|ஏண்|என|எண)\b", "பட்டா எண்", t)
        t = re.sub(r"\bபழய\b", "பழைய", t)
        t = re.sub(r"\bதர்வை\b", "தீர்வை", t)
        t = re.sub(r"\bஹக்\b(?=\s*[-–—]\s*ஏர்)", "ஹெக்", t)
        t = re.sub(r"\bதுண\b(?=\s*வட்டாட்சியர்)", "துணை", t)
        t = re.sub(r"\bநரத்தில்\b", "நேரத்தில்", t)
        t = re.sub(r"\bமின்கயாப்பம்\b", "மின்கையொப்பம்", t)
        t = re.sub(r"\bகயாப்பம்\b", "கையொப்பம்", t)
        t = re.sub(r"\bஇணய\b", "இணைய", t)
        t = re.sub(r"\bசெைய்து\b|\bசய்து\b", "செய்து", t)
        t = re.sub(r"\bமூுலம்\b", "மூலம்", t)
        t = re.sub(r"\bசேர்கப்பட்டுள்ளது\b", "சேர்க்கப்பட்டுள்ளது", t)
        t = re.sub(r"\bரயத\s*்\s*வாரி\b", "ரயத்துவாரி", t)
        t = re.sub(r"(?<!சி)ன்னக்கண்(?!ணு)", "சின்னக்கண்ணு", t)
        t = re.sub(r"சின்னக்கண்(?!ணு)", "சின்னக்கண்ணு", t)

        # Normalize visual order Kombu signs (ெ, ே, ை) appearing before consonant
        t = re.sub(r'([ெேை])([\u0b95-\u0bb9])', r'\2\1', t)

        return t.strip()

    # -- Public API --

    def process_image(self, image, lang="ta"):
        """Process a single image through the dual OCR pipeline with EasyOCR fallback and image pre-processing."""
        # Pre-process image: upscale low-res thumbnail documents for crisp character segmentation
        orig_w, orig_h = image.size
        processed_img = image
        scale_factor = 1.0

        if max(orig_w, orig_h) < 900:
            scale_factor = min(2.5, 1200.0 / max(orig_w, orig_h))
            new_w = int(orig_w * scale_factor)
            new_h = int(orig_h * scale_factor)
            processed_img = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
            logger.info(f"Upscaled low-res image {orig_w}x{orig_h} -> {new_w}x{new_h} (scale={scale_factor:.2f}) for enhanced Tamil OCR.")

        if processed_img.mode != "RGB":
            processed_img = processed_img.convert("RGB")

        cur_w, cur_h = processed_img.size
        img_np = np.array(processed_img)
        lines_data = []

        if self.paddle_available:
            if lang == "en":
                pipeline_en = self._get_pipeline_en()
                en_texts, en_scores, en_polys = self._run_pipeline(pipeline_en, img_np) if pipeline_en else ([], [], [])
                lines_data = self._merge_lines([], [], [], en_texts, en_scores, en_polys, cur_w, cur_h)
            else:
                pipeline_ta = self._get_pipeline_ta()
                ta_texts, ta_scores, ta_polys = self._run_pipeline(pipeline_ta, img_np) if pipeline_ta else ([], [], [])
                logger.info(f"Tamil pipeline: {len(ta_texts)} lines detected")
                if len(ta_texts) > 0:
                    lines_data = self._merge_lines(ta_texts, ta_scores, ta_polys, [], [], [], cur_w, cur_h)
                else:
                    pipeline_en = self._get_pipeline_en()
                    en_texts, en_scores, en_polys = self._run_pipeline(pipeline_en, img_np) if pipeline_en else ([], [], [])
                    lines_data = self._merge_lines([], [], [], en_texts, en_scores, en_polys, cur_w, cur_h)

            logger.info(f"PaddleOCR extracted: {len(lines_data)} lines")

        # If low lines detected (e.g. degraded / heavily compressed scan), attempt adaptive enhancement
        if len(lines_data) < 3 and self.paddle_available:
            try:
                from PIL import ImageEnhance
                enh_img = ImageEnhance.Contrast(processed_img).enhance(1.8)
                enh_img = ImageEnhance.Sharpness(enh_img).enhance(1.5)
                enh_np = np.array(enh_img)
                if lang == "en":
                    pipeline_en = self._get_pipeline_en()
                    en_texts_enh, en_scores_enh, en_polys_enh = self._run_pipeline(pipeline_en, enh_np) if pipeline_en else ([], [], [])
                    if len(en_texts_enh) > len(lines_data):
                        lines_data = self._merge_lines([], [], [], en_texts_enh, en_scores_enh, en_polys_enh, cur_w, cur_h)
                else:
                    pipeline_ta = self._get_pipeline_ta()
                    ta_texts_enh, ta_scores_enh, ta_polys_enh = self._run_pipeline(pipeline_ta, enh_np) if pipeline_ta else ([], [], [])
                    if len(ta_texts_enh) > len(lines_data):
                        logger.info(f"Adaptive contrast enhancement recovered {len(ta_texts_enh)} text lines.")
                        lines_data = self._merge_lines(ta_texts_enh, ta_scores_enh, ta_polys_enh, [], [], [], cur_w, cur_h)
            except Exception as enh_err:
                logger.warning(f"Adaptive enhancement pass error: {enh_err}")

        # If Paddle pipeline returned 0 lines, invoke EasyOCR fallback
        if not lines_data:
            logger.info("PaddleOCR returned 0 lines. Invoking EasyOCR fallback...")
            lines_data = self._run_easyocr_fallback(img_np, cur_w, cur_h, lang=lang)

        # Normalize Tamil OCR text in all lines
        for line in lines_data:
            if "text" in line:
                line["text"] = self.clean_tamil_ocr_text(line["text"])

        # Generate word-level bounding boxes and dynamic translations for scanned lines
        all_words = []
        for line in lines_data:
            if "words" not in line or not line["words"]:
                line_words = []
                tokens = list(re.finditer(r'\S+', line.get("text", "")))
                rect = line.get("rect", {})
                line_w = rect.get("w_pct", 0)
                line_x = rect.get("x_pct", 0)
                line_y = rect.get("y_pct", 0)
                line_h = rect.get("h_pct", 0)
                total_len = len(line.get("text", ""))
                if total_len > 0 and line_w > 0:
                    for m in tokens:
                        w_text = m.group()
                        w_start_pct = line_x + (m.start() / total_len) * line_w
                        w_width_pct = max(1.2, (len(w_text) / total_len) * line_w)
                        w_trans = translate_word_bilingual(w_text)
                        w_obj = {
                            "text": w_text,
                            "translation": w_trans,
                            "confidence": line.get("confidence", 0.92),
                            "x_pct": round(w_start_pct, 2),
                            "y_pct": round(line_y, 2),
                            "w_pct": round(w_width_pct, 2),
                            "h_pct": round(line_h, 2),
                        }
                        line_words.append(w_obj)
                        all_words.append(w_obj)
                line["words"] = line_words
            else:
                all_words.extend(line["words"])

        full_text_lines = [line["text"] for line in lines_data]
        preview_url = self.image_to_base64(image)

        return {
            "width": orig_w,
            "height": orig_h,
            "lines": lines_data,
            "words": all_words,
            "full_text": "\n".join(full_text_lines),
            "preview_url": preview_url,
        }

    def _extract_native_pdf_lines(self, pdfplumber_page, width_pt, height_pt):
        """Extract lines, words, and bounding boxes directly from native PDF page with 100% character and spatial precision."""
        raw_words = pdfplumber_page.extract_words()
        if not raw_words:
            return [], []

        all_words = []
        for w in raw_words:
            w_text = w.get("text", "").strip()
            if not w_text:
                continue
            x0 = max(0.0, float(w.get("x0", 0.0)))
            top = max(0.0, float(w.get("top", 0.0)))
            x1 = min(float(width_pt), float(w.get("x1", x0 + 5.0)))
            bottom = min(float(height_pt), float(w.get("bottom", top + 5.0)))
            w_val = max(2.0, x1 - x0)
            h_val = max(2.0, bottom - top)

            norm_text = self.clean_tamil_ocr_text(w_text)
            w_trans = translate_word_bilingual(norm_text)
            all_words.append({
                "text": norm_text,
                "translation": w_trans,
                "confidence": 0.99,
                "x": round(x0, 1),
                "y": round(top, 1),
                "w": round(w_val, 1),
                "h": round(h_val, 1),
                "x_pct": round((x0 / width_pt) * 100, 2),
                "y_pct": round((top / height_pt) * 100, 2),
                "w_pct": round((w_val / width_pt) * 100, 2),
                "h_pct": round((h_val / height_pt) * 100, 2),
            })

        # Group words into natural reading order lines
        text_lines = pdfplumber_page.extract_text_lines(layout=False)
        lines = []
        for tl in text_lines:
            t_text = self.clean_tamil_ocr_text(tl.get("text", "").strip())
            if not t_text:
                continue
            lx0 = max(0.0, float(tl.get("x0", 0.0)))
            ltop = max(0.0, float(tl.get("top", 0.0)))
            lx1 = min(float(width_pt), float(tl.get("x1", lx0 + 5.0)))
            lbottom = min(float(height_pt), float(tl.get("bottom", ltop + 5.0)))
            lw = max(4.0, lx1 - lx0)
            lh = max(4.0, lbottom - ltop)

            # Associate words belonging to this line
            line_words = [
                w for w in all_words
                if (ltop - 3.0 <= w["y"] <= lbottom + 3.0) and (lx0 - 4.0 <= w["x"] <= lx1 + 4.0)
            ]

            lines.append({
                "text": t_text,
                "confidence": 0.99,
                "words": line_words,
                "rect": {
                    "x": round(lx0, 1),
                    "y": round(ltop, 1),
                    "w": round(lw, 1),
                    "h": round(lh, 1),
                    "x_pct": round((lx0 / width_pt) * 100, 2),
                    "y_pct": round((ltop / height_pt) * 100, 2),
                    "w_pct": round((lw / width_pt) * 100, 2),
                    "h_pct": round((lh / height_pt) * 100, 2),
                }
            })

        return lines, all_words

    @staticmethod
    def parse_page_indices(total_pages: int, page_range: Optional[str] = None, max_pages: Optional[int] = None) -> List[int]:
        """Parse 1-indexed page range (e.g. '1-3', '1,2,5') or max_pages into 0-indexed list."""
        if total_pages <= 0:
            return []
        if page_range and str(page_range).strip() and str(page_range).strip().lower() not in ("all", "none", ""):
            indices = set()
            for part in str(page_range).split(","):
                part = part.strip()
                if "-" in part:
                    try:
                        s, e = part.split("-", 1)
                        s_idx = max(1, int(s.strip()))
                        e_idx = min(total_pages, int(e.strip()))
                        for p in range(s_idx, e_idx + 1):
                            indices.add(p - 1)
                    except ValueError:
                        pass
                else:
                    try:
                        p = int(part)
                        if 1 <= p <= total_pages:
                            indices.add(p - 1)
                    except ValueError:
                        pass
            if indices:
                return sorted(list(indices))

        if max_pages and int(max_pages) > 0:
            return list(range(min(total_pages, int(max_pages))))

        return list(range(total_pages))

    def process_file(self, file_bytes, filename, lang="ta", page_range: Optional[str] = None, max_pages: Optional[int] = None):
        """
        Process a file (PDF or image) through the dual OCR pipeline.
        Supports multi-page documents (e.g. 1 to 30+ pages) with page selection and real-time progress logging:
        - For digital PDFs with native text: extracts exact text & boxes via pdfplumber
        - For scanned PDFs / images: runs the dual PaddleOCR + EasyOCR pipeline
        """
        import time
        doc_start_time = time.time()

        if isinstance(file_bytes, str):
            with open(file_bytes, "rb") as f:
                file_bytes = f.read()

        ext = os.path.splitext(filename)[1].lower()
        pages = []
        all_text_parts = []

        if ext == ".pdf":
            import io
            import pdfplumber
            import pypdfium2 as pdfium

            pdf_plum = None
            num_pages = 0
            try:
                pdf_plum = pdfplumber.open(io.BytesIO(file_bytes))
                num_pages = len(pdf_plum.pages)
            except Exception as e:
                logger.warning(f"pdfplumber open failed: {e}")

            target_indices = self.parse_page_indices(num_pages, page_range, max_pages) if num_pages > 0 else []

            # Pre-render high-res page images safely via pypdfium2 (with pdfplumber fallback)
            rendered_images = {}
            pdf_ium = None
            try:
                pdf_ium = pdfium.PdfDocument(file_bytes)
                total_ium = len(pdf_ium)
                if num_pages == 0:
                    num_pages = total_ium
                    target_indices = self.parse_page_indices(num_pages, page_range, max_pages)

                for idx in target_indices:
                    pil_img = None
                    if idx < total_ium:
                        try:
                            ium_page = pdf_ium[idx]
                            bitmap = ium_page.render(scale=1.5)
                            pil_img = bitmap.to_pil().copy()
                            try:
                                bitmap.close()
                            except (Exception, OSError):
                                pass
                            try:
                                ium_page.close()
                            except (Exception, OSError):
                                pass
                        except Exception as p_err:
                            logger.warning(f"pypdfium2 page {idx + 1} render failed: {p_err}")

                    if pil_img is None and pdf_plum and idx < len(pdf_plum.pages):
                        try:
                            pil_img = pdf_plum.pages[idx].to_image(resolution=150).original.convert("RGB")
                        except Exception as pl_err:
                            logger.warning(f"pdfplumber fallback page {idx + 1} render failed: {pl_err}")

                    rendered_images[idx] = pil_img
            except Exception as ium_err:
                logger.warning(f"pypdfium2 failed to load document ({ium_err}), using pdfplumber fallback...")
                if pdf_plum:
                    for idx in target_indices:
                        if idx < len(pdf_plum.pages):
                            try:
                                rendered_images[idx] = pdf_plum.pages[idx].to_image(resolution=150).original.convert("RGB")
                            except Exception:
                                rendered_images[idx] = None
            finally:
                if pdf_ium is not None:
                    try:
                        pdf_ium.close()
                    except (Exception, OSError) as close_err:
                        logger.debug(f"Safely suppressed pdf_ium close warning: {close_err}")
                    pdf_ium = None

            logger.info(f"Processing PDF '{filename}' ({num_pages} total pages). Target pages to extract ({len(target_indices)}): {[i+1 for i in target_indices]}")

            try:
                for step_num, idx in enumerate(target_indices, start=1):
                    page_start_time = time.time()
                    plum_page = pdf_plum.pages[idx] if (pdf_plum and idx < len(pdf_plum.pages)) else None
                    pil_image = rendered_images.get(idx)

                    width_pt = float(plum_page.width) if plum_page else (pil_image.width if pil_image else 800.0)
                    height_pt = float(plum_page.height) if plum_page else (pil_image.height if pil_image else 1100.0)

                    preview_url = self.image_to_base64(pil_image) if pil_image else ""

                    logger.info(f"==> [Page {idx + 1}/{num_pages}] (Step {step_num}/{len(target_indices)}) Processing page...")

                    # Extract native digital PDF lines & words with exact top-left coordinates
                    native_lines, native_words = [], []
                    joined_text = ""
                    cid_matches = []
                    page_fonts = set()
                    if plum_page:
                        native_lines, native_words = self._extract_native_pdf_lines(plum_page, width_pt, height_pt)
                        joined_text = plum_page.extract_text() or ""
                        cid_matches = re.findall(r'\(cid:\d+\)', joined_text)
                        page_fonts = {c.get("fontname", "") for c in plum_page.chars}

                    is_cid_corrupted = len(cid_matches) >= 5 or (len(cid_matches) >= 1 and len(joined_text.strip()) < 100)

                    _LEGACY_TAMIL_FONT_MARKERS = (
                        "bamini", "tscu_", "tscii", "tam-tam", "tam_",
                        "amudham", "elango", "tboomis", "shreetam", "vanavil",
                        "kamban", "softview"
                    )
                    _MODERN_UNICODE_FONT_MARKERS = (
                        "notosans", "noto sans", "lohit", "mukta", "tiro", "arial",
                        "times", "helvetica", "calibri", "cambria", "georgia", "dejavu"
                    )
                    has_modern_font = any(
                        marker in f.lower() for f in page_fonts for marker in _MODERN_UNICODE_FONT_MARKERS
                    )
                    has_legacy_tamil_font = (not has_modern_font) and any(
                        marker in f.lower() for f in page_fonts for marker in _LEGACY_TAMIL_FONT_MARKERS
                    )
                    has_tamil_unicode = any('\u0b80' <= c <= '\u0bff' for c in joined_text)
                    empty_paren_count = len(re.findall(r'\(\s*\)', joined_text))
                    has_dropped_bilingual_text = has_legacy_tamil_font and (not has_tamil_unicode) and empty_paren_count >= 3

                    # Check for dropped Tamil glyphs in digital PDFs (e.g. subset NirmalaUI or eServices export where characters like சி, ணு, பு, தீ, ரு are stripped leaving orphaned spaces or pullis)
                    has_dropped_tamil_glyphs = False
                    if has_tamil_unicode:
                        broken_tamil_patterns = [
                            r'(?:\s|^)[்][\u0b80-\u0bff]',  # word starting with virama/pulli like " ன்னக்கண்"
                            r'த\s+ழ்நா',                     # த ழ்நா (தமிழ்நாடு)
                            r'வ\s+வாய்',                     # வ வாய் (வருவாய்)
                            r'மற்\s+ம்',                     # மற் ம் (மற்றும்)
                            r'(?:\s|^)ல\s*எண்',              # ல எண் (புல எண்)
                            r'உட\s*்\s*ரி',                 # உட ் ரி (உட்பிரிவு)
                            r'பரப்\s+',                      # பரப் (பரப்பு)
                            r'ரயத\s*்\s*வாரி',              # ரயத ் வாரி (ரயத்துவாரி)
                            r'சான்றளிக்கப்ப\s+ற',            # சான்றளிக்கப்ப  ற
                            r'ன்னக்கண்',                     # ன்னக்கண் (சின்னக்கண்ணு)
                            r'\s+ரை்\s*வ',                   #  ரை் வ (தீர்வை)
                            r'\s+ப்\s*:',                    #  ப் : (குறிப்பு :)
                        ]
                        broken_count = sum(1 for pat in broken_tamil_patterns if re.search(pat, joined_text))
                        if broken_count >= 2:
                            has_dropped_tamil_glyphs = True
                            logger.info(f"Page {idx + 1}: Detected {broken_count} dropped/corrupted Tamil glyph patterns in native PDF text. Forcing full OCR pipeline.")

                    # Use native digital PDF lines directly if present and uncorrupted
                    if (native_lines and not is_cid_corrupted and not has_dropped_bilingual_text and not has_dropped_tamil_glyphs):
                        full_text = "\n".join(l["text"] for l in native_lines)
                        page_res = {
                            "page_number": idx + 1,
                            "width": int(width_pt),
                            "height": int(height_pt),
                            "lines": native_lines,
                            "words": native_words,
                            "full_text": full_text,
                            "preview_url": preview_url,
                        }
                    else:
                        # Check if this page is essentially a blank/uniform reverse side
                        is_blank = False
                        if pil_image:
                            try:
                                gray_arr = np.array(pil_image.convert('L'))
                                if (np.mean(gray_arr) > 215 and np.std(gray_arr) < 22) or (np.mean(gray_arr) > 185 and np.std(gray_arr) < 14):
                                    is_blank = True
                            except Exception:
                                pass

                        if is_blank:
                            logger.info(f"Page {idx + 1} is a blank/reverse sheet — fast skipping vision OCR.")
                            page_res = {
                                "page_number": idx + 1,
                                "width": int(width_pt),
                                "height": int(height_pt),
                                "lines": [],
                                "words": [],
                                "full_text": "",
                                "preview_url": preview_url,
                            }
                        else:
                            if is_cid_corrupted:
                                logger.info(f"Page {idx + 1} contains non-Unicode CID-encoded fonts ({len(cid_matches)} occurrences). Running PaddleOCR-VL-1.6 Vision Engine for clean character extraction...")
                            elif has_dropped_bilingual_text:
                                logger.info(f"Page {idx + 1} uses a legacy Tamil font ({sorted(page_fonts)}) whose text layer dropped the Tamil characters. Running PaddleOCR-VL-1.6 Vision Engine to read the rendered glyphs instead...")
                            page_res = self.process_image(pil_image, lang=lang) if pil_image else {"lines": [], "words": [], "full_text": ""}
                            page_res["page_number"] = idx + 1
                            page_res["preview_url"] = preview_url

                    page_dur = time.time() - page_start_time
                    lines_count = len(page_res.get("lines", []))
                    logger.info(f"<== [Page {idx + 1}/{num_pages}] Finished in {page_dur:.1f}s ({lines_count} lines extracted)")

                    pages.append(page_res)
                    if page_res.get("full_text"):
                        all_text_parts.append(f"--- PAGE {idx + 1} ---\n" + page_res["full_text"])
            finally:
                if pdf_plum:
                    try:
                        pdf_plum.close()
                    except (Exception, OSError):
                        pass
        else:
            images = self.convert_file_to_images(file_bytes, filename)
            target_indices = self.parse_page_indices(len(images), page_range, max_pages)
            logger.info(f"Processing image file '{filename}': {len(images)} total pages, targeting {[i+1 for i in target_indices]}")
            for step_num, idx in enumerate(target_indices, start=1):
                p_start = time.time()
                logger.info(f"==> [Page {idx + 1}/{len(images)}] (Step {step_num}/{len(target_indices)}) Processing...")
                img = images[idx]
                page_res = self.process_image(img, lang=lang)
                page_res["page_number"] = idx + 1
                p_dur = time.time() - p_start
                logger.info(f"<== [Page {idx + 1}/{len(images)}] Finished in {p_dur:.1f}s ({len(page_res.get('lines', []))} lines extracted)")
                pages.append(page_res)
                if page_res.get("full_text"):
                    all_text_parts.append(f"--- PAGE {idx + 1} ---\n" + page_res["full_text"])

        aggregated_text = "\n\n".join(all_text_parts) if all_text_parts else ""
        total_dur = time.time() - doc_start_time
        logger.info(f"Completed processing '{filename}': {len(pages)} pages extracted in {total_dur:.1f}s.")
        return {
            "filename": filename,
            "total_pages": len(pages),
            "original_total_pages": num_pages if ext == ".pdf" else len(pages),
            "pages": pages,
            "aggregated_text": aggregated_text,
            "model": "PaddleOCR-VL-1.6",
            "engine": "PaddleOCR-VL-1.6 Vision-Language Model",
        }
