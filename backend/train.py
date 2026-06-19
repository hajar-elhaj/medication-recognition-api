"""
Train a medication-box classifier using transfer learning (MobileNetV2).

Why transfer learning: the dataset is tiny (~30 images/class), far too few to
train a CNN from scratch without overfitting. MobileNetV2 comes pre-trained on
ImageNet; we freeze it and train only a small classification head, plus data
augmentation to stretch the small dataset.

Run from the backend/ folder:   py train.py
Outputs:
  model/medicine_model.h5   - the trained model (preprocessing baked in)
  model/class_names.json    - class order, loaded by cnn.py at inference
"""
import json
import os

import tensorflow as tf
from tensorflow.keras import layers

# ---- paths ----
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TRAIN_DIR = os.path.join(ROOT, "dataset", "train")
TEST_DIR = os.path.join(ROOT, "dataset", "test")
MODEL_DIR = os.path.join(HERE, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "medicine_model.h5")
CLASS_NAMES_PATH = os.path.join(MODEL_DIR, "class_names.json")

# ---- config ----
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 20
SEED = 123

os.makedirs(MODEL_DIR, exist_ok=True)

# ---- datasets ----
# 80/20 split of the train folder for training vs validation.
train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)
test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False,
)

# image_dataset_from_directory sorts class names alphabetically; persist that
# exact order so cnn.py maps prediction indices back to names correctly.
class_names = train_ds.class_names
num_classes = len(class_names)
print("Classes:", class_names)

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)
test_ds = test_ds.cache().prefetch(AUTOTUNE)

# ---- model ----
data_augmentation = tf.keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.1),
    ],
    name="data_augmentation",
)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False  # freeze pretrained backbone

inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
# MobileNetV2's preprocess_input scales pixels to [-1, 1] (x/127.5 - 1).
# Baking it in as a Rescaling layer means cnn.py can feed raw 0-255 images and
# serialization to .h5 stays clean (no Lambda layer).
x = layers.Rescaling(1.0 / 127.5, offset=-1)(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(num_classes, activation="softmax")(x)
model = tf.keras.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
model.summary()

# ---- train ----
callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=5, restore_best_weights=True
    ),
]
model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

# ---- evaluate on the held-out test set ----
test_loss, test_acc = model.evaluate(test_ds)
print(f"\nTest accuracy: {test_acc:.3f}  (loss {test_loss:.3f})")

# ---- save ----
model.save(MODEL_PATH)
with open(CLASS_NAMES_PATH, "w", encoding="utf-8") as fh:
    json.dump(class_names, fh, ensure_ascii=False, indent=2)
print(f"\nSaved model -> {MODEL_PATH}")
print(f"Saved class names -> {CLASS_NAMES_PATH}")
