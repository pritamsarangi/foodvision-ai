
import io
import json
import os
from functools import lru_cache
from pathlib import Path

# Force TensorFlow to use CPU for backend inference.
# This avoids interfering with GPU model training.
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps


# Project root: C:/deep_learning_projects/foodvision-ai
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = (
    PROJECT_ROOT / "ml" / "experiments" / "efficientnet_b0"
)

WEIGHTS_PATH = MODEL_DIR / "best_finetuned_weights.h5"

CLASSES_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "splits"
    / "class_to_index.json"
)


@lru_cache(maxsize=1)
def load_model():
    # Load food class names
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        class_to_index = json.load(f)

    index_to_class = {
        int(index): name
        for name, index in class_to_index.items()
    }

    # Recreate EfficientNet-B0 backbone
    base_model = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights=None,
        input_shape=(224, 224, 3),
    )

    
    # Match the trainable-layer configuration used
    # when the fine-tuned checkpoint was saved.

    base_model.trainable = True

    # Only the last 20 backbone layers were unfrozen.
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    # All BatchNormalization layers remained frozen.
    for layer in base_model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False


    # Recreate classification architecture
    inputs = tf.keras.layers.Input(
        shape=(224, 224, 3),
        name="input_image",
    )

    x = base_model(inputs, training=False)

    x = tf.keras.layers.GlobalAveragePooling2D()(x)

    x = tf.keras.layers.Dropout(0.3)(x)

    outputs = tf.keras.layers.Dense(
        len(index_to_class),
        activation="softmax",
    )(x)

    model = tf.keras.Model(
        inputs=inputs,
        outputs=outputs,
        name="foodvision_efficientnet_b0",
    )

    # Restore the fine-tuned model weights
    model.load_weights(str(WEIGHTS_PATH))

    return model, index_to_class


def predict_image(image_bytes):
    model, index_to_class = load_model()

    # Decode the uploaded image
    with Image.open(io.BytesIO(image_bytes)) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = image.resize(
            (224, 224),
            Image.Resampling.BILINEAR,
        )

        image_array = np.asarray(
            image,
            dtype=np.float32,
        )

    # EfficientNet includes its own preprocessing.
    # Keep image values in the 0-255 range.
    batch = np.expand_dims(image_array, axis=0)

    # Run inference
    probabilities = model(
        batch,
        training=False,
    ).numpy()[0]

    # Extract five most likely food categories
    top_indices = np.argsort(probabilities)[-5:][::-1]

    top_5 = [
        {
            "food_name": index_to_class[int(index)],
            "confidence": float(probabilities[index]),
        }
        for index in top_indices
    ]

    return top_5
