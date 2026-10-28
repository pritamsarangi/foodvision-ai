
from pathlib import Path

import tensorflow as tf
import argparse

from ml.src.tf_data_pipeline import build_dataset

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--splits-dir",
        type=Path,
        default=Path("ml/reports/splits"),
    )
    args = parser.parse_args()

    gpus = tf.config.list_physical_devices("GPU")

    if gpus:
        tf.config.experimental.set_memory_growth(
            gpus[0], True
        )

    print("TensorFlow:", tf.__version__)
    print("GPU devices:", gpus)

    for name in ("train", "val", "test"):
        dataset = build_dataset(
            dataset_root=args.dataset_root,
            split_path=args.splits_dir / f"{name}.csv",
            batch_size=8,
            training=(name == "train"),
        )

        images, labels = next(iter(dataset))

        print(f"\n{name.upper()} BATCH")
        print("Image shape:", images.shape)
        print("Label shape:", labels.shape)
        print("Image dtype:", images.dtype)
        print("Min pixel value:",
              float(tf.reduce_min(images)))
        print("Max pixel value:",
              float(tf.reduce_max(images)))
        print("Labels:", labels.numpy())

        assert images.shape[1:] == (224, 224, 3)
        assert labels.shape[0] == images.shape[0]
        assert bool(tf.reduce_all(tf.math.is_finite(images)))
        assert float(tf.reduce_min(images)) >= 0
        assert float(tf.reduce_max(images)) <= 255

    print("\nAll data-loading smoke tests passed!")


if __name__ == "__main__":
    main()
