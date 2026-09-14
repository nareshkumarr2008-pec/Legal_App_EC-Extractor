import sys
import time
from PIL import Image
from app.ocr_engine import OCREngine

sys.stdout.reconfigure(encoding='utf-8')
img = Image.open('scratch_pdf2_page1.png')
engine = OCREngine()
print('Paddle available:', engine.paddle_available, flush=True)
print('Device:', engine.device, flush=True)

t0 = time.time()
res = engine.process_image(img, lang='ta')
print(f"Done in {time.time()-t0:.2f}s, lines: {len(res.get('lines', []))}", flush=True)
for l in res.get('lines', [])[:15]:
    print('  LINE:', l.get('text'))
