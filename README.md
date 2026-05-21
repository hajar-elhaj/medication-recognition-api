# Medication Recognition API

## Project Overview
This project is a prototype system that recognizes medication names from images of medicine packaging using OCR and image processing techniques.

## Pipeline
Image → Preprocessing → OCR (EasyOCR) → Text Extraction → Database Matching (MySQL) → Fuzzy Matching (RapidFuzz)

## Technologies Used
- Python
- OpenCV
- EasyOCR
- MySQL
- RapidFuzz

## Current Progress
- OCR extraction is working
- MySQL database is connected
- Fuzzy matching is implemented
- Basic end-to-end pipeline is functional

## Next Steps
- Improve OCR accuracy using preprocessing techniques
- Build REST API for external access
- Improve multilingual support (Arabic + French)