import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["FLAGS_use_mkldnn"] = "0"
import sys, time
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

print("1. Initializing PaddleOCR with enable_mkldnn=False...", flush=True)
ocr = PaddleOCR(
    lang="ta",
    device="cpu",
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
print("2. PaddleOCR ready. Opening image crop...", flush=True)
img = Image.open('scratch_pdf2_page1.png')
crop = np.array(img.crop((100, 100, 500, 300)))
print("3. Crop shape:", crop.shape, flush=True)

t0 = time.time()
res = ocr.predict(crop)
print(f"4. Predict finished in {time.time()-t0:.2f}s", flush=True)
print("Result:", res, flush=True)
