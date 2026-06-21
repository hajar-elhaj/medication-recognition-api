# Medication Box Recognition API

A computer-vision system that recognizes medications from a photo of their
packaging. It combines a CNN image classifier with multilingual OCR
(French + Arabic), then matches the result against a medication database to
return the medicine's name, dosage, pharmaceutical form, and usage — in both
French and Arabic. It is exposed as a REST API and ships with a simple web
frontend.

> **Academic project — Master IT, Mohammed V University (Faculty of Sciences, Rabat).**
> Authors: **Hajar El Haj** & **Ikram Belmalhouz**.
> Supervisor: **Pr. Abdelhak Mahmoudi** · Co-supervisor: **Saad Frihi**.

---

## Demo at a glance

Upload a photo of a medicine box → the system returns one of three honest
verdicts and, when recognized, the full bilingual details:

| Verdict | Meaning |
|---------|---------|
| **recognized** (`matched` / `partial`) | The name was read and matched to the database; dosage & form identified when readable. |
| **unrecognized** | The text was read clearly, but it matches no medicine in the database. |
| **rejected** | Not a medicine box (e.g. an object or animal), or the text was unreadable. |

The system **never invents an identity**: an *exact* dosage/form is reported
only when the dosage was actually read from the box.

---

## Features

- **Name recognition from text (primary)** — the medicine name is read from the
  box via OCR + fuzzy matching (RapidFuzz). This is the most reliable signal;
  the CNN is only a fallback. Works for Latin **and** Arabic-only boxes.
- **CNN classification (fallback)** — MobileNetV2 (transfer learning) predicts
  the medicine when no name can be read, and helps reject non-medicines.
- **Multilingual OCR** — EasyOCR reads both French and Arabic text (two separate
  readers, merged).
- **Adaptive image preprocessing** — OpenCV measures each image (brightness,
  contrast, sharpness) and applies only the corrections it needs (CLAHE,
  unsharp mask, bilateral filter).
- **Dosage & form extraction** — robust to OCR quirks: split number/unit,
  French long forms (`microgrammes`), symbols (`µg`), Arabic units (`مجم`, `ملغ`,
  …) and both Arabic numeral systems (`٠-٩` and `۰-۹`).
- **Three-way input validation** — recognized / unrecognized / rejected.
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

Orchestration lives in `pipeline.py`, shared by both the API (`app.py`) and the
command-line demo (`main.py`).

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
│   ├── train.py          # CNN training script (optional)
│   ├── fetch_other.py    # downloads the "other" (non-medicine) class
│   ├── db_setup.sql      # creates + seeds the database (schema + 33 variants)
│   ├── .env.example      # template for DB credentials
│   └── model/
│       ├── medicine_model.h5    # trained CNN (committed, ~9 MB)
│       └── class_names.json     # class order used at inference
├── frontend/
│   └── index.html        # web UI (open in a browser)
├── evaluation/
│   ├── images/           # 20 fresh test images
│   └── results.md        # full evaluation report & metrics
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

### 3. Create and seed the database
`backend/db_setup.sql` is self-contained: it creates the `medicines_db`
database, the `medicines` table, and inserts all 33 medicine variants (with
French + Arabic names, forms, and usages). Run it once:
```bash
mysql --default-character-set=utf8mb4 -u root -p < backend/db_setup.sql
```
> ⚠️ **Keep `--default-character-set=utf8mb4`.** The Windows `mysql` client
> defaults to `cp850`, which corrupts the Arabic and accented-French text on
> import (you would see mojibake like `fi├¿vre`). The flag forces UTF-8.

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

> **Reproducibility note.** The trained CNN model
> (`backend/model/medicine_model.h5`, ~9 MB) is committed to the repository, so
> the project runs after a fresh clone **without retraining**. You only need the
> three steps above (dependencies, database, credentials).

---

## Running

### Option A — REST API (recommended)
```bash
cd backend
python -m uvicorn app:app --reload
```
Then open the interactive docs in your browser:

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
Run with no argument to use the bundled sample image:
```bash
python main.py
```

> Good images to try are in `evaluation/images/` — e.g. `smecta.jpg` (exact
> match), `doliprane_in_arabic.webp` (Arabic box), `candy.webp` (rejected).

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
dosage/form not confirmed), `unrecognized` (readable text, no DB match),
`not_in_db`, or `rejected` (not a medicine).

---

## Recognition strategy

The medicine **name** is taken from the **printed text** (OCR + fuzzy matching),
not the CNN — the name on the box is the most reliable identifier, and the CNN
(trained on a small dataset) confuses visually similar boxes. The CNN is used
only as a fallback when no name is readable, and to help reject non-medicines.

An **exact** dosage/form is reported only when the dosage was actually read from
the box, so the system never asserts a dosage it did not see.

---

## Evaluation

The system was evaluated on **20 fresh images** (never used in training):
known and unknown medicines, blurry photos, Arabic-only boxes, rotated/flipped
boxes, and non-medicine objects. Headline results:

| Metric | Result |
|--------|--------|
| Known medicines correctly named | **11 / 11 — 100 %** |
| No false medicine identity shown | **17 / 20 — 85 %** |
| Non-medicines correctly rejected | **2 / 2 — 100 %** |

Full methodology, per-image results, and a limitations analysis are in
[`evaluation/results.md`](evaluation/results.md).

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

## Retraining the CNN (optional)

The trained model is already included. To retrain from the `dataset/` folder:
```bash
cd backend
python fetch_other.py   # downloads the non-medicine "other" class (once)
python train.py         # trains and saves model/medicine_model.h5
```
Class order is saved to `model/class_names.json` and must stay aligned with the
alphabetical dataset folder names.
