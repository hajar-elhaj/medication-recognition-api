"""CLI demo of the recognition pipeline.

Runs the same pipeline the API uses (see pipeline.py / app.py) on a single
image and prints a human-readable report. Pass an image path as an argument,
or it falls back to the default sample below.

    py main.py "C:\\path\\to\\box.jpg"
"""
import sys

from pipeline import recognize

DEFAULT_IMAGE = r"C:\Users\frita\OneDrive\Desktop\medication-recognition-api\dataset\train\ventoline\images (7).jpg"

image_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE

r = recognize(image_path)

# ── CNN PREDICTION ──────────────────────────────────────────────────────────
print("\nCNN Prediction :", r["cnn_prediction"])
print(f"Confidence     : {r['confidence']:.1f}%  (visual guess)")

# ── IMAGE ANALYSIS (OpenCV) ─────────────────────────────────────────────────
a = r["image_analysis"]
print("\nIMAGE ANALYSIS (OpenCV):")
print(f"  Brightness : {a['brightness']:.1f}")
print(f"  Contrast   : {a['contrast']:.1f}")
print(f"  Sharpness  : {a['sharpness']:.1f}")
print(f"  Applied    : {a['applied'] if a['applied'] else 'none (image quality OK)'}")

# ── OCR ─────────────────────────────────────────────────────────────────────
print("\nOCR RESULT:")
print(r["ocr_text"])

# ── INPUT VALIDATION ────────────────────────────────────────────────────────
print("\n" + "-" * 50)
print("INPUT VALIDATION")
print("-" * 50)
print(f"Text detected : {'yes' if r['has_text'] else 'no'}")
print(f"Language      : {r['language']}")
print(f"Is a medicine : {'yes' if r['is_medicine'] else 'no'} ({r['reason']})")

if r["status"] == "rejected":
    print("\n>> Rejected: this image does not appear to be a medicine box.")
    raise SystemExit(0)

# ── FINAL RESULT ────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("FINAL RESULT")
print("=" * 50)
print(f"Medicine (FR) : {r['medicine_name']}")
print(f"Name source   : {r['name_source']} (match {r['name_match_score']:.0f}%)")

if r["status"] == "not_in_db":
    print("Medicine not found in database.")
    raise SystemExit(0)

m = r["medicine"]
print(f"Medicine (AR) : {m['name_ar']}")
print(f"Usage (FR)    : {m['usage_fr']}")
print(f"Usage (AR)    : {m['usage_ar']}")

if r["status"] == "matched":
    exact = r["exact_variant"]
    print("\n>> Exact match (from OCR):")
    print(f"   Dosage     : {exact['dosage']}")
    print(f"   Form (FR)  : {exact['form']}")
    print(f"   Form (AR)  : {exact['form_ar']}")
else:  # partial
    detected = []
    if r["detected"]["dosage"]:
        detected.append(f"dosage='{r['detected']['dosage']}'")
    if r["detected"]["form"]:
        detected.append(f"form='{r['detected']['form']}'")
    hint = f" (OCR detected {', '.join(detected)})" if detected else ""
    candidates = r["candidates"]
    print(f"\n>> Could not pin down the exact box{hint}.")
    print(f"   Possible variants ({len(candidates)}):")
    for v in candidates:
        print(f"   - {v['dosage']:<8} | {v['form'] or '?':<22} | {v['form_ar'] or ''}")
