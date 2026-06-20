"""Core recognition pipeline, shared by the CLI (main.py) and the API (app.py).

Given an image path, runs the full flow:
  CNN prediction -> adaptive OpenCV preprocessing -> OCR (FR + AR) ->
  input validation -> DB lookup -> exact-variant matching

and returns a single structured dict. No printing here — callers decide how
to present the result (console text or JSON response).
"""
import re

from cnn import predict_medicine
from ocr import extract_text
from db import get_connection
from matcher import identify_variant, match_name
from validation import has_text, detect_language, is_medicine
from preprocess import adaptive_preprocess


def clean_text(text):
    """Keep Latin letters, digits, the Arabic Unicode block and spaces."""
    text = re.sub(r'[^\w؀-ۿ ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _has_readable_text(text):
    """True if OCR produced enough real words to trust it actually read the box.

    This is what tells two very different failures apart:
      - "this medicine isn't in our database" — the box text was read clearly
        (≥2 real words) but matched no known name. The medicine name is printed
        on the box, so if it were one of ours, OCR would have found it.
      - "the image was too poor to read" — almost no text came out, so the only
        signal left is the CNN's visual guess.
    """
    words = re.findall(r"[a-zA-Z؀-ۿ]{3,}", text or "")
    return len(words) >= 2


def recognize(image_path):
    """Run the full recognition pipeline on an image file.

    Returns a dict describing the result. The 'status' field is one of:
      'rejected'     — the image is not a medicine box (other fields explain why)
      'unrecognized' — the box text was read clearly but matches no medicine in
                       our database (e.g. a real medicine we simply don't stock)
      'matched'      — an exact dosage+form variant was identified
      'partial'      — the medicine is known but the exact box couldn't be pinned
      'not_in_db'    — the CNN class isn't present in the database
    """
    # ── CNN PREDICTION ──────────────────────────────────────────────────────
    medicine, confidence = predict_medicine(image_path)
    result_cnn = medicine   # remember the raw CNN guess for reference/fallback

    # ── ADAPTIVE PREPROCESSING (OpenCV) ─────────────────────────────────────
    preprocessed, report = adaptive_preprocess(image_path)

    # ── OCR (French + Arabic) ───────────────────────────────────────────────
    ocr_text = clean_text(extract_text(preprocessed))
    language = detect_language(ocr_text)

    # ── LOAD KNOWN NAMES ────────────────────────────────────────────────────
    # The name is printed on the box, so the OCR text identifies it far more
    # reliably than the CNN (which only sees the image and confuses similar
    # boxes). Strategy below, in order: (1) trust a confident fuzzy name match
    # from the OCR text; (2) if the text was read clearly but matches nothing,
    # the medicine isn't in our DB → 'unrecognized' (no CNN guess); (3) only
    # when the text is unreadable do we fall back to the CNN's visual guess.
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT name, name_ar FROM medicines")
    name_rows = cursor.fetchall()
    known_names = [r[0] for r in name_rows]
    name_ar_map = {r[0]: r[1] for r in name_rows if r[1]}

    ocr_name, name_score = match_name(ocr_text, known_names, name_ar=name_ar_map)

    # Fields shared by every return path.
    result = {
        "cnn_prediction": result_cnn,
        "confidence": round(confidence, 1),
        "name_match_score": round(name_score, 1),
        "image_analysis": {
            "brightness": round(report["brightness"], 1),
            "contrast": round(report["contrast"], 1),
            "sharpness": round(report["sharpness"], 1),
            "applied": report["applied"],
        },
        "ocr_text": ocr_text,
        "language": language,
        "has_text": has_text(ocr_text),
    }

    # ── DECIDE THE MEDICINE NAME + VALIDATE ─────────────────────────────────
    if ocr_name:
        # A known name was read from the box — authoritative, and itself strong
        # proof this is a real medicine.
        medicine = ocr_name
        name_source = "OCR text"
        ok = True
        reason = (f"OCR text matches known medicine '{ocr_name}' "
                  f"({name_score:.0f}% similarity)")
    elif _has_readable_text(ocr_text):
        # The box text was read clearly, yet it matches NONE of our medicines.
        # The name is printed on the box, so this is strong evidence the medicine
        # is simply not in our database — we must NOT fall back to the CNN's
        # forced guess among its 5 classes (that wrongly labelled e.g. a Myoflex
        # tube as "Augmentin"). Use is_medicine() only to tell an unknown
        # *medicine* apart from a non-medicine image with text.
        ok, reason = is_medicine(ocr_text, confidence, known_names)
        result["medicine_name"] = None
        result["name_source"] = "OCR text"
        result["is_medicine"] = ok
        if ok:
            result["status"] = "unrecognized"
            result["reason"] = ("Readable text found, but it matches no medicine "
                                "in the database.")
        else:
            result["status"] = "rejected"
            result["reason"] = reason
        cursor.close()
        db.close()
        return result
    else:
        # Too little readable text (blurry/dark box) to identify the name from
        # the text — fall back to the CNN's visual guess as a last resort.
        medicine = result_cnn
        name_source = "CNN"
        if medicine == "other":
            ok = False
            reason = f"CNN classified the image as 'other' ({confidence:.1f}%)"
        else:
            ok, reason = is_medicine(ocr_text, confidence, known_names)

    result["medicine_name"] = medicine
    result["name_source"] = name_source
    result["is_medicine"] = ok
    result["reason"] = reason

    if not ok:
        cursor.close()
        db.close()
        result["status"] = "rejected"
        return result

    # ── DATABASE LOOKUP ─────────────────────────────────────────────────────
    cursor.execute(
        "SELECT name_ar, usage_fr, usage_ar, dosage, form, form_ar "
        "FROM medicines WHERE LOWER(name) = LOWER(%s) ORDER BY dosage",
        (medicine,),
    )
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    if not rows:
        result["status"] = "not_in_db"
        return result

    result["medicine"] = {
        "name": medicine,
        "name_ar": rows[0][0] or "",
        "usage_fr": rows[0][1] or "",
        "usage_ar": rows[0][2] or "",
    }

    # ── EXACT VARIANT MATCHING ──────────────────────────────────────────────
    variants = [{"dosage": r[3], "form": r[4], "form_ar": r[5]} for r in rows]
    match = identify_variant(ocr_text, variants)

    result["detected"] = {"dosage": match["dosage"], "form": match["form"]}

    if match["exact"]:
        result["status"] = "matched"
        result["exact_variant"] = match["exact"]
    else:
        result["status"] = "partial"
        result["candidates"] = match["candidates"]

    return result
