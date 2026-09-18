import pdfplumber
import json

def inspect_pdf(path, name):
    print(f"=== {name} ===")
    with pdfplumber.open(path) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            txt = page.extract_text()
            print(f"--- Page {i+1} ---")
            print(txt if txt else "[No text]")

if __name__ == "__main__":
    inspect_pdf(r"C:\Users\nares\.gemini\antigravity-ide\brain\3e9977d8-8e3e-4809-8f0a-b5f029072d75\.user_uploaded\media_1789735016637.pdf", "MEDIA 1 (Patta Ref)")
    print("\n" + "="*80 + "\n")
    inspect_pdf(r"C:\Users\nares\.gemini\antigravity-ide\brain\3e9977d8-8e3e-4809-8f0a-b5f029072d75\.user_uploaded\media_1789735146836.pdf", "MEDIA 2 (TSLR Ref)")
