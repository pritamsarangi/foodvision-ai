
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def create_manifest(
    dataset_path: Path,
    report_path: Path,
    output_dir: Path,
) -> dict:
    if not dataset_path.is_dir():
        raise ValueError(f"Dataset not found: {dataset_path}")

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    corrupt = {
        normalize(item["path"])
        for item in report["corrupt_images"]
    }

    same_class_excluded = set()
    cross_class_excluded = set()

    for group in report["duplicate_groups"]:
        paths = sorted(normalize(p) for p in group)
        classes = {path.split("/")[0] for path in paths}

        if len(classes) > 1:
            # Ambiguous labels: exclude the complete group.
            cross_class_excluded.update(paths)
        else:
            # Same label: retain one deterministic copy.
            same_class_excluded.update(paths[1:])

    class_counts = Counter()
    clean_rows = []
    actual_valid_count = 0

    class_dirs = sorted(
        (path for path in dataset_path.iterdir() if path.is_dir()),
        key=lambda p: p.name,
    )

    for class_dir in class_dirs:
        for image_path in sorted(class_dir.iterdir()):
            if not image_path.is_file():
                continue

            if image_path.suffix.lower() not in EXTENSIONS:
                continue

            relative = image_path.relative_to(
                dataset_path
            ).as_posix()

            if relative in corrupt:
                continue

            actual_valid_count += 1

            if relative in cross_class_excluded:
                continue

            if relative in same_class_excluded:
                continue

            clean_rows.append((class_dir.name, relative))
            class_counts[class_dir.name] += 1

    expected_count = report["total_valid_images"]

    if actual_valid_count != expected_count:
        raise ValueError(
            "Dataset no longer matches the inspection report. "
            f"Expected {expected_count}, found {actual_valid_count}. "
            "Run the dataset inspection again."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "clean_manifest.csv"

    with manifest_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["class_name", "relative_path"])
        writer.writerows(clean_rows)

    summary = {
        "original_valid_images": actual_valid_count,
        "same_class_copies_excluded": len(same_class_excluded),
        "ambiguous_cross_class_files_excluded": len(
            cross_class_excluded
        ),
        "clean_images": len(clean_rows),
        "classes_with_images": len(class_counts),
        "class_counts": dict(sorted(class_counts.items())),
    }

    summary_path = output_dir / "clean_manifest_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-path", type=Path, required=True
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("ml/reports/dataset_summary.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("ml/reports"),
    )

    args = parser.parse_args()

    result = create_manifest(
        args.dataset_path,
        args.report_path,
        args.output_dir,
    )

    print("\nFOOD-270 CLEAN MANIFEST")
    print("=" * 45)

    for key, value in result.items():
        if key != "class_counts":
            print(f"{key}: {value}")

    print("\nClean manifest generated successfully.")


if __name__ == "__main__":
    main()
