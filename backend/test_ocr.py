import easyocr

reader = easyocr.Reader(['fr'])

image_path = r"C:\Users\hajar\Downloads\doli.jpg"

result = reader.readtext(image_path)

for r in result:
    print(r[1])