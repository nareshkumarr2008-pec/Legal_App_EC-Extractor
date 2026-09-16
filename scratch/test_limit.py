import time, os
import numpy as np
from PIL import Image, ImageDraw
from paddleocr import PaddleOCR

img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
d = ImageDraw.Draw(img)
for y in range(50, 1500, 50):
    d.text((80, y), "Legal document line for testing OCR speed 123456", fill=(0, 0, 0))
img_np = np.array(img)

print("Initializing PaddleOCR with text_det_limit_type='max', text_det_limit_side_len=960...")
p = PaddleOCR(
    lang='ta',
    device='cpu',
    enable_mkldnn=False,
    text_det_limit_type='max',
    text_det_limit_side_len=960,
    text_det_thresh=0.38,
    text_det_box_thresh=0.5,
    text_rec_score_thresh=0.5,
)

t0 = time.time()
res = p.predict(img_np)
t1 = time.time()
lines = res[0].get("rec_texts", [])
print(f"DONE in {t1 - t0:.2f}s! Extracted {len(lines)} lines.")
