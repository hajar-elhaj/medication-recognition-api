# Medication Box Recognition API

A computer-vision system that recognizes medications from a photo of their
packaging. It combines a CNN image classifier with multilingual OCR
(French + Arabic), then matches the result against a medication database to
return the medicine's name, dosage, pharmaceutical form, and usage — in both
French and Arabic. It is exposed as a REST API and comes with a simple web
frontend.

> Academic project — Master IT. Supervised by Abdelhak Mahmoudi.

---

## Features

- **CNN classification** — MobileNetV2 (transfer learning) predicts the medicine
  from the image.
- **Name recognition from text** — the medicine name is read from the box via
  OCR + fuzzy matching (RapidFuzz). This is the primary, most reliable signal;
  the CNN is a fallback. Works for Latin **and** Arabic-only boxes.
- **Multilingual OCR** — EasyOCR reads both French and Arabic text.
- **Adaptive image preprocessing** — OpenCV analyzes each image (brightness,
  contrast, sharpness) and applies only the corrections it needs (CLAHE,
  unsharp mask, bilateral filter).
- **Dosage & form extraction** — robust to OCR quirks: handles split number/unit,
  French long forms (`microgrammes`), symbols (`µg`), Arabic units (`مجم`, `ملغ`,
  …) and both Arabic numeral systems (`٠-٩` and `۰-۹`).
- **Input validation** — rejects images that are not medicine boxes.
- **Bilingual output** — name, form, and usage in French and Arabic.
- **REST API** with automatic interactive documentation (Swagger UI).
- **Web frontend** — drag-and-drop upload with a clean result card.

---

## Pipeline

```
Image
  → CNN prediction (MobileNetV2)            [cnn.py]
  → Adaptive preprocessing (OpenCV)         [preprocess.py]
  → OCR, French + Arabic (EasyOCR)          [ocr.py]
  → Name recognition (RapidFuzz fuzzy)      [matcher.py: match_name]
  → Input validation                        [validation.py]
  → Database lookup (MySQL)                 [db.py]
  → Dosage + form variant matching          [matcher.py: identify_variant]
  → Result (FR + AR)
```

The orchestration lives in `pipeline.py` and is shared by both the API
(`app.py`) and the command-line demo (`main.py`).

---

## Technology stack

| Area | Technology |
|------|-----------|
| Language | Python 3.11 |
| CNN | TensorFlow / Keras (MobileNetV2) |
| Image processing | OpenCV |
| OCR | EasyOCR (PyTorch backend) |
| Fuzzy matching | RapidFuzz |
| Database | MySQL |
| REST API | FastAPI + Uvicorn |
| Frontend | HTML + CSS + JavaScript (no framework) |

---

## Project structure

```
medication-recognition-api/
├── backend/
│   ├── app.py            # FastAPI REST layer (POST /recognize)
│   ├── main.py           # command-line demo over the pipeline
│   ├── pipeline.py       # shared recognition pipeline
│   ├── cnn.py            # CNN model loading + prediction
│   ├── ocr.py            # EasyOCR (French + Arabic)
│   ├── preprocess.py     # adaptive OpenCV preprocessing
│   ├── matcher.py        # name matching + dosage/form variant matching
│   ├── validation.py     # "is this a medicine box?" checks
│   ├── db.py             # MySQL connection
│   ├── train.py          # CNN training script
│   ├── fetch_other.py    # downloads the "other" (non-medicine) class
│   ├── db_setup.sql      # adds the `form` column (one-time)
│   ├── .env.example      # template for DB credentials
│   └── model/            # trained model + class_names.json
├── frontend/
│   └── index.html        # web UI (open in a browser)
├── dataset/              # training/test images per class
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Prerequisites
- Python 3.11
- MySQL server running locally

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up the database
Create the database and table, then load your medicine data. The schema uses
these columns: `name`, `dosage`, `form`, `form_ar`, `name_ar`, `usage_fr`,
`usage_ar`, `usage_description`.

If you are adding the `form` column to an existing table, run:
```bash
mysql -u root -p medicines_db < backend/db_setup.sql
```

### 4. Configure credentials
Copy the example env file and fill in your MySQL password:
```bash
cp backend/.env.example backend/.env
```
`backend/.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=medicines_db
```
(`.env` is gitignored — credentials are never committed.)

---

## Running

### Option A — REST API (recommended)
```bash
cd backend
python -m uvicorn app:app --reload
```
Then open the interactive docs to test it in your browser:

**http://localhost:8000/docs**

Click `POST /recognize` → **Try it out** → choose an image → **Execute**.

### Option B — Web frontend
With the API running (Option A), open `frontend/index.html` in your browser
(double-click it). Drag in a medicine image and click **Recognize**.

### Option C — Command line
```bash
cd backend
python main.py "C:\path\to\medicine.jpg"
```

---

## API

### `GET /`
Health check. Returns `{"status": "ok", ...}`.

### `POST /recognize`
Upload an image (multipart form field **`file`**). Returns JSON, e.g.:
```json
{
  "cnn_prediction": "doliprane",
  "confidence": 64.8,
  "medicine_name": "Doliprane",
  "name_source": "OCR text",
  "name_match_score": 100.0,
  "status": "matched",
  "medicine": {
    "name": "Doliprane",
    "name_ar": "دوليبران",
    "usage_fr": "Soulagement de la douleur et de la fièvre",
    "usage_ar": "تخفيف الألم والحمى"
  },
  "detected": { "dosage": "1000mg", "form": "comprimé" },
  "exact_variant": { "dosage": "1000mg", "form": "comprimé", "form_ar": "قرص" }
}
```
`status` is one of: `matched` (exact variant), `partial` (medicine known, exact
dosage/form not confirmed), `not_in_db`, or `rejected` (not a medicine).

---

## Recognition strategy

The medicine **name** is taken from the **printed text** (OCR + fuzzy matching),
not the CNN — the name on the box is the most reliable identifier, and the CNN
(trained on a small dataset) confuses visually similar boxes. The CNN is used
only as a fallback when no name is readable in the text.

An **exact** dosage/form is reported only when the dosage was actually read from
the box, so the system never asserts a dosage it did not see.

---

## GPU acceleration (optional)

EasyOCR installs the CPU build of PyTorch on Windows. To run OCR on an NVIDIA GPU
(significantly faster), reinstall PyTorch with CUDA:
```bash
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```
Verify:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```
Note: the TensorFlow CNN runs on CPU on native Windows (TF ≥ 2.11 dropped
native-Windows GPU support), but a single CNN prediction is fast regardless.

---

## Training the CNN (optional)

To retrain the classifier from the `dataset/` folder:
```bash
cd backend
python fetch_other.py   # downloads the non-medicine "other" class (once)
python train.py         # trains and saves model/medicine_model.h5
```
Class order is saved to `model/class_names.json` and must stay aligned with the
alphabetical dataset folder names.
