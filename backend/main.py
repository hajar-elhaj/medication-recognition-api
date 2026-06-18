from cnn import predict_medicine
from ocr import extract_text
from db import get_connection
import cv2
import re

image_path = r"C:\Users\frita\OneDrive\Desktop\medication-recognition-api\dataset\train\ventoline\images (7).jpg"



# CNN PREDICTION

medicine = predict_medicine(image_path)
print("\nCNN Prediction:", medicine)



# PREPROCESS IMAGE (OpenCV)

def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        raise Exception("Image not found")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return thresh


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


processed_image = preprocess_image(image_path)
text = extract_text(processed_image)
text = clean_text(text)

print("\nOCR RESULT:")
print(text)



# DATABASE

db = get_connection()
cursor = db.cursor()

cursor.execute("SELECT name, dosage, usage_description FROM medicines")
rows = cursor.fetchall()



# MATCH OCR → DB 

best_medicine = medicine   # CNN is primary source

dosage = ""
usage = ""

for row in rows:
    if row[0].lower() == best_medicine.lower():
        dosage = row[1]
        usage = row[2]
        break




# OUTPUT

print("\nFINAL RESULT:")
print("Medicine:", best_medicine)
print("Dosage:", dosage)
print("Usage:", usage)
