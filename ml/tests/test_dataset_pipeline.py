
import csv
import shutil

import pytest
from PIL import Image

from ml.src.inspect_dataset import (
    inspect_dataset,
    save_reports,
)
from ml.src.create_clean_manifest import create_manifest


@pytest.fixture
def sample_dataset(tmp_path):
    """Create a tiny dataset with known data quality issues."""

    root = tmp_path / "images"

    for name in ("pizza", "sushi", "ginger"):
        (root / name).mkdir(parents=True)

    def save_image(relative_path, color):
        path = root / relative_path
        Image.new("RGB", (16, 16), color).save(path)

    # Original images
    save_image("pizza/a.png", (255, 0, 0))
    save_image("pizza/c.png", (0, 255, 0))
    save_image("sushi/a.png", (0, 0, 255))
    save_image("ginger/a.png", (255, 255, 0))

    # Same-class duplicate
    shutil.copyfile(
        root / "pizza/a.png",
        root / "pizza/b.png",
    )

    # Cross-class duplicate (conflicting labels)
    shutil.copyfile(
        root / "pizza/c.png",
        root / "sushi/b.png",
    )

    # Corrupt image
    (root / "ginger/broken.png").write_bytes(
        b"not a real image"
    )

    return root


def test_dataset_inspection(sample_dataset):
    result = inspect_dataset(sample_dataset)

    assert result["total_classes"] == 3
    assert result["total_valid_images"] == 6
    assert len(result["corrupt_images"]) == 1
    assert len(result["duplicate_groups"]) == 2
    assert result["class_counts"]["pizza"] == 3
    assert result["image_formats"]["PNG"] == 6


def test_clean_manifest(sample_dataset, tmp_path):
    report = inspect_dataset(sample_dataset)

    reports_dir = tmp_path / "reports"
    save_reports(report, reports_dir)

    summary = create_manifest(
        dataset_path=sample_dataset,
        report_path=reports_dir / "dataset_summary.json",
        output_dir=reports_dir,
    )

    assert summary["original_valid_images"] == 6
    assert summary["same_class_copies_excluded"] == 1
    assert summary["ambiguous_cross_class_files_excluded"] == 2
    assert summary["clean_images"] == 3
    assert summary["classes_with_images"] == 3

    manifest_path = reports_dir / "clean_manifest.csv"

    with manifest_path.open(
        newline="", encoding="utf-8"
    ) as file:
        rows = list(csv.DictReader(file))

    retained_paths = {
        row["relative_path"]
        for row in rows
    }

    assert retained_paths == {
        "pizza/a.png",
        "sushi/a.png",
        "ginger/a.png",
    }
