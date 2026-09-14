import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["FLAGS_use_mkldnn"] = "0"
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pypdfium2 as pdfium
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

def main():
    print("Loading OCR...", flush=True)
    ocr = PaddleOCR(
        lang="ta",
        device="cpu",
        enable_mkldnn=False,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    pdf2_path = r'C:\Users\nares\Downloads\EC -3- 01.01.1975 to 24.06.2024.pdf'
    doc = pdfium.PdfDocument(pdf2_path)

    page = doc[0]
    bitmap = page.render(scale=1.5)
    pil_img = bitmap.to_pil()
    np_img = np.array(pil_img)
    print("Running predict on page 1...", np_img.shape, flush=True)
    res = ocr.predict(np_img)
    print("=== Page 1 Result ===", flush=True)
    for r in res:
        texts = r.get("rec_texts", [])
        print(f"Detected {len(texts)} lines:", flush=True)
        for t in texts:
            print("  ", t, flush=True)

if __name__ == "__main__":
    main()
