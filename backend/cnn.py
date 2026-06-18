import tensorflow as tf
import numpy as np


model = tf.keras.models.load_model(
    r"C:\Users\frita\OneDrive\Desktop\medication-recognition-api\backend\model\medicine_model.h5"
)

class_names = ["aspirin","brufen","doliprane","smecta","ventoline"]

def predict_medicine(image_path):
    img = tf.keras.utils.load_img(image_path, target_size=(224,224))
    img = tf.keras.utils.img_to_array(img)
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img)
    return class_names[np.argmax(pred)]

