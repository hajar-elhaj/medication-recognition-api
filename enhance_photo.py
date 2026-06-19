"""
CV Photo Enhancer
-----------------
Enhances a headshot photo for professional use:
- Brightens and sharpens the image
- Smooths skin tones slightly
- Lightens and cleans up the background
- Crops to a standard CV portrait ratio (3:4)
- Saves as high-quality JPEG

Usage:
    python enhance_photo.py input.jpg
    python enhance_photo.py input.jpg output.jpg   (optional custom output path)
"""

import sys
import cv2
import numpy as np
from pathlib import Path


def enhance_cv_photo(input_path: str, output_path: str | None = None) -> str:
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {input_path}")

    # ── Step 1: Upscale if small (ensures print quality at 35x45mm @ 300dpi) ──
    h, w = img.shape[:2]
    min_dim = 900
    if min(h, w) < min_dim:
        scale = min_dim / min(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)
        h, w = img.shape[:2]

    # ── Step 2: Brightness & contrast boost (subtle) ─────────────────────────
    # alpha=1.15 contrast, beta=8 brightness lift
    img = cv2.convertScaleAbs(img, alpha=1.15, beta=8)

    # ── Step 3: Sharpening ───────────────────────────────────────────────────
    kernel = np.array([[0, -0.5, 0],
                       [-0.5, 3, -0.5],
                       [0, -0.5, 0]])
    img = cv2.filter2D(img, -1, kernel)
    img = np.clip(img, 0, 255).astype(np.uint8)

    # ── Step 4: Lighten background ───────────────────────────────────────────
    # Convert to LAB for luminance-based background detection
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel = lab[:, :, 0]

    # GrabCut to separate foreground (person) from background
    mask = np.zeros((h, w), np.uint8)
    # Initialize foreground rectangle (leave 5% margin on each side)
    margin_x, margin_y = int(w * 0.05), int(h * 0.05)
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    fg_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)

    # Dilate slightly to avoid fringe artifacts
    fg_mask = cv2.dilate(fg_mask, np.ones((7, 7), np.uint8), iterations=2)
    fg_mask = cv2.GaussianBlur(fg_mask.astype(np.float32), (21, 21), 0)

    # Create a clean light grey background (lighter than the original)
    target_bg = np.full_like(img, 230)  # light grey, professional look

    fg_3 = np.stack([fg_mask, fg_mask, fg_mask], axis=-1)
    img = (img.astype(np.float32) * fg_3 + target_bg.astype(np.float32) * (1 - fg_3)).astype(np.uint8)

    # ── Step 5: Gentle skin smoothing (bilateral filter, preserves edges) ────
    img = cv2.bilateralFilter(img, d=9, sigmaColor=35, sigmaSpace=35)

    # ── Step 6: Crop to 3:4 portrait ratio (standard CV/passport format) ─────
    target_ratio = 3 / 4
    current_ratio = w / h
    if current_ratio > target_ratio:
        # Image is too wide — crop sides
        new_w = int(h * target_ratio)
        x_start = (w - new_w) // 2
        img = img[:, x_start:x_start + new_w]
    elif current_ratio < target_ratio:
        # Image is too tall — crop top/bottom (keep head centered, bias upward)
        new_h = int(w / target_ratio)
        y_start = max(0, (h - new_h) // 3)  # bias toward top (head)
        img = img[y_start:y_start + new_h, :]

    # ── Step 7: Resize to standard CV photo size (413×531 px @ 96dpi ≈ 3.5×4.5cm) ─
    img = cv2.resize(img, (413, 551), interpolation=cv2.INTER_LANCZOS4)

    # ── Step 8: Save ─────────────────────────────────────────────────────────
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.parent / (p.stem + "_cv_professional" + p.suffix))

    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 97])
    print(f"Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhance_photo.py <input_image> [output_image]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else None
    enhance_cv_photo(input_file, output_file)
