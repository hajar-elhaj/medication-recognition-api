"""FastAPI REST layer for the Medication Box Recognition system.

Run from the backend/ folder:
    uvicorn app:app --reload

Then open the interactive docs at:
    http://localhost:8000/docs

Endpoints:
    GET  /            health check
    POST /recognize   upload an image, get the recognition result as JSON
"""
import os
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pipeline import recognize

app = FastAPI(
    title="Medication Box Recognition API",
    description=(
        "Upload a photo of a medicine box. The API runs a CNN classifier and "
        "multilingual OCR (French + Arabic), then matches the result against a "
        "medication database to identify the medicine, its dosage and form."
    ),
    version="1.0.0",
)

# Allow a future frontend (React/Vue/plain JS) on any origin to call the API.
# For production, replace ["*"] with the specific frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Accept the common image types the model and OCR can handle.
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@app.get("/")
def health():
    """Simple health check."""
    return {"status": "ok", "service": "Medication Box Recognition API"}


@app.post("/recognize")
async def recognize_endpoint(file: UploadFile = File(...)):
    """Recognize a medicine from an uploaded image.

    Returns the CNN prediction, OCR text, detected language, and—if the image
    is a known medicine—its bilingual name, usage, and exact dosage/form.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. "
                   f"Allowed: {', '.join(sorted(ALLOWED_TYPES))}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")

    # The pipeline reads from disk (cv2/tf load by path), so persist the upload
    # to a temp file, run recognition, then always clean it up.
    suffix = os.path.splitext(file.filename or "")[1] or ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        result = recognize(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recognition failed: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return result
