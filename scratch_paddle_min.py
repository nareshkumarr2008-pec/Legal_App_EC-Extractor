import numpy as np
from paddleocr import PaddleOCR

print("1. Loading PaddleOCR...")
ocr = PaddleOCR(lang='ta', use_angle_cls=False)
print("2. Loaded. Creating dummy image...")
img = np.ones((100, 300, 3), dtype=np.uint8) * 255
print("3. Calling predict...")
res = ocr.predict(img)
print("4. Result:", res)
