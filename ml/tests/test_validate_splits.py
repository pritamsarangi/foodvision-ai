
import csv
import json

import pytest

from ml.src.validate_splits import validate_splits


def prepare_inputs(tmp_path, duplicate_groups):
    manifest = tmp_path / "clean_manifest.csv"
    report = tmp_path / "dataset_summary.json"
    splits = tmp_path / "splits"
    splits.mkdir()

    images = [
        ("pizza/a.jpg", "pizza"),
        ("sushi/a.jpg", "sushi"),
    ]

    with manifest.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["relative_path", "class_name"])
        writer.writerows(images)

    for name, rows in {
        "train": [images[0]],
        "val": [images[1]],
        "test": [],
    }.items():
        with (splits / f"{name}.csv").open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["relative_path", "class_name"])
            writer.writerows(rows)

    report.write_text(
        json.dumps({"duplicate_groups": duplicate_groups}),
        encoding="utf-8",
    )

    return report, manifest, splits


def test_valid_splits(tmp_path):
    paths = prepare_inputs(
        tmp_path,
        [["pizza/a.jpg", "pizza/unused.jpg"]],
    )

    result = validate_splits(*paths)

    assert result["total_images"] == 2
    assert result["duplicate_conflicts"] == 0


def test_duplicate_content_rejected(tmp_path):
    paths = prepare_inputs(
        tmp_path,
        [["pizza/a.jpg", "sushi/a.jpg"]],
    )

    with pytest.raises(
        ValueError, match="Exact duplicate content"
    ):
        validate_splits(*paths)


def test_cross_class_conflict_rejected(tmp_path):
    paths = prepare_inputs(
        tmp_path,
        [["pizza/a.jpg", "sushi/unused.jpg"]],
    )

    with pytest.raises(
        ValueError, match="Cross-class duplicate"
    ):
        validate_splits(*paths)
