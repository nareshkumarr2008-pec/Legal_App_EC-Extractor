# -*- coding: utf-8 -*-
"""
PDF Report Generator for Real Estate Document OCR & Intelligence.
Produces clean, professional, publication-ready PDF reports with Tamil font support.
Specialized EC Extracted Report matching the authoritative TNREGINET standard (10-column precision grid).
"""

import io
import os
import re
import atexit
import tempfile
import unicodedata
import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Pillow is used for one job only: shaping Tamil text runs into correctly
# formed glyph images (see _tamil_run_to_img_tag below). This requires
# Pillow's "raqm" text layout engine (HarfBuzz + FriBidi under the hood) --
# bundled in all official Pillow wheels since Pillow 8.3, so no extra
# system packages are needed on top of the existing `pillow` requirement.
from PIL import Image as _PILImage, ImageDraw as _PILImageDraw, ImageFont as _PILImageFont


_ASSETS_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")

# Cache so we only hit the filesystem / register with reportlab once per process.
_REGISTERED_FONTS_CACHE = None


def _get_registered_fonts():
    """
    Register and return a (regular, bold) font-name pair capable of rendering
    both Tamil and Latin script in the same PDF.

    Priority order:
      1. A Tamil-capable font bundled with this repo (app/assets/fonts) --
         works identically on every platform (Linux servers, CI, Windows, Mac),
         which is what makes the Tamil / Bilingual PDF modes actually work in
         production instead of only on a Windows dev machine.
      2. Native Windows Tamil fonts (Latha / Vijaya), if present -- kept as an
         optional override for anyone who prefers the OS-installed look.
      3. Helvetica -- last resort. Tamil glyphs will not render with this font;
         callers must not request lang='ta'/'both' text through it.
    """
    global _REGISTERED_FONTS_CACHE
    if _REGISTERED_FONTS_CACHE is not None:
        return _REGISTERED_FONTS_CACHE

    font_name = 'Helvetica'
    font_bold = 'Helvetica-Bold'

    font_candidates = [
        (
            os.path.join(_ASSETS_FONT_DIR, "NotoSansTamil-Regular.ttf"),
            os.path.join(_ASSETS_FONT_DIR, "NotoSansTamil-Bold.ttf"),
            "NotoSansTamil", "NotoSansTamil-Bold",
        ),
        # OS-installed Tamil fonts are kept only as a fallback for the rare
        # case the bundled font fails to load -- they must never be tried
        # first, since every Tamil run in the document is rasterized with
        # the *bundled* NotoSansTamil font regardless of what's chosen here
        # (see _pil_tamil_font, which hardcodes that path). If Latha/Vijaya
        # won this race instead, this font is still used for every plain
        # Latin/English character in the report, while Tamil keeps coming
        # out in NotoSansTamil -- so English and Tamil visibly mismatch in
        # weight/x-height/style wherever they sit on the same line (e.g.
        # "Adyar (" in Latha next to an "அடையாறு" image in NotoSansTamil).
        # Trying the bundled font first keeps Latin and Tamil visually
        # consistent everywhere, and also removes the platform dependency
        # the docstring above already promises (Windows-only paths would
        # silently fall through to Helvetica -- no Tamil at all -- on
        # Linux/Mac/CI anyway).
        (r"C:\Windows\Fonts\latha.ttf", r"C:\Windows\Fonts\lathab.ttf", "Latha", "Latha-Bold"),
        (r"C:\Windows\Fonts\vijaya.ttf", r"C:\Windows\Fonts\vijayab.ttf", "Vijaya", "Vijaya-Bold"),
    ]

    for reg_path, bold_path, f_reg, f_bld in font_candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont(f_reg, reg_path))
                font_name = f_reg
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(f_bld, bold_path))
                    font_bold = f_bld
                else:
                    font_bold = f_reg
                break
            except Exception:
                continue

    _REGISTERED_FONTS_CACHE = (font_name, font_bold)
    return _REGISTERED_FONTS_CACHE


def _tamil_font_available() -> bool:
    """True if the registered regular font can actually render Tamil glyphs
    (i.e. we didn't fall all the way back to Helvetica)."""
    font_name, _ = _get_registered_fonts()
    return font_name != 'Helvetica'


