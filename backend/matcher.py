from rapidfuzz import process

def find_best_match(text, medicines_list):
    match = process.extractOne(text, medicines_list)
    return match