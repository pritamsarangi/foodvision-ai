
import argparse
import csv
import json
from pathlib import Path


SPLIT_NAMES = ("train", "val", "test")


def normalize(path):
    return path.replace("\\", "/")


def validate_splits(report_path, manifest_path, splits_dir):
    # Load the original duplicate analysis.
    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    # Load the cleaned manifest.
    manifest = {}

    with manifest_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        for row in csv.DictReader(file):
            path = normalize(row["relative_path"])
            if path in manifest:
                raise ValueError(f"Duplicate manifest path: {path}")
            manifest[path] = row["class_name"]

    # Load the actual train/val/test partitions.
    assignments = {}
    split_counts = {}

    for split_name in SPLIT_NAMES:
        path = splits_dir / f"{split_name}.csv"

        with path.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))

        split_counts[split_name] = len(rows)

        for row in rows:
            relative = normalize(row["relative_path"])

            if relative in assignments:
                raise ValueError(
                    f"Path appears more than once: {relative}"
                )

            assignments[relative] = (
                split_name,
                row["class_name"],
            )

    # Every cleaned image must appear exactly once.
    if set(assignments) != set(manifest):
        raise ValueError(
            "Split paths do not match the clean manifest"
        )

    for path, (_, label) in assignments.items():
        if label != manifest[path]:
            raise ValueError(
                f"Class label mismatch: {path}"
            )

    # Validate using the prior SHA-256 duplicate audit.
    groups_checked = 0

    for group in report["duplicate_groups"]:
        paths = [normalize(path) for path in group]

        retained = [
            path for path in paths if path in assignments
        ]

        # A cleaned dataset must retain at most one
        # file from any exact-duplicate group.
        if len(retained) > 1:
            raise ValueError(
                f"Exact duplicate content retained: {retained}"
            )

        # Cross-class conflicts must be excluded entirely.
        classes = {
            path.split("/")[0] for path in paths
        }

        if len(classes) > 1 and retained:
            raise ValueError(
                f"Cross-class duplicate retained: {retained}"
            )

        groups_checked += 1

    summary = {
        "total_images": len(assignments),
        "train_images": split_counts["train"],
        "val_images": split_counts["val"],
        "test_images": split_counts["test"],
        "duplicate_groups_checked": groups_checked,
        "duplicate_conflicts": 0,
    }

    return summary


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("ml/reports/dataset_summary.json"),
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("ml/reports/clean_manifest.csv"),
    )
    parser.add_argument(
        "--splits-dir",
        type=Path,
        default=Path("ml/reports/splits"),
    )

    args = parser.parse_args()

    summary = validate_splits(
        args.report_path,
        args.manifest_path,
        args.splits_dir,
    )

    print("\nFOOD-270 SPLIT VALIDATION")
    print("=" * 40)

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nSplit validation successful!")


if __name__ == "__main__":
    main()
