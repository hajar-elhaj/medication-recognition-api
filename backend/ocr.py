import easyocr

reader = easyocr.Reader(['fr'])

def extract_text(image_path):
    result = reader.readtext(image_path)

    text = " ".join([r[1] for r in result])

    return text