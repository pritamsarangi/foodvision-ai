
import csv
import io
import random
from pathlib import Path, PurePosixPath

import numpy as np
import tensorflow as tf
from PIL import Image


IMAGE_SIZE = (224, 224)
BATCH_SIZE = 8
SEED = 42


def decode_webp(encoded_bytes):
    """Decode WebP images using Pillow."""

    # tf.numpy_function may supply bytes directly 
    # or a NumPy scaler/array depending on the input.
    if hasattr(encoded_bytes, 'item'):
        encoded_bytes = encoded_bytes.item() 

    with Image.open(io.BytesIO(encoded_bytes)) as image:
        return np.asarray(
            image.convert("RGB"),
            dtype=np.uint8,
        )


def load_image(path, label, image_size):
    """Read, decode and resize one image."""

    contents = tf.io.read_file(path)

    is_webp = tf.strings.regex_full_match(
        tf.strings.lower(path),
        r".*\.webp",
    )

    def webp_decoder():
        return tf.numpy_function(
            decode_webp,
            [contents],
            tf.uint8,
        )

    def native_decoder():
        return tf.io.decode_image(
            contents,
            channels=3,
            expand_animations=False,
        )

    image = tf.cond(
        is_webp,
        webp_decoder,
        native_decoder,
    )

    image.set_shape([None, None, 3])

    image = tf.image.resize(
        image,
        image_size,
        method="bilinear",
        antialias=True,
    )

    # Keep resized pixel values within the valid image range.
    image = tf.clip_by_value(
        image,
        clip_value_min=0.0,
        clip_value_max=255.0,
    )

    image = tf.ensure_shape(
        image,
        [image_size[0], image_size[1], 3],
    )

    return image, tf.cast(label, tf.int32)


def build_dataset(
    dataset_root: Path,
    split_path: Path,
    batch_size: int = BATCH_SIZE,
    image_size: tuple = IMAGE_SIZE,
    training: bool = False,
    seed: int = SEED,
):
    """Build a memory-conscious tf.data pipeline."""

    if not dataset_root.is_dir():
        raise ValueError(
            f"Dataset root not found: {dataset_root}"
        )

    paths = []
    labels = []

    with split_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        required = {"relative_path", "class_index"}

        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Invalid split CSV columns")

        for row in reader:
            relative = PurePosixPath(
                row["relative_path"]
            )

            full_path = dataset_root.joinpath(
                *relative.parts
            )

            paths.append(str(full_path))
            labels.append(int(row["class_index"]))

    if not paths:
        raise ValueError("Split contains no images")

    # CSV rows are grouped by food category.
    # Shuffle all metadata first to mix classes.
    examples = list(zip(paths, labels))

    if training:
        rng = random.Random(seed)
        rng.shuffle(examples)

    paths, labels = zip(*examples)

    dataset = tf.data.Dataset.from_tensor_slices(
        (list(paths), list(labels))
    )

    if training:
        dataset = dataset.shuffle(
            buffer_size=min(2048, len(paths)),
            seed=seed,
            reshuffle_each_iteration=True,
        )

    dataset = dataset.map(
        lambda path, label: load_image(
            path, label, image_size
        ),
        num_parallel_calls=2,
    )

    dataset = dataset.batch(
        batch_size,
        drop_remainder=False,
    )

    # Keep the prefetch queue small initially.
    dataset = dataset.prefetch(1)

    return dataset
