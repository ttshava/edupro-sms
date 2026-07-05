import os

import numpy as np
from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))


def trim(name):
    path = os.path.join(DIR, name)
    img = Image.open(path).convert("L")  # grayscale
    arr = np.array(img)
    # Find rows containing meaningfully dark pixels (real text/borders),
    # not just "not pure white" (blank card interior is white too).
    dark_mask = arr < 180
    rows_with_ink = np.where(dark_mask.any(axis=1))[0]
    if len(rows_with_ink) == 0:
        print(f"no ink found for {name}")
        return
    bottom = min(arr.shape[0], rows_with_ink.max() + 40)
    img_rgb = Image.open(path).convert("RGB")
    cropped = img_rgb.crop((0, 0, img_rgb.width, bottom))
    cropped.save(path)
    print(f"{name}: {img_rgb.height} -> {cropped.height}")


for n in ["11_report_card_pdf.png", "12_fee_statement_pdf.png"]:
    trim(n)
