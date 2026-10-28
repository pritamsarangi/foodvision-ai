
import csv

import pytest
from PIL import Image, features

# CI can run lightweight tests without installing TensorFlow.
# On our local tf_gpu environment, these tests will execute.
tf = pytest.importorskip("tensorflow")

from ml.src.tf_data_pipeline import build_dataset


@pytest.fixture
def sample_image_split(tmp_path):
    root = tmp_path / "images"
    (root / "pizza").mkdir(parents=True)
    (root / "sushi").mkdir(parents=True)

    samples = [
        ("pizza/a.png", "PNG", (255, 0, 0), 4),
        ("sushi/b.jpg", "JPEG", (0, 255, 0), 9),
        ("pizza/c.bmp", "BMP", (0, 0, 255), 4),
    ]

    split_path = tmp_path / "val.csv"

    with split_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ["relative_path", "class_name", "class_index"]
        )

        for relative, image_format, color, label in samples:
            image_path = root / relative

            Image.new(
                "RGB", (32, 32), color
            ).save(image_path, format=image_format)

            writer.writerow([
                relative,
                relative.split("/")[0],
                label,
            ])

    return root, split_path


def test_image_decoding_and_batch_shapes(sample_image_split):
    root, split_path = sample_image_split

    dataset = build_dataset(
        dataset_root=root,
        split_path=split_path,
        batch_size=2,
        training=False,
    )

    batches = list(dataset.as_numpy_iterator())

    assert len(batches) == 2
    assert batches[0][0].shape == (2, 224, 224, 3)
    assert batches[1][0].shape == (1, 224, 224, 3)

    all_labels = [
        int(label)
        for _, labels in batches
        for label in labels
    ]

    assert all_labels == [4, 9, 4]

    for images, _ in batches:
        assert images.dtype.name == "float32"
        assert images.min() >= 0
        assert images.max() <= 255


def test_training_preserves_all_samples(sample_image_split):
    root, split_path = sample_image_split

    dataset = build_dataset(
        dataset_root=root,
        split_path=split_path,
        batch_size=2,
        training=True,
        seed=42,
    )

    labels = [
        int(label)
        for _, batch_labels in dataset.as_numpy_iterator()
        for label in batch_labels
    ]

    assert len(labels) == 3
    assert sorted(labels) == [4, 4, 9]


def test_webp_decoding(tmp_path):
    if not features.check("webp"):
        pytest.skip("Pillow WebP support unavailable")

    root = tmp_path / "images"
    (root / "pizza").mkdir(parents=True)

    image_path = root / "pizza" / "sample.webp"

    Image.new(
        "RGB", (32, 32), (120, 80, 40)
    ).save(image_path, format="WEBP")

    split_path = tmp_path / "test.csv"

    with split_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ["relative_path", "class_name", "class_index"]
        )
        writer.writerow([
            "pizza/sample.webp",
            "pizza",
            4,
        ])

    dataset = build_dataset(
        dataset_root=root,
        split_path=split_path,
        batch_size=1,
        training=False,
    )

    images, labels = next(iter(dataset))

    assert tuple(images.shape) == (1, 224, 224, 3)
    assert labels.numpy().tolist() == [4]
    assert float(tf.reduce_min(images)) >= 0
    assert float(tf.reduce_max(images)) <= 255
