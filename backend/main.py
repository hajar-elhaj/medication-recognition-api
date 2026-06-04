from ocr import extract_text
from db import get_connection
from matcher import find_best_match
import cv2
import re

# IMAGE PATH
image_path = r"C:\Users\frita\OneDrive\Desktop\medication-recognition-api\images\dolipran.jpg"



# PREPROCESS IMAGE (OpenCV)

def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        raise Exception("Image not found or invalid path")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return thresh



# CLEAN OCR TEXT

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text



# OCR STEP 

processed_image = preprocess_image(image_path)

text = extract_text(processed_image)
text = clean_text(text)

print("\nOCR RESULT:")
print(text)



# DATABASE CONNECTION

db = get_connection()
cursor = db.cursor()

cursor.execute("SELECT name, dosage, usage_description FROM medicines")
rows = cursor.fetchall()

medicines = [row[0] for row in rows]

print("\nDATABASE MEDICINES:")
print(medicines)



# MATCHING

result = find_best_match(text, medicines)

best_medicine = result[0]
similarity = result[1]

# Similarity threshold
if similarity < 75:
    print("\nFINAL RESULT:")
    print("No confident match found")
    exit()

dosage = ""
usage = ""

for row in rows:
    if row[0] == best_medicine:
        dosage = row[1]
        usage = row[2]
        break


#output
print("\nFINAL RESULT:")
print("Medicine:", best_medicine)
print("Dosage:", dosage)
print("Usage:", usage)
print("Similarity:", similarity)