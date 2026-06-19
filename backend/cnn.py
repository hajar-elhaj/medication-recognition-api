import json
import os

import numpy as np
import tensorflow as tf

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "model", "medicine_model.h5")
CLASS_NAMES_PATH = os.path.join(HERE, "model", "class_names.json")

model = tf.keras.models.load_model(MODEL_PATH)

# Load the class order saved by train.py so prediction indices always map back to
# the right name. Falls back to the alphabetical folder order if the file is
# missing (image_dataset_from_directory sorts class folders alphabetically).
if os.path.exists(CLASS_NAMES_PATH):
    with open(CLASS_NAMES_PATH, encoding="utf-8") as fh:
        class_names = json.load(fh)
else:
    class_names = ["augmentin", "brufen", "doliprane", "other", "smecta", "ventoline"]


def predict_medicine(image_path):
    """Return (predicted_class_name, confidence_percent)."""
    img = tf.keras.utils.load_img(image_path, target_size=(224, 224))
    img = tf.keras.utils.img_to_array(img)
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img, verbose=0)   # verbose=0 suppresses the progress bar
    idx = int(np.argmax(pred))
    confidence = float(pred[0][idx]) * 100
    return class_names[idx], confidence
