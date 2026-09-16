import time, os
os.environ["OMP_NUM_THREADS"] = "8"
os.environ["CPU_NUM"] = "8"

import numpy as np
from app.ocr_engine import OCREngine

engine = OCREngine()
pipe = engine._get_pipeline_ta()

# Generate a synthetic test image with text
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
d = ImageDraw.Draw(img)
for y in range(50, 1500, 45):
    d.text((80, y), "This is a legal document line for sale deed verification test 123456", fill=(0, 0, 0))

img_np = np.array(img)

# Measure warm inference
t0 = time.time()
res = pipe.predict(img_np)
t1 = time.time()
print(f"Inference took: {t1 - t0:.2f} seconds!")
