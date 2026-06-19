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


def recognize(image_path):
    """Run the full recognition pipeline on an image file.

    Returns a dict describing the result. The 'status' field is one of:
      'rejected' — the image is not a medicine box (other fields explain why)
      'matched'  — an exact dosage+form variant was identified
      'partial'  — the medicine is known but the exact box couldn't be pinned
      'not_in_db'— the CNN class isn't present in the database
    """
    # ── CNN PREDICTION ──────────────────────────────────────────────────────
    medicine, confidence = predict_medicine(image_path)
    result_cnn = medicine   # remember the raw CNN guess for reference/fallback

    # ── ADAPTIVE PREPROCESSING (OpenCV) ─────────────────────────────────────
    preprocessed, report = adaptive_preprocess(image_path)

    # ── OCR (French + Arabic) ───────────────────────────────────────────────
    ocr_text = clean_text(extract_text(preprocessed))
    language = detect_language(ocr_text)

    # ── DECIDE THE MEDICINE NAME ────────────────────────────────────────────
    # The name is printed on the box, so the OCR text identifies it far more
    # reliably than the CNN (which only sees the image and confuses similar
    # boxes). Strategy: trust a confident fuzzy name match from the OCR text;
    # fall back to the CNN only when the text gives us no clear name.
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT name, name_ar FROM medicines")
    name_rows = cursor.fetchall()
    known_names = [r[0] for r in name_rows]
    name_ar_map = {r[0]: r[1] for r in name_rows if r[1]}

    ocr_name, name_score = match_name(ocr_text, known_names, name_ar=name_ar_map)
    if ocr_name:
        medicine = ocr_name           # OCR is authoritative for the name
        name_source = "OCR text"
    else:
        name_source = "CNN"           # no name in the text — fall back to CNN

    result = {
        "cnn_prediction": result_cnn,
        "confidence": round(confidence, 1),
        "medicine_name": medicine,
        "name_source": name_source,
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

    # ── INPUT VALIDATION ────────────────────────────────────────────────────
    # A confident OCR name match is itself strong proof this is a real medicine.
    if ocr_name:
        ok, reason = True, f"OCR text matches known medicine '{ocr_name}' ({name_score:.0f}% similarity)"
    elif medicine == "other":
        ok, reason = False, f"CNN classified the image as 'other' ({confidence:.1f}%)"
    else:
        ok, reason = is_medicine(ocr_text, confidence, known_names)

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
