import pdfplumber

pdf_path = "C:/Users/nares/Downloads/Sale Deed_3978_2010 - Naagesh.pdf"
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").strip()
        chars = len(page.chars)
        images = len(page.images)
        print(f"Page {i+1}: chars={chars}, text_len={len(text)}, images={images}, snippet={text[:60]!r}")
