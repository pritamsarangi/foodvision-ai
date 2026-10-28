
import csv
import json
from collections import Counter
from pathlib import Path

import pytest

from ml.src.create_splits import create_splits, load_manifest


@pytest.fixture
def sample_manifest(tmp_path):
    """Create a small manifest with three food classes."""

    path = tmp_path / "clean_manifest.csv"

    class_counts = {
        "pizza": 20,
        "sushi": 10,
        "ginger": 7,
    }

    with path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["class_name", "relative_path"])

        for class_name, count in class_counts.items():
            for index in range(count):
                writer.writerow([
                    class_name,
                    f"{class_name}/image_{index:03d}.jpg",
                ])

    return path


def read_split(path: Path):
    with path.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def test_split_counts(sample_manifest, tmp_path):
    output_dir = tmp_path / "splits"

    summary = create_splits(
        sample_manifest,
        output_dir,
        seed=42,
    )

    assert summary["total_classes"] == 3
    assert summary["total_images"] == 37

    assert summary["train_images"] == 26
    assert summary["val_images"] == 6
    assert summary["test_images"] == 5

    assert (
        summary["train_images"]
        + summary["val_images"]
        + summary["test_images"]
        == 37
    )


def test_no_data_leakage(sample_manifest, tmp_path):
    output_dir = tmp_path / "splits"

    create_splits(sample_manifest, output_dir)

    train = read_split(output_dir / "train.csv")
    val = read_split(output_dir / "val.csv")
    test = read_split(output_dir / "test.csv")

    train_paths = {row["relative_path"] for row in train}
    val_paths = {row["relative_path"] for row in val}
    test_paths = {row["relative_path"] for row in test}

    assert train_paths.isdisjoint(val_paths)
    assert train_paths.isdisjoint(test_paths)
    assert val_paths.isdisjoint(test_paths)

    assert len(train_paths | val_paths | test_paths) == 37


def test_stratified_distribution(sample_manifest, tmp_path):
    output_dir = tmp_path / "splits"

    create_splits(sample_manifest, output_dir)

    for split_name in ("train", "val", "test"):
        rows = read_split(output_dir / f"{split_name}.csv")

        counts = Counter(
            row["class_name"] for row in rows
        )

        assert set(counts) == {
            "pizza",
            "sushi",
            "ginger",
        }

    train = Counter(
        row["class_name"]
        for row in read_split(output_dir / "train.csv")
    )

    assert train == {
        "pizza": 14,
        "sushi": 7,
        "ginger": 5,
    }


def test_reproducibility(sample_manifest, tmp_path):
    first_dir = tmp_path / "run_1"
    second_dir = tmp_path / "run_2"

    create_splits(sample_manifest, first_dir, seed=42)
    create_splits(sample_manifest, second_dir, seed=42)

    filenames = (
        "train.csv",
        "val.csv",
        "test.csv",
        "class_to_index.json",
        "split_summary.json",
    )

    for filename in filenames:
        assert (
            (first_dir / filename).read_bytes()
            == (second_dir / filename).read_bytes()
        )


def test_class_mapping(sample_manifest, tmp_path):
    output_dir = tmp_path / "splits"

    create_splits(sample_manifest, output_dir)

    mapping = json.loads(
        (output_dir / "class_to_index.json").read_text(
            encoding="utf-8"
        )
    )

    assert mapping == {
        "ginger": 0,
        "pizza": 1,
        "sushi": 2,
    }


def test_duplicate_paths_rejected(tmp_path):
    manifest = tmp_path / "duplicate_manifest.csv"

    with manifest.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["class_name", "relative_path"])
        writer.writerow(["pizza", "pizza/a.jpg"])
        writer.writerow(["pizza", "pizza/a.jpg"])

    with pytest.raises(ValueError, match="Duplicate image path"):
        load_manifest(manifest)

