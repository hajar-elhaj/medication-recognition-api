import easyocr

# EasyOCR uses two separate internal engines: one for Arabic/RTL scripts and
# one for Latin scripts. Arabic cannot be combined with French in a single
# Reader — it raises a ValueError. The solution is two readers run separately,
# then their results are merged.
reader_latin = easyocr.Reader(['fr'], gpu=True)          # handles French text
reader_arabic = easyocr.Reader(['ar', 'en'], gpu=True)   # 'en' is required by EasyOCR when Arabic is used


def extract_text(image):
    """Return all detected text (French + Arabic) from `image`.

    `image` can be a file path (str) or a preprocessed numpy array (uint8).
    """
    results_latin = reader_latin.readtext(image)
    results_arabic = reader_arabic.readtext(image)

    all_results = results_latin + results_arabic
    text = " ".join([r[1] for r in all_results])
    return text
