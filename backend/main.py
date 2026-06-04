from ocr import extract_text
from db import get_connection
from matcher import find_best_match

# IMAGE PATH
image_path = r"C:\Users\frita\OneDrive\Desktop\medication-recognition-api\images\dolipran.jpg"

# OCR STEP
text = extract_text(image_path)

print("\nOCR RESULT:")
print(text)

# CONNECT DB
db = get_connection()
cursor = db.cursor()
cursor.execute("SELECT name, dosage, usage_description FROM medicines")
rows = cursor.fetchall()

medicines = [row[0] for row in rows]

result = find_best_match(text, medicines)

best_medicine = result[0]
similarity = result[1]

dosage = ""
usage = ""

for row in rows:
    if row[0] == best_medicine:
        dosage = row[1]
        usage = row[2]
        break

print("\nFINAL RESULT:")
print("Medicine:", best_medicine)
print("Dosage:", dosage)
print("Usage:", usage)
print("Similarity:", similarity)