class _NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for exact total page numbering and running headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        font_name, _ = _get_registered_fonts()
        self.setFont(font_name, 8)
        self.setFillColor(colors.HexColor('#64748b'))
        
        # Header line & label
        self.setStrokeColor(colors.HexColor('#e2e8f0'))
        self.setLineWidth(0.5)
        self.line(36, 805, 559, 805)
        self.drawString(36, 810, "PlotChoice Legal OCR & Document Intelligence Report")
        self.drawRightString(559, 810, datetime.datetime.now().strftime("%d-%b-%Y %I:%M %p"))

        # Footer line & label
        self.line(36, 45, 559, 45)
        self.drawString(36, 32, "Confidential • Automatically Extracted via GPU OCR & Document Intelligence Engine")
        self.drawRightString(559, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


class _ECNumberedCanvas(canvas.Canvas):
    """Clean landscape canvas for publication-style EC Extracted Reports."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#64748b'))
        if self._pageNumber > 1:
            self.drawRightString(805, 18, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


from app.translator import transliterate_tamil_text

_TAMIL_RANGE = range(0x0B80, 0x0C00)


def _has_tamil(s: str) -> bool:
    return any(ord(c) in _TAMIL_RANGE for c in s)


# ---------------------------------------------------------------------------
# Tamil rendering: shape-then-rasterize, instead of guessing glyph order.
#
# ReportLab's canvas/Paragraph text drawing does not do complex-script
# shaping at all -- it just draws each Unicode codepoint's glyph in the
# exact order the string gives it, left to right, using each glyph's
# default (unligated, isolated-form) advance width. Tamil relies on an
# OpenType shaping engine (HarfBuzz, used by every browser via Pango/
# CoreText/DirectWrite) to reorder pre-base vowel signs, form conjuncts,
# and tighten the spacing between a consonant, a virama, and the next
# consonant. Without that shaping step, correct, perfectly ordinary Unicode
# Tamil like "சார்பதிவாளர்" comes out looking like "சா ர்பதி வா ளர்" --
# not because the underlying text is wrong, but because each glyph is
# drawn on its own with its unshaped side-bearing, which reads as stray
# gaps in the middle of the word.
#
# An earlier version of this module tried to patch this by manually
# re-ordering pre-base vowel signs before drawing. That only fixes one of
# several shaping rules Tamil needs and does not address the spacing
# problem at all, so it has been replaced with the approach below: shape
# the Tamil run exactly the way a browser would (via Pillow's "raqm"
# layout engine, which wraps the same HarfBuzz + FriBidi libraries), and
# embed the shaped result as a small inline image using ReportLab's
# built-in Paragraph <img> tag. This is also what keeps the PDF's Tamil
# text and font identical to the website's own table -- both start from
# the same untouched Unicode string and the same bundled NotoSansTamil
# font, so nothing about the spelling or shaping can drift between them.
_TAMIL_RUN_RE = re.compile(r'([\u0B80-\u0BFF]+)')

_pil_tamil_font_cache: Dict[Any, Any] = {}

# Every shaped-Tamil PNG is a real temp file on disk (ReportLab's <img> tag
# requires a path/file it can re-open while laying out and while writing
# the final PDF, not in-memory bytes). They're tracked here and deleted
# once the process exits; each is a few KB, and _cleanup_tamil_tmp_images()
# is also called explicitly at the end of every PDF-generating function
# below so they don't pile up on a long-running server.
_tamil_tmp_images: List[str] = []


def _cleanup_tamil_tmp_images() -> None:
    while _tamil_tmp_images:
        path = _tamil_tmp_images.pop()
        try:
            os.remove(path)
        except OSError:
            pass


atexit.register(_cleanup_tamil_tmp_images)


try:
    import uharfbuzz as _hb
    import freetype as _ft
    _UHARFBUZZ_AVAILABLE = True
except ImportError:
    _UHARFBUZZ_AVAILABLE = False
    _hb = None
    _ft = None

_hb_face_cache: Dict[str, Any] = {}


def _render_tamil_run_harfbuzz(run: str, font_path: str, size_px: int, text_color: tuple = (15, 23, 42)):
    """
    Renders complex Tamil script with full HarfBuzz OpenType shaping and FreeType rasterization.
    Produces perfectly formed ligatures (சு, னு, று, க், etc.) and correctly positioned vowel signs.
    """
    if font_path not in _hb_face_cache:
        with open(font_path, 'rb') as f:
            data = f.read()
        _hb_face_cache[font_path] = _hb.Face(data)
    
    hb_face = _hb_face_cache[font_path]
    face = _ft.Face(font_path)
    face.set_pixel_sizes(0, size_px)
    
    hb_font = _hb.Font(hb_face)
    hb_font.scale = (face.size.x_ppem * 64, face.size.y_ppem * 64)
    
    buf = _hb.Buffer()
    buf.add_str(run)
    buf.guess_segment_properties()
    _hb.shape(hb_font, buf)
    
    ascent = face.size.ascender >> 6
    descent = face.size.descender >> 6
    line_height = ascent - descent
    
    total_width_64 = sum(pos.x_advance for pos in buf.glyph_positions)
    total_width = (total_width_64 >> 6) + 6
    
    img = _PILImage.new('RGBA', (max(total_width, 1), max(line_height + 6, 1)), (0, 0, 0, 0))
    
    pen_x = 2
    pen_y = ascent + 3
    
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        face.load_glyph(info.codepoint, _ft.FT_LOAD_RENDER)
        bm = face.glyph.bitmap
        x = pen_x + (pos.x_offset >> 6) + face.glyph.bitmap_left
        y = pen_y - (pos.y_offset >> 6) - face.glyph.bitmap_top
        if bm.width > 0 and bm.rows > 0:
            glyph_img = _PILImage.frombytes('L', (bm.width, bm.rows), bytes(bm.buffer))
            rgba = _PILImage.new('RGBA', (bm.width, bm.rows), text_color + (0,))
            rgba.putalpha(glyph_img)
            img.alpha_composite(rgba, (x, y))
        pen_x += (pos.x_advance >> 6)
        pen_y += (pos.y_advance >> 6)
        
    bbox = img.getbbox()
    if bbox:
        pad = 1
        crop_box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(img.width, bbox[2] + pad), min(img.height, bbox[3] + pad))
        cropped = img.crop(crop_box)
        baseline_px = pen_y - crop_box[1]
        valign_offset = -(cropped.height - baseline_px)
        return cropped, valign_offset
    return img, 0


def _pil_tamil_font(size_px: int, bold: bool = False):
    """Load (and cache) the bundled Tamil TTF at a given pixel size."""
    key = (size_px, bold)
    cached = _pil_tamil_font_cache.get(key)
    if cached is not None:
        return cached
    fname = "NotoSansTamil-Bold.ttf" if bold else "NotoSansTamil-Regular.ttf"
    path = os.path.join(_ASSETS_FONT_DIR, fname)
    try:
        font = _PILImageFont.truetype(path, size_px, layout_engine=_PILImageFont.Layout.RAQM)
    except Exception:
        font = _PILImageFont.truetype(path, size_px)
    _pil_tamil_font_cache[key] = font
    return font


def _tamil_run_to_img_tag(run: str, font_size_pt: float, bold: bool = False) -> str:
    """
    Shape one run of Tamil-script characters with HarfBuzz (uharfbuzz + freetype)
    and return a ReportLab Paragraph <img .../> tag that embeds the result inline
    with the surrounding text, sized and baseline-aligned to match a
    `font_size_pt`-sized line of ordinary text.
    """
    if not run:
        return ""
    render_px = max(28, int(round(font_size_pt * 4)))  # render big, downscale for crisp edges
    fname = "NotoSansTamil-Bold.ttf" if bold else "NotoSansTamil-Regular.ttf"
    font_path = os.path.join(_ASSETS_FONT_DIR, fname)
    if not os.path.exists(font_path):
        font_path = os.path.join(_ASSETS_FONT_DIR, "NotoSansTamil-Regular.ttf")

    if _UHARFBUZZ_AVAILABLE and os.path.exists(font_path):
        try:
            img, valign_offset = _render_tamil_run_harfbuzz(run, font_path, render_px)
            tmp = tempfile.NamedTemporaryFile(prefix="tamil_", suffix=".png", delete=False)
            img.save(tmp.name)
            tmp.close()
            _tamil_tmp_images.append(tmp.name)

            scale = font_size_pt / render_px
            w_pt, h_pt = img.width * scale, img.height * scale
            valign_pt = max(-1.8, valign_offset * scale)
            return (f'<img src="{tmp.name}" width="{w_pt:.2f}" height="{h_pt:.2f}" '
                    f'valign="{valign_pt:.2f}"/>')
        except Exception:
            pass

    # Fallback to PIL basic rendering
    font = _pil_tamil_font(render_px, bold=bold)
    probe = _PILImageDraw.Draw(_PILImage.new("RGBA", (1, 1)))
    bbox = probe.textbbox((0, 0), run, font=font)
    if bbox is None:
        return ""
    x0, y0, x1, y1 = bbox
    pad = 2
    w_px = max(1, x1 - x0) + pad * 2
    h_px = max(1, y1 - y0) + pad * 2
    img = _PILImage.new("RGBA", (w_px, h_px), (0, 0, 0, 0))
    draw = _PILImageDraw.Draw(img)
    draw.text((pad - x0, pad - y0), run, font=font, fill=(15, 23, 42, 255))

    tmp = tempfile.NamedTemporaryFile(prefix="tamil_", suffix=".png", delete=False)
    img.save(tmp.name)
    tmp.close()
    _tamil_tmp_images.append(tmp.name)

    scale = font_size_pt / render_px
    w_pt, h_pt = w_px * scale, h_px * scale
    ascent, _descent = font.getmetrics()
    baseline_px = ascent + pad - y0
    valign_pt = max(-1.8, -(h_px - baseline_px) * scale)
    return (f'<img src="{tmp.name}" width="{w_pt:.2f}" height="{h_pt:.2f}" '
            f'valign="{valign_pt:.2f}"/>')


def _xml_escape_for_paragraph(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _tamilify_for_paragraph(s: str, font_size_pt: float = 7.5, bold: bool = False) -> str:
    """
    Take a sanitized field string and prepare it for ReportLab Paragraph:
    Shapes every run of Tamil script with HarfBuzz (uharfbuzz + freetype) so that
    complex conjuncts, pre-base vowels (ெ, ே, ை), and ligatures render with 100%
    typographic accuracy.
    """
    if not s or not _has_tamil(s):
        return _xml_escape_for_paragraph(s or "")
    parts = _TAMIL_RUN_RE.split(s)
    out = []
    for part in parts:
        if not part:
            continue
        if _has_tamil(part):
            out.append(_tamil_run_to_img_tag(part, font_size_pt, bold=bold))
        else:
            out.append(_xml_escape_for_paragraph(part))
    return "".join(out)


def _sanitize_text_for_pdf(text: Any, default: str = "-", lang: str = "en") -> str:
    """
    Sanitize a raw extracted field into clean, print-ready text for the PDF.

    `lang` controls what script the field ends up in:
      - "en"   (default): transliterate any Tamil to English. Legacy behaviour,
        used for the plain English report.
      - "ta": keep the original Tamil script untouched (no transliteration).
        Requires a Tamil-capable font to be in use for this to render (see
        _tamil_font_available / _get_registered_fonts).
      - "both": bilingual -- "English (Tamil)" when the source contains Tamil
        and a transliteration is available and actually differs from it,
        otherwise the original value is kept as-is.
    """
    if text is None:
        return default
    s = str(text).strip()
    if not s or s == "" or s.lower() in ["none", "null"]:
        return default
    if s == "-":
        return "-"

    has_tamil = _has_tamil(s)
    already_bilingual = False

    if has_tamil:
        # Some upstream fields (village / taluk / district / owner names run
        # through format_bilingual_entity, or LLM fields already stored as
        # "English (Tamil)") arrive here *already* bilingual. Detect that
        # shape up front -- otherwise "both" mode would wrap the whole
        # "English (Tamil)" string a second time into
        # "English (Tamil) (English (Tamil))".
        # IMPORTANT: this must only match a simple, single "Name (Name)" pair
        # (e.g. "Chennai (சென்னை)"), not a full sentence that merely happens
        # to contain parentheses elsewhere (e.g. "Registered Lease(s)
        # recorded: Doc 2309/2007 (18-Dec-2007) to ... (Lessor)"). The old
        # `.*` version matched greedily from the FIRST "(" to the LAST ")" in
        # the whole string, so a sentence like that got sliced in half --
        # everything from "(s) recorded: ..." onward was mistaken for "the
        # Tamil side" and the English lead-in before it was silently dropped.
        # Requiring no other "(" / ")" anywhere in the string restricts the
        # match to genuine short bilingual entity pairs.
        _m = re.match(r'^([^()]*?)\s*\(([^()]*)\)\s*$', s)
        if _m:
            _a, _b = _m.group(1).strip(), _m.group(2).strip()
            if _a and _has_tamil(_a) != _has_tamil(_b):  # exactly one side is Tamil
                already_bilingual = True
                if lang in ("en", "ta"):
                    s = _pick_lang_variant(s, lang)
                    has_tamil = _has_tamil(s)
                # lang == "both": leave s untouched, it's already in shape.

        if lang == "ta":
            pass  # keep native Tamil script as-is
        elif lang == "both":
            if not already_bilingual:
                # normalize=False: fields reaching this function have
                # already been through normalize_tamil_visual_order() once,
                # upstream in the extractors (see e.g. ec_extractor.py,
                # which does this at extraction time and -- for the same
                # reason -- already calls transliterate_tamil_text with
                # normalize=False itself). That transform is directional
                # and not idempotent, so re-running it here on
                # already-correct canonical-order text scrambles it before
                # transliteration ever sees it (e.g. "சென்னை" / Chennai
                # was coming out as "Sanenai").
                translit = transliterate_tamil_text(s, normalize=False)
                translit = translit.strip() if translit else ""
                if translit and translit.lower() != s.lower():
                    s = f"{translit} ({s})"
        else:  # "en"
            if not already_bilingual:
                s = transliterate_tamil_text(s, normalize=False)

    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2019': "'", '\u2018': "'", '`': "'", '\u00b4': "'",
        '\u2014': ' - ', '\u2013': ' - ', '\u2026': '...', '\u00a0': ' ',
        '\u2022': '*', '\u20b9': 'Rs. ', '\u2122': '', '\u00ae': '', '\u00a9': '(c)',
        '\u200b': '', '\u200c': '', '\u200d': '', '\ufeff': '',
        # Arrows used by extractors (e.g. "executants -> claimants" in the EC
        # verification-flags text) fall outside Latin-1 and the Tamil block,
        # so the character filter below used to silently delete them --
        # jamming two name lists together with no separator at all instead of
        # rendering as a plain-text arrow the way the website's HTML does.
        '\u2192': ' -> ', '\u2190': ' <- ', '\u2194': ' <-> ', '\u21d2': ' => ',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # Keep Latin-1 printable characters, plus the Tamil block when this field
    # is meant to still carry Tamil script (ta / both modes).
    if lang in ("ta", "both"):
        s = "".join(ch for ch in s if ord(ch) <= 255 or ord(ch) in _TAMIL_RANGE)
    else:
        s = "".join(ch for ch in s if ord(ch) <= 255)

    # Clean up empty parens
    s = re.sub(r'\(\s*\)', '', s)
    s = re.sub(r'\(\s*[.,;:\-]+\s*\)', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s if s else default

    # Note: unlike an earlier version of this function, nothing further
    # happens to Tamil text here -- it is left in plain, correct, logical-
    # order Unicode (identical to what the website sends to the browser).
    # Shaping now happens later, right before the text reaches a Paragraph,
    # via _tamilify_for_paragraph / _tamil_run_to_img_tag above, which is
    # the only place that needs to (and can correctly) turn it into glyphs.
    return s


def _sanitize_bilingual_cell(text: str) -> str:
    """
    Light sanitizer for a table cell that has ALREADY been assembled into a
    correct "English Name (Tamil Name)" bilingual string (see
    _format_bilingual_party_list below). Only does safe cosmetic cleanup --
    smart quotes, stray zero-width characters, whitespace collapsing.

    Deliberately does NOT call transliterate_tamil_text()/_sanitize_text_for_pdf()
    the way plain single-value fields do: those treat any Tamil they see as
    raw, untranslated OCR text and run it through the phonetic fallback
    transliterator, which would take the already-correct Tamil half of a
    verified bilingual pair and re-mangle it (this was the root cause of
    names like "Sushila Goklaney" turning into "Sushilaa Koklaani").
    """
    if not text:
        return "-"
    s = str(text).strip()
    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2019': "'", '\u2018': "'", '`': "'", '\u00b4': "'",
        '\u2014': ' - ', '\u2013': ' - ', '\u2026': '...', '\u00a0': ' ',
        '\u200b': '', '\u200c': '', '\u200d': '', '\ufeff': '',
        '\u2192': ' -> ', '\u2190': ' <- ',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    # Keep ASCII printable characters, Latin-1 printable characters plus the Tamil Unicode block; drop
    # anything else (stray control chars / unsupported scripts).
    s = "".join(ch for ch in s if ord(ch) <= 255 or ord(ch) in _TAMIL_RANGE)
    # Normalize spaces around parens so labels don't get orphan parens: "Word (\n text )" -> "Word (text)"
    s = re.sub(r'\s*\(\s*', ' (', s)
    s = re.sub(r'\s*\)\s*', ') ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s or "-"


def _format_bilingual_party_list(bilingual: Any, raw_fallback: Any = None) -> str:
    """
    Renders a list of translate_and_verify()-shaped records (see
    app.deep_translate_verifier.bilingual_party_list) as:
        "English Name (Tamil Name) (Role); English Name (Tamil Name) (Role); ..."
    -- the same "English (Tamil)" convention used everywhere else in this
    report. Each record's `english`/`tamil` values are already the verified,
    correctly-paired names (parsed straight from a "Name (Name)" pair in the
    source OCR text where one was present), so no further translation is
    applied here. Falls back to the raw OCR party string if no bilingual
    records are available (e.g. this extractor didn't produce them).
    """
    if not bilingual or not isinstance(bilingual, list):
        return str(raw_fallback).strip() if raw_fallback else "-"

    pieces: List[str] = []
    for rec in bilingual:
        if not isinstance(rec, dict):
            continue
        eng = (rec.get("english") or rec.get("original") or "").strip()
        tam = (rec.get("tamil") or "").strip()
        if eng and tam and eng.lower() != tam.lower():
            piece = f"{eng} ({tam})"
        else:
            piece = eng or tam
        role = rec.get("role_english")
        if role and piece:
            piece = f"{piece} ({role})"
        if piece:
            pieces.append(piece)

    if pieces:
        return "; ".join(pieces)
    return str(raw_fallback).strip() if raw_fallback else "-"


_NATURE_MAP = {
    "உரிமை ஆவணங்களின் ஒப்படைப்பு ஆவணம்": "Deposit of Title Deeds",
    "உரிமை ஆவணங்களின் ஒப்படைப்பு": "Deposit of Title Deeds",
    "உரிமை ஆவணங்கள் ஒப்படைப்பு ஆவணம்": "Deposit of Title Deeds",
    "உரிமை மாற்றம்": "Transfer of Rights",
    "ஈடு / அடைமானம்": "Mortgage",
    "ஈடு": "Mortgage",
    "அடைமானம்": "Mortgage",
    "இரசீது ஆவணம்": "Receipt Deed",
    "இரசீது": "Receipt",
    "கிரையப் பத்திரம்": "Sale Deed",
    "கிரையம்": "Sale",
    "தான செட்டில்மெண்ட்": "Gift Settlement",
    "செட்டில்மெண்ட்": "Settlement",
    "பாகப்பிரிவினை": "Partition",
    "விடுதலை": "Release",
    "பொது அதிகார ஆவணம்": "General Power of Attorney",
    "அதிகார ஆவணம்": "Power of Attorney",
    "குத்தகை": "Lease",
}


def _format_bilingual_nature(nature: Any, lang: str = "both") -> str:
    if not nature:
        return "-"
    s = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(nature))).strip()
    if not s or s == "-":
        return "-"
    if "(" in s and ")" in s and _has_tamil(s):
        return s

    eng = None
    # 1. Exact match
    for k, v in _NATURE_MAP.items():
        if unicodedata.normalize('NFC', k) == s:
            eng = v
            break

    # 2. Key phrase match
    if not eng:
        if "ஒப்படைப்பு" in s:
            eng = "Deposit of Title Deeds"
        elif "அடைமானம்" in s or "ஈடு" in s:
            eng = "Mortgage"
        elif "இரசீது" in s:
            eng = "Receipt Deed" if "ஆவணம்" in s else "Receipt"
        elif "மாற்றம்" in s:
            eng = "Transfer of Rights"
        elif "கிரையம்" in s or "கிரைய" in s:
            eng = "Sale Deed"
        elif "செட்டில்மெண்ட்" in s or "செட்டில்மென்ட்" in s:
            eng = "Settlement Deed"
        elif "பாகப்பிரிவினை" in s:
            eng = "Partition Deed"
        elif "விடுதலை" in s:
            eng = "Release Deed"
        elif "அதிகார" in s:
            eng = "Power of Attorney"

    # 3. Substring match
    if not eng:
        for k, v in _NATURE_MAP.items():
            if unicodedata.normalize('NFC', k) in s:
                eng = v
                break

    if not eng and _has_tamil(s):
        eng = transliterate_tamil_text(s, normalize=False)

    if lang == "both":
        if eng and _has_tamil(s):
            return f"{eng} ({s})"
        return s or "-"
    elif lang == "ta":
        return s
    else:  # en
        return eng or s


def generate_ec_extracted_report_pdf(ec_data: dict, lang: str = "en") -> bytes:
    """
    Generate authoritative, publication-ready Encumbrance Certificate Extracted Report
    in Landscape A4 with full 10-column precision table matching authoritative TNREGINET standards.

    lang: "en" (English, default), "ta" (Tamil script, no transliteration),
          or "both" (bilingual "English (Tamil)" per field).
    """
    lang = (lang or "en").lower()
    if lang not in ("en", "ta", "both"):
        lang = "en"

    buffer = io.BytesIO()

    font_name, font_bold = _get_registered_fonts()
    if lang in ("ta", "both") and not _tamil_font_available():
        # No Tamil-capable font could be registered (bundled font missing from
        # this install) -- degrade gracefully to English rather than emitting
        # a PDF full of missing-glyph boxes.
        lang = "en"

    def S(text, default: str = "-", size: float = 7.5, bold: bool = False) -> str:
        # `size` should match the fontSize of whichever ParagraphStyle this
        # value is about to be placed into, so any Tamil in it is shaped
        # and rendered at the right physical size for that style (see
        # _tamilify_for_paragraph). 7.5 covers the large majority of body
        # text in this report (meta_val / callout_style / flag_body /
        # sec_sub_style are all 7.5pt); call sites that land in the
        # 6.8pt/6.0pt entries-table styles pass size explicitly.
        return _tamilify_for_paragraph(
            _sanitize_text_for_pdf(text, default, lang=lang), size, bold=bold
        )

    # Landscape A4 margins 28pt (width 841.89pt - 56pt = 785.89pt printable)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ECTitle',
        fontName=font_bold,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'ECSubtitle',
        fontName=font_name,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569'),
        spaceAfter=5
    )

    sec_header_style = ParagraphStyle(
        'ECSecHeader',
        fontName=font_bold,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=6,
        spaceAfter=4
    )

    sec_sub_style = ParagraphStyle(
        'ECSecSub',
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=5
    )

    meta_label = ParagraphStyle(
        'ECMetaLabel',
        fontName=font_bold,
        fontSize=7.5,
        leading=11.5,
        textColor=colors.HexColor('#0f172a')
    )

    meta_val = ParagraphStyle(
        'ECMetaVal',
        fontName=font_name,
        fontSize=7.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b')
    )

    callout_style = ParagraphStyle(
        'ECCallout',
        fontName=font_name,
        fontSize=7.5,
        leading=11.5,
        textColor=colors.HexColor('#991b1b')
    )

    flag_body = ParagraphStyle(
        'ECFlagBody',
        fontName=font_name,
        fontSize=7.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3
    )

    th_style = ParagraphStyle(
        'ECTableH',
        fontName=font_bold,
        fontSize=6.8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    td_style = ParagraphStyle(
        'ECTableD',
        fontName=font_name,
        fontSize=6.8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    td_bold = ParagraphStyle(
        'ECTableDBold',
        fontName=font_bold,
        fontSize=6.8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    td_note = ParagraphStyle(
        'ECTableDNote',
        fontName=font_name,
        fontSize=6.0,
        leading=9.0,
        textColor=colors.HexColor('#475569')
    )

    caveat_p = ParagraphStyle(
        'ECCaveatP',
        fontName=font_name,
        fontSize=7.5,
        leading=11,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5
    )

    footer_p = ParagraphStyle(
        'ECFooterP',
        fontName=font_name,
        fontSize=7.0,
        leading=9.5,
        textColor=colors.HexColor('#64748b'),
        spaceBefore=10
    )

    elements = []

    # ── PAGE 1: HEADER & SECTIONS 1 & 2 ──────────────────────────────────
    elements.append(Paragraph("Encumbrance Certificate — Extracted Report", title_style))
    elements.append(Paragraph("Government of Tamil Nadu, Registration Department (TNREGINET) — source document parsed field-by-field", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=6, spaceBefore=0))

    # Section 1: Property & Search Identification
    elements.append(Paragraph("1. Property & Search Identification", sec_header_style))

    # 4-column Table across 785pt
    col_w = [185, 207, 185, 208]
    prop_data = [
        [
            Paragraph("<b>Sub-Registrar Office (SRO)</b>", meta_label),
            Paragraph(S(ec_data.get("sro", "-")), meta_val),
            Paragraph("<b>Certificate Issue Date</b>", meta_label),
            Paragraph(S(ec_data.get("issue_date", "-")), meta_val),
        ],
        [
            Paragraph("<b>Village</b>", meta_label),
            Paragraph(S(ec_data.get("village", "-")), meta_val),
            Paragraph("<b>Survey Number(s) Searched</b>", meta_label),
            Paragraph(S(str(ec_data.get("survey_searched", "-"))), meta_val),
        ],
        [
            Paragraph("<b>Zone</b>", meta_label),
            Paragraph(S(ec_data.get("zone", "-")), meta_val),
            Paragraph("<b>District</b>", meta_label),
            Paragraph(S(ec_data.get("district", "-")), meta_val),
        ],
        [
            Paragraph("<b>Search Period Requested</b>", meta_label),
            Paragraph(S(ec_data.get("search_period", "-")), meta_val),
            Paragraph("<b>SRO Date Available Range</b>", meta_label),
            Paragraph(S(ec_data.get("sro_available_from", "-")), meta_val),
        ],
        [
            Paragraph("<b>Form Type</b>", meta_label),
            Paragraph(S(ec_data.get("form_type", "Form 15")), meta_val),
            Paragraph("<b>Total Entries Found</b>", meta_label),
            Paragraph(S(str(ec_data.get("total_entries", "0"))), meta_val),
        ],
    ]

    prop_table = Table(prop_data, colWidths=col_w)
    prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(prop_table)
    elements.append(Spacer(1, 4))

    # Search window advisory note
    search_period_str = S(ec_data.get("search_period", "-"))
    is_below_30 = ec_data.get("below_30yr_standard", True)
    if is_below_30:
        callout_data = [[
            Paragraph(f"<b>Search-window note:</b> Tamil Nadu title-verification practice generally recommends a minimum 30-year EC search window. This certificate's data-available range ({search_period_str}) is shorter than that standard, so ownership history before this window is not covered by this document and should be verified through a separate, earlier-period EC or parent title deeds.", callout_style)
        ]]
        callout_table = Table(callout_data, colWidths=[785])
        callout_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff1f2')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#fecdd3')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(callout_table)
        elements.append(Spacer(1, 6))

    # Section 2: Key Verification Flags
    elements.append(Paragraph("2. Key Verification Flags", sec_header_style))
    elements.append(Paragraph("<b>Live / unreleased mortgages (Deposit of Title Deeds) found in this window:</b>", flag_body))

    mortgage_flags = ec_data.get("mortgages_flags", [])
    if not mortgage_flags:
        mortgage_flags = ["No registered mortgage or charge instruments found in this search window."]

    for mf in mortgage_flags:
        san_mf = S(mf)
        if san_mf.startswith("[CLOSED]"):
            mf_html = san_mf.replace("[CLOSED]", "<font color='#059669'><b>[CLOSED]</b></font>")
        elif san_mf.startswith("[OPEN / UNRELEASED]"):
            mf_html = san_mf.replace("[OPEN / UNRELEASED]", "<font color='#dc2626'><b>[OPEN / UNRELEASED]</b></font>")
        else:
            mf_html = san_mf
        elements.append(Paragraph(mf_html, flag_body))

    elements.append(Spacer(1, 2))
    court_text = S(ec_data.get("court_attachments_text") or "No court attachments, decrees, or lis-pendens entries appear among the registered documents in this search window.")
    elements.append(Paragraph(court_text, flag_body))
    elements.append(Spacer(1, 2))
    lease_text = S(ec_data.get("lease_text") or "No active registered lease agreements recorded in this search window.")
    elements.append(Paragraph(lease_text, flag_body))
    elements.append(Spacer(1, 2))
    rect_text = S(ec_data.get("rectification_text") or "No rectification instruments present in this search window.")
    elements.append(Paragraph(rect_text, flag_body))

    sr_gaps_text = S(ec_data.get("sr_gaps_text") or "")
    if sr_gaps_text and "GAP DETECTED" in sr_gaps_text:
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(f"<font color='#dc2626'><b>[Source Certificate Anomaly]</b></font> {sr_gaps_text}", flag_body))

    # ── PAGES 2 & 3: REGISTERED ENTRIES TABLE (10 COLUMNS) ─────────────────
    elements.append(PageBreak())

    elements.append(Paragraph("3. Registered Entries (Form 15) — Full Detail Table", sec_header_style))
    elements.append(Paragraph(f"All {ec_data.get('total_entries', 0)} entries returned for the search period {S(ec_data.get('search_period', '-'))}, SRO {S(ec_data.get('sro', '-'))}, Village {S(ec_data.get('village', '-'))}, Survey {S(ec_data.get('survey_searched', '-'))}.", sec_sub_style))

    # 10 Columns total width: 786pt
    # [Sr(22), Doc(54), Date(58), Nature(85), Execs(125), Claims(115), Cons(72), Mkt(72), PR(53), Schedule(130)]
    t_widths = [22, 54, 58, 85, 125, 115, 72, 72, 53, 130]
    
    t_rows = [[
        Paragraph("<b>Sr.</b>", th_style),
        Paragraph("<b>Doc No/Year</b>", th_style),
        Paragraph("<b>Date</b>", th_style),
        Paragraph("<b>Nature</b>", th_style),
        Paragraph("<b>Executant(s)</b>", th_style),
        Paragraph("<b>Claimant(s)</b>", th_style),
        Paragraph("<b>Consideration Value</b>", th_style),
        Paragraph("<b>Market Value</b>", th_style),
        Paragraph("<b>PR Number</b>", th_style),
        Paragraph("<b>Remarks / Schedule</b>", th_style),
    ]]

    entries = ec_data.get("transactions", [])
    if entries:
        for idx, row in enumerate(entries):
            # 1. Sr
            sr_num = row.get("sr") or (idx + 1)
            
            # 2. Doc No
            doc_no_val = S(row.get("doc_no") or "-", size=6.8, bold=True)
            
            # 3. Date
            date_val = S(row.get("date") or "-", size=6.8).replace("\n", "<br/>")
            
            # 4. Nature & Note
            nature_val = S(row.get("nature") or "Conveyance", size=6.8).replace("\n", "<br/>")
            nature_cell = [Paragraph(nature_val, td_style)]
            note_str = S(row.get("nature_note") or "", size=6.0)
            if note_str and note_str != "-":
                nature_cell.append(Spacer(1, 1.5))
                nature_cell.append(Paragraph(f"<i>{note_str}</i>", td_note))

            # 5. Executants & 6. Claimants (Use verified bilingual structure to prevent overlapping text)
            execs_raw = _format_bilingual_party_list(row.get("executants_bilingual"), row.get("executants") or row.get("parties"))
            claims_raw = _format_bilingual_party_list(row.get("claimants_bilingual"), row.get("claimants"))
            execs_val = B(execs_raw, size=6.8)
            claims_val = B(claims_raw, size=6.8)
            
            # 7. Consideration Value (Architecture: 1-by-1 explicit mapping)
            raw_cons = row.get("consideration")
            if not raw_cons or str(raw_cons).strip() in ["-", "0", "None", "null", ""]:
                cons_norm = row.get("consideration_norm")
                if isinstance(cons_norm, dict) and cons_norm.get("amount_inr", 0) > 0:
                    raw_cons = cons_norm.get("formatted", "-")
                else:
                    raw_cons = "-"
            cons_val = S(raw_cons, size=6.8)

            # 8. Market Value (Architecture: 1-by-1 explicit mapping)
            raw_mkt = row.get("market_value")
            if not raw_mkt or str(raw_mkt).strip() in ["-", "0", "None", "null", ""]:
                mkt_norm = row.get("market_value_norm")
                if isinstance(mkt_norm, dict) and mkt_norm.get("amount_inr", 0) > 0:
                    raw_mkt = mkt_norm.get("formatted", "-")
                else:
                    raw_mkt = "-"
            mkt_val = S(raw_mkt, size=6.8)

            # 9. PR Number (Architecture: 1-by-1 explicit mapping with currency guard)
            raw_pr = str(row.get("pr_number") or "-").strip()
            if bool(re.search(r'Rs\.?|₹|\bINR\b', raw_pr, re.I)) or (bool(re.search(r'^\s*[\d,]+\s*$', raw_pr)) and '/' not in raw_pr):
                raw_pr = "-"
            pr_val = S(raw_pr, size=6.8)

            # 10. Remarks / Schedule Details
            sch_list = row.get("schedules", [])
            rem_str = row.get("remarks") or row.get("document_remarks") or ""
            sch_parts = []
            if rem_str and rem_str != "-":
                sch_parts.append(rem_str)
            if sch_list and isinstance(sch_list, list) and len(sch_list) > 0:
                s0 = sch_list[0]
                if s0.get("extent") and s0.get("extent") != "-": sch_parts.append(s0["extent"])
                if s0.get("survey_no") and s0.get("survey_no") != "-": sch_parts.append(f"Sy:{s0['survey_no']}")
                if s0.get("plot_no") and s0.get("plot_no") != "-": sch_parts.append(f"Plot:{s0['plot_no']}")
            sch_val = S(" | ".join(sch_parts) if sch_parts else "-", size=6.8)

            t_rows.append([
                Paragraph(str(sr_num), td_style),
                Paragraph(doc_no_val, td_bold),
                Paragraph(date_val, td_style),
                nature_cell,
                Paragraph(execs_val, td_style),
                Paragraph(claims_val, td_style),
                Paragraph(cons_val, td_style),
                Paragraph(mkt_val, td_style),
                Paragraph(pr_val, td_style),
                Paragraph(sch_val, td_style),
            ])

        entries_table = Table(t_rows, colWidths=t_widths, repeatRows=1)
        entries_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eef2f6')),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        elements.append(entries_table)
    else:
        elements.append(Paragraph("<b>Nil Encumbrance Certificate (Form 16)</b> — No registered transactions found in the search window.", flag_body))

    # ── PAGE 4: CAVEATS ──────────────────────────────────────────────────
    elements.append(PageBreak())

    elements.append(Paragraph("4. Caveats — What This EC Does NOT Cover", sec_header_style))
    elements.append(Spacer(1, 4))

    sro_name = S(ec_data.get("sro", "-"))
    caveats = [
        f"* <b>This certificate reflects only registered documents</b> presented at the {sro_name} SRO within the stated search window. It is not proof of current, unencumbered ownership on its own.",
        "* <b>Unregistered agreements</b> (e.g. unregistered sale agreements, unregistered leases below the registration threshold, informal family arrangements) will not appear here.",
        "* <b>Court orders / decrees not yet registered with the SRO</b> - including injunctions, attachments, or succession orders pending registration - are invisible to this search.",
        "* <b>Property tax dues, utility dues, or statutory charges</b> (e.g. municipal tax arrears) are not tracked by the Registration Department and require a separate check with the local body.",
        "* <b>Physical possession disputes or adverse possession claims</b> are not recorded in registration data and require a physical inspection and local enquiry.",
        f"* <b>The search window ({search_period_str}) does not cover the full recommended 30-year history</b>; earlier encumbrances, mortgages, or litigation before this period will not surface in this document.",
        "* <b>Entries dated after the end of this search window</b> are not included - a fresh EC should be pulled through the present date to confirm no later mortgages, sales, or attachments exist."
    ]

    for c in caveats:
        elements.append(Paragraph(c, caveat_p))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Source: Government of Tamil Nadu Registration Department, Certificate of Encumbrance on Property, SRO {sro_name}, issued {S(ec_data.get('issue_date', '-'))}.<br/>"
        "Extracted and structured for review purposes; refer to the original certificate for the authoritative record and digital signature validity.",
        footer_p
    ))

    doc.build(elements, canvasmaker=_ECNumberedCanvas)
    return buffer.getvalue()


def _pick_lang_variant(s: str, lang: str = "en") -> str:
    """
    Fields like "Chengalpattu (செங்கல்பட்டு)" already carry both an English
    and a Tamil name, wrapped as "primary (secondary)". Pick the right side
    for the requested report language, regardless of which side happens to
    hold the Tamil script:
      - "en":   the Latin-script side (legacy behaviour: text before the "(").
      - "ta":   the Tamil-script side, if one exists.
      - "both": the original string untouched (already bilingual).
    """
    s = str(s or "").strip()
    if not s:
        return s
    lang = (lang or "en").lower()
    if lang == "both":
        return s
    # Same tightened shape as _sanitize_text_for_pdf above: only a single,
    # unambiguous "Name (Name)" pair qualifies -- not any string that merely
    # contains parentheses somewhere inside a longer sentence.
    m = re.match(r'^([^()]*?)\s*\(([^()]*)\)\s*$', s)
    if not m or not m.group(1).strip():
        return s
    a, b = m.group(1).strip(), m.group(2).strip()
    a_has_ta, b_has_ta = _has_tamil(a), _has_tamil(b)
    if lang == "ta":
        if b_has_ta:
            return b
        if a_has_ta:
            return a
        return s  # no Tamil side available -- best effort, keep as-is
    # lang == "en"
    if a_has_ta and not b_has_ta:
        return b
    return a


def _prepare_ec_report_data(data: dict, fields: dict, ext: dict, lang: str = "en") -> dict:
    """Helper to extract and format EC fields for the report generator."""
    def _val(k, default=""):
        f = fields.get(k)
        if isinstance(f, dict):
            return str(f.get("raw_value") or f.get("value") or default).strip()
        elif f is not None:
            return str(f).strip()
        return default

    def _en_only(s):
        return _pick_lang_variant(s, lang)

    sro = _en_only(_val("sro_office", "-"))
    issue_date = _val("certificate_date", "-")
    village = _en_only(_val("village", "-"))
    survey_searched = _val("survey_searched", "-")
    zone = _en_only(_val("zone", "-"))
    district = _en_only(_val("district", "-"))
    search_period = _val("search_period", "-")
    sro_available = _val("sro_available_from", search_period)
    
    form_type = _en_only(_val("form_type", "Form 15"))
    
    tx_list = fields.get("transactions_table", {}).get("value", [])
    if not isinstance(tx_list, list):
        tx_list = []
    total_entries = _val("total_entries", str(len(tx_list)))

    verif = ext.get("verification_flags") or fields.get("verification_flags") or {}
    mortgage_flags = verif.get("mortgages_flags") or []
    court_text = verif.get("court_attachments_text") or _val("court_attachments", f"No court attachments, decrees, or lis-pendens entries appear among the {total_entries} registered documents in this search window.")
    lease_text = verif.get("lease_text") or _val("lease_status", "No active registered lease agreements recorded in this search window.")
    rect_text = verif.get("rectification_text") or _val("rectification_deeds", "No rectification instruments present in this search window.")
    sr_gaps_text = verif.get("sr_gaps_text") or _val("sr_no_gaps", "")

    below_30yr = ext.get("below_30yr_standard") if "below_30yr_standard" in ext else fields.get("below_30yr_standard", True)
    search_years = ext.get("search_window_years") or fields.get("search_window_years", 0)

    return {
        "sro": sro,
        "issue_date": issue_date,
        "village": village,
        "survey_searched": survey_searched,
        "zone": zone,
        "district": district,
        "search_period": search_period,
        "sro_available_from": sro_available,
        "below_30yr_standard": below_30yr,
        "search_window_years": search_years,
        "form_type": form_type,
        "total_entries": total_entries,
        "mortgages_flags": mortgage_flags,
        "court_attachments_text": court_text,
        "lease_text": lease_text,
        "rectification_text": rect_text,
        "sr_gaps_text": sr_gaps_text,
        "transactions": tx_list
    }


def generate_ocr_pdf_report(data: Dict[str, Any], lang: str = "en") -> bytes:
    """
    Generate a full-fidelity PDF report of the OCR extraction results.
    If the document is an Encumbrance Certificate (EC), routes to the specialized 10-column landscape report.
    Returns bytes of the compiled PDF.

    lang: "en" (English, default), "ta" (Tamil script), or "both" (bilingual).
    Also accepted via data["lang"] / data["pdf_lang"] if not passed explicitly.
    """
    lang = (lang or data.get("lang") or data.get("pdf_lang") or "en").lower()
    if lang not in ("en", "ta", "both"):
        lang = "en"

    ext = data.get("extraction", {})
    fields = ext.get("fields", {}) or data.get("fields", {})
    doc_type = data.get("doc_type") or ext.get("document_type_id")

    # NOTE: Encumbrance Certificates used to be routed to the old
    # generate_ec_extracted_report_pdf() 10-column landscape grid via
    # _prepare_ec_report_data(). That path re-derives Executant/Claimant
    # text straight from the raw OCR party string using the crude
    # phonetic transliterate_tamil_text() fallback, discarding the
    # already-verified bilingual party data ECExtractor computes via
    # deep_translate_verifier.bilingual_party_list() (which preserves the
    # actual English name present in the source bilingual PDF instead of
    # reconstructing one from Tamil OCR text). That produced garbled names,
    # e.g. "Sushila Goklaney" -> "Sushilaa Koklaani". Every document type,
    # including EC, now renders through the single "Legal Document
    # Intelligence Report" layout below, which reads that verified
    # bilingual data directly instead of re-deriving it.
    buffer = io.BytesIO()
    font_name, font_bold = _get_registered_fonts()

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=10,
        spaceAfter=6
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#334155')
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#0f172a')
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    if lang in ("ta", "both") and not _tamil_font_available():
        lang = "en"

    def S(text, default: str = "-", size: float = 9, bold: bool = False) -> str:
        # 9pt matches meta_label_style / meta_val_style, which is where the
        # large majority of S(...) values in this report end up; the title
        # (16pt) is the one call site that needs a different size.
        return _tamilify_for_paragraph(
            _sanitize_text_for_pdf(text, default, lang=lang), size, bold=bold
        )

    def B(text, default: str = "-", size: float = 9, bold: bool = False) -> str:
        s = str(text).strip() if text is not None else ""
        if not s:
            s = default
        # Clean up stray linebreaks before opening parens in labels e.g. "SRO Office\n( சார்பதிவாளர்...)" -> "SRO Office (சார்பதிவாளர்...)"
        s = re.sub(r'\s*\n\s*\(\s*', ' (', s)
        s = re.sub(r'\s*\(\s*\n\s*', ' (', s)
        return _tamilify_for_paragraph(_sanitize_bilingual_cell(s), size, bold=bold)

    elements = []

    # Title & Metadata
    elements.append(Paragraph("Legal Document Intelligence Report", title_style))
    gen_ts = datetime.datetime.now().strftime('%b %d %Y, %H:%M')
    doc_type_disp = doc_type.upper() if doc_type else "-"
    elements.append(Paragraph(f"Generated: {gen_ts} | Document Type: {doc_type_disp}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=10))

    # Fields that are structural (rendered in their own sections below, or
    # internal bookkeeping) rather than simple key/value rows.
    _STRUCTURAL_FIELD_KEYS = {
        "transactions_table", "checklist", "verification_flags",
        "confidence_summary", "ec_report", "below_30yr_standard",
        "search_window_years", "owners_registry",
    }

    # 1. Extracted Key Legal Fields
    elements.append(Paragraph("1. Extracted Key Legal Fields", section_header_style))

    rows = [[
        Paragraph("<b>Key Field</b>", meta_label_style),
        Paragraph("<b>Extracted Value</b>", meta_label_style),
        Paragraph("<b>Confidence</b>", meta_label_style)
    ]]

    for k, v in fields.items():
        if k in _STRUCTURAL_FIELD_KEYS or isinstance(v, list):
            continue

        if isinstance(v, dict):
            label_str = v.get("label") or k.replace("_", " ").title()
            val_str = str(v.get("value") or v.get("raw_value") or "-")
            conf_raw = v.get("confidence", 0.95)
        else:
            label_str = k.replace("_", " ").title()
            val_str = str(v)
            conf_raw = 0.95

        conf_pct = round(conf_raw * 100) if isinstance(conf_raw, (int, float)) and conf_raw <= 1 else round(conf_raw)
        conf_str = f"{conf_pct}%"

        # Guard against exceptionally long field values (e.g. multi-property boundary schedules)
        # that exceed an entire page height and cause ReportLab LayoutError.
        if len(val_str) > 400:
            val_str = val_str[:400] + " ... (continued in detailed schedule / registry)"

        rows.append([
            Paragraph(B(label_str), meta_label_style),
            Paragraph(B(val_str), meta_val_style),
            Paragraph(conf_str, meta_val_style)
        ])

    table = Table(rows, colWidths=[185, 280, 58])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    # 2. Document Verification Checklist
    # ECExtractor (and other extractors) put this under fields["checklist"];
    # some older callers instead set it at the top level of the extraction
    # result -- check both so neither shape silently renders an empty section.
    checklist = fields.get("checklist") or ext.get("checklist") or []
    if checklist:
        elements.append(Paragraph("2. Document Verification Checklist", section_header_style))
        chk_rows = [[
            Paragraph("<b>Verification Item</b>", meta_label_style),
            Paragraph("<b>Status</b>", meta_label_style),
            Paragraph("<b>Details & Findings</b>", meta_label_style)
        ]]
        for item in checklist:
            if "is_valid" in item:
                passed = bool(item.get("is_valid"))
                status_word = "PASSED" if passed else "FLAGGED"
            else:
                raw_status = item.get("status", "REVIEW")
                passed = raw_status == "PASS"
                status_word = {"PASS": "PASSED", "FAIL": "FLAGGED"}.get(raw_status, raw_status)
            status_color = "#16a34a" if passed else "#dc2626"
            status_html = f"<font color='{status_color}'><b>{status_word}</b></font>"
            rule_name = item.get("title") or item.get("rule_name", "")
            remarks = item.get("details") or item.get("detail") or item.get("remarks", "")
            if len(remarks) > 400:
                remarks = remarks[:400] + "..."
            chk_rows.append([
                Paragraph(B(rule_name), meta_label_style),
                Paragraph(status_html, meta_val_style),
                Paragraph(B(remarks), meta_val_style)
            ])
        
        chk_table = Table(chk_rows, colWidths=[195, 60, 268])
        chk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        elements.append(chk_table)
        elements.append(Spacer(1, 14))

    # 3. Registered Transactions (EC party table) — uses the pre-verified
    # bilingual Executant/Claimant records (deep_translate_verifier) instead
    # of re-transliterating the raw OCR string, so names keep the actual
    # English spelling that was present in the source bilingual PDF.
    tx_field = fields.get("transactions_table") or {}
    tx_list = tx_field.get("value") if isinstance(tx_field, dict) else tx_field
    if isinstance(tx_list, list) and tx_list:
        elements.append(PageBreak())
        elements.append(Paragraph("3. Registered Transactions", section_header_style))

        tx_rows = [[
            Paragraph("<b>Sr.</b>", meta_label_style),
            Paragraph("<b>Doc No/Year</b>", meta_label_style),
            Paragraph("<b>Date</b>", meta_label_style),
            Paragraph("<b>Nature</b>", meta_label_style),
            Paragraph("<b>Executants</b>", meta_label_style),
            Paragraph("<b>Claimants</b>", meta_label_style),
        ]]

        tx_val_style = ParagraphStyle(
            'TxVal', parent=meta_val_style, fontSize=8, leading=12.5
        )

        for i, t in enumerate(tx_list, start=1):
            execs_str = _format_bilingual_party_list(
                t.get("executants_bilingual"), t.get("executants")
            )
            claims_str = _format_bilingual_party_list(
                t.get("claimants_bilingual"), t.get("claimants")
            )
            if len(execs_str) > 300:
                execs_str = execs_str[:300] + "..."
            if len(claims_str) > 300:
                claims_str = claims_str[:300] + "..."
            tx_rows.append([
                Paragraph(str(t.get("sr_no") or i), tx_val_style),
                Paragraph(B(t.get("doc_no_year") or t.get("doc_no") or "-", size=8), tx_val_style),
                Paragraph(B(t.get("date") or t.get("execution_date") or "-", size=8), tx_val_style),
                Paragraph(B(_format_bilingual_nature(t.get("nature"), lang=lang), size=8), tx_val_style),
                Paragraph(B(execs_str, size=8), tx_val_style),
                Paragraph(B(claims_str, size=8), tx_val_style),
            ])

        # Width sum: 22 + 60 + 60 + 95 + 143 + 143 = 523pt (Exact A4 printable area width: 595.27 - 72 = 523.27pt)
        tx_table = Table(tx_rows, colWidths=[22, 60, 60, 95, 143, 143], repeatRows=1)
        tx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        elements.append(tx_table)

    doc.build(elements, canvasmaker=_NumberedCanvas)
    return buffer.getvalue()
