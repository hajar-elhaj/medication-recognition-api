from ocr import extract_text
from db import get_connection
from matcher import find_best_match

#IMAGE PATH
image_path = r"C:\Users\hajar\OneDrive\Bureau\medication-recognition-api\images\dolipran.jpg"

#OCR STEP
text = extract_text(image_path)
print("\nOCR RESULT:")
print(text)

#CONNECT DB
db = get_connection()
cursor = db.cursor()

cursor.execute("SELECT name FROM medicines")
medicines = [row[0] for row in cursor.fetchall()]

print("\nDATABASE MEDICINES:")
print(medicines)

#MATCHING
result = find_best_match(text, medicines)

print("\nFINAL RESULT:")
print(result)