"""Adaptive image preprocessing for the OCR step.

Instead of applying a fixed pipeline to every image, this module measures
the image's actual quality and applies only the corrections it needs.

Three possible corrections (can stack):
  CLAHE            — fixes dark or low-contrast images (operates in LAB
                     colour space so hues are not shifted)
  unsharp_mask     — recovers edge detail in blurry images
  bilateral_filter — reduces grain/noise while keeping text edges crisp

Output is a BGR numpy array, which EasyOCR accepts directly alongside
file paths.
"""
import cv2
import numpy as np


def _analyze(gray):
    """Return quality metrics for a grayscale image."""
    return {
        "brightness": float(np.mean(gray)),
        "contrast": float(np.std(gray)),
        "sharpness": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
    }


def adaptive_preprocess(image_path):
    """Load an image and apply targeted corrections based on its quality.

    Args:
        image_path: path to the input image file

    Returns:
        img    — corrected BGR numpy array ready for EasyOCR
        report — dict with brightness/contrast/sharpness metrics and
                 an 'applied' list of which corrections were used
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    metrics = _analyze(gray)
    applied = []

    # Dark or low-contrast image → CLAHE on the L channel.
    # Working in LAB space means only luminance is adjusted;
    # colour (A, B channels) stays untouched so text colours are preserved.
    if metrics["brightness"] < 80 or metrics["contrast"] < 40:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        applied.append("CLAHE")

    # Blurry image → unsharp mask (original weighted against its own blur).
    # Recovers fine detail like small text without introducing colour noise.
    if metrics["sharpness"] < 100:
        blurred = cv2.GaussianBlur(img, (0, 0), 3)
        img = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
        applied.append("unsharp_mask")

    # Noisy image: high contrast but low sharpness means variation comes from
    # grain, not actual edges. Bilateral filter smooths grain while keeping
    # the sharp boundaries that define text characters.
    if metrics["contrast"] > 60 and metrics["sharpness"] < 80:
        img = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        applied.append("bilateral_filter")

    return img, {**metrics, "applied": applied}
