
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp"
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def inspect_dataset(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError(f"Dataset directory not found: {root}")

    class_dirs = sorted(
        (path for path in root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
    )

    if not class_dirs:
        raise ValueError("No class folders found")

    class_counts = {}
    formats = Counter()
    widths = []
    heights = []
    corrupt = []
    unsupported = []
    hashes = defaultdict(list)

    for class_dir in class_dirs:
        valid_count = 0

        for path in sorted(class_dir.iterdir()):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                unsupported.append(str(path.relative_to(root)))
                continue

            relative_path = str(path.relative_to(root))

            try:
                with Image.open(path) as image:
                    image.verify()

                with Image.open(path) as image:
                    image.load()
                    width, height = image.size
                    image_format = image.format or "unknown"

                widths.append(width)
                heights.append(height)
                formats[image_format] += 1
                hashes[sha256_file(path)].append(relative_path)
                valid_count += 1

            except (
                OSError,
                ValueError,
                UnidentifiedImageError,
            ) as error:
                corrupt.append({
                    "path": relative_path,
                    "reason": str(error),
                })

        class_counts[class_dir.name] = valid_count
        print(f"{class_dir.name}: {valid_count} valid images", flush=True)

    duplicates = [
        paths
        for paths in hashes.values()
        if len(paths) > 1
    ]

    total_valid = sum(class_counts.values())

    return {
        "total_classes": len(class_dirs),
        "total_valid_images": total_valid,
        "class_counts": class_counts,
        "image_formats": dict(formats),
        "image_dimensions": {
            "min_width": min(widths) if widths else None,
            "max_width": max(widths) if widths else None,
            "min_height": min(heights) if heights else None,
            "max_height": max(heights) if heights else None,
        },
        "corrupt_images": corrupt,
        "unsupported_files": unsupported,
        "duplicate_groups": duplicates,
    }


def save_reports(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "dataset_summary.json"
    summary_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    class_counts_path = output_dir / "class_distribution.csv"

    with class_counts_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["class_name", "valid_images"])

        for class_name, count in sorted(
            result["class_counts"].items()
        ):
            writer.writerow([class_name, count])

    print(f"\nReports saved to: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("ml/reports"),
    )

    args = parser.parse_args()

    result = inspect_dataset(args.dataset_path.resolve())

    save_reports(result, args.output_dir)

    print("\nDataset inspection complete!")
    print("Classes:", result["total_classes"])
    print("Valid images:", result["total_valid_images"])
    print("Corrupt images:", len(result["corrupt_images"]))
    print("Duplicate groups:", len(result["duplicate_groups"]))


if __name__ == "__main__":
    main()
