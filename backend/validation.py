"""Input validation gate for the recognition pipeline.

Before we trust the CNN + OCR result, we answer three questions about the
input image:

  1. Does it contain any readable text?          -> has_text()
  2. What language is that text (AR / FR / both)? -> detect_language()
  3. Is this plausibly a medicine box at all?     -> is_medicine()

Note on (3): the CNN only knows 5 classes and uses softmax, so on its own it
ALWAYS returns one of them, even for a photo of a cat ("brufen 60%"). True
out-of-distribution rejection would need retraining with a "not a medicine"
class. Instead we use a pragmatic heuristic: a real medicine box has text AND
the CNN is reasonably confident AND/OR the OCR text contains a known medicine
or pharmaceutical-form keyword.
"""
import re

# Arabic Unicode block U+0600–U+06FF; Latin letters for French/English.
_ARABIC = re.compile(r"[؀-ۿ]")
_LATIN = re.compile(r"[A-Za-z]")

# Pharmaceutical-form words that strongly indicate a medicine box (FR + AR).
_MED_KEYWORDS = [
    "comprime", "comprimé", "gelule", "gélule", "sachet", "sirop",
    "suspension", "inhalateur", "injectable", "ampoule", "effervescent",
    "pellicul", "mg", "ml", "posologie", "boite", "boîte",
    "قرص", "كبسولة", "كيس", "شراب", "حقن", "بخاخ", "فوار", "مغلف",
]

# CNN softmax above this is treated as "confident enough".
CONFIDENCE_THRESHOLD = 60.0


def has_text(ocr_text):
    """True if the OCR found any non-whitespace text."""
    return bool(ocr_text and ocr_text.strip())


def detect_language(ocr_text):
    """Return 'Arabic', 'French/Latin', 'Arabic + French/Latin', or 'Unknown'."""
    has_ar = bool(_ARABIC.search(ocr_text or ""))
    has_lat = bool(_LATIN.search(ocr_text or ""))
    if has_ar and has_lat:
        return "Arabic + French/Latin"
    if has_ar:
        return "Arabic"
    if has_lat:
        return "French/Latin"
    return "Unknown"


def is_medicine(ocr_text, confidence, known_names=None):
    """Heuristic check that the image is plausibly a medicine box.

    Returns (is_medicine: bool, reason: str).

    Signals, strongest first:
      - OCR text contains a known medicine name (from the DB)        -> yes
      - OCR text contains a pharmaceutical-form / dosage keyword     -> yes
      - No text at all                                               -> no
      - CNN confidence below threshold and no keywords               -> no
    """
    text = (ocr_text or "").lower()

    if not has_text(ocr_text):
        return False, "no text detected in the image"

    if known_names:
        for name in known_names:
            if name and name.lower() in text:
                return True, f"OCR text contains known medicine name '{name}'"

    for kw in _MED_KEYWORDS:
        if kw in text:
            return True, f"OCR text contains pharmaceutical keyword '{kw}'"

    if confidence < CONFIDENCE_THRESHOLD:
        return False, (
            f"low CNN confidence ({confidence:.1f}%) and no medical keywords found"
        )

    return True, f"CNN confident ({confidence:.1f}%)"
