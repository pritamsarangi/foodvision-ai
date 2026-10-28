
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path, PurePosixPath


TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
SEED = 42


def load_manifest(manifest_path: Path) -> dict:
    class_images = defaultdict(list)
    seen_paths = set()

    with manifest_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        required = {"class_name", "relative_path"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Invalid manifest columns")

        for row in reader:
            class_name = row["class_name"]
            relative_path = row["relative_path"].replace("\\", "/")

            parts = PurePosixPath(relative_path).parts

            if (
                not class_name
                or not relative_path
                or not parts
                or parts[0] != class_name
                or ".." in parts
                or relative_path.startswith("/")
            ):
                raise ValueError(
                    f"Invalid manifest entry: {relative_path}"
                )

            if relative_path in seen_paths:
                raise ValueError(
                    f"Duplicate image path: {relative_path}"
                )

            seen_paths.add(relative_path)
            class_images[class_name].append(relative_path)

    if not class_images:
        raise ValueError("Manifest contains no images")

    return class_images


def save_csv(path: Path, rows: list):
    with path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ["relative_path", "class_name", "class_index"]
        )
        writer.writerows(rows)


def create_splits(
    manifest_path: Path,
    output_dir: Path,
    seed: int = SEED,
) -> dict:
    class_images = load_manifest(manifest_path)

    class_names = sorted(class_images)
    class_to_index = {
        name: index
        for index, name in enumerate(class_names)
    }

    rng = random.Random(seed)

    splits = {
        "train": [],
        "val": [],
        "test": [],
    }

    per_class_counts = {}

    for class_name in class_names:
        images = sorted(class_images[class_name])
        rng.shuffle(images)

        total = len(images)

        n_train = round(total * TRAIN_RATIO)
        n_val = round(total * VAL_RATIO)
        n_test = total - n_train - n_val

        if min(n_train, n_val, n_test) < 1:
            raise ValueError(
                f"Too few images in class: {class_name}"
            )

        partitions = {
            "train": images[:n_train],
            "val": images[n_train:n_train + n_val],
            "test": images[n_train + n_val:],
        }

        for split_name, paths in partitions.items():
            for relative_path in paths:
                splits[split_name].append(
                    (
                        relative_path,
                        class_name,
                        class_to_index[class_name],
                    )
                )

        per_class_counts[class_name] = {
            "train": n_train,
            "val": n_val,
            "test": n_test,
        }

    train_paths = {row[0] for row in splits["train"]}
    val_paths = {row[0] for row in splits["val"]}
    test_paths = {row[0] for row in splits["test"]}

    assert train_paths.isdisjoint(val_paths)
    assert train_paths.isdisjoint(test_paths)
    assert val_paths.isdisjoint(test_paths)

    total_images = sum(len(rows) for rows in splits.values())

    assert len(train_paths | val_paths | test_paths) == total_images
    assert total_images == sum(map(len, class_images.values()))

    output_dir.mkdir(parents=True, exist_ok=True)

    for name, rows in splits.items():
        save_csv(output_dir / f"{name}.csv", rows)

    (output_dir / "class_to_index.json").write_text(
        json.dumps(class_to_index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    summary = {
        "seed": seed,
        "train_ratio": TRAIN_RATIO,
        "val_ratio": VAL_RATIO,
        "test_ratio": 1 - TRAIN_RATIO - VAL_RATIO,
        "total_classes": len(class_names),
        "total_images": total_images,
        "train_images": len(splits["train"]),
        "val_images": len(splits["val"]),
        "test_images": len(splits["test"]),
        "per_class_counts": per_class_counts,
    }

    (output_dir / "split_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("ml/reports/clean_manifest.csv"),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("ml/reports/splits"),
    )

    args = parser.parse_args()

    summary = create_splits(
        manifest_path=args.manifest_path,
        output_dir=args.output_dir,
    )

    print("\nFOOD-270 DATASET SPLIT")
    print("=" * 40)

    for key, value in summary.items():
        if key != "per_class_counts":
            print(f"{key}: {value}")

    print("\nSplitting completed successfully!")


if __name__ == "__main__":
    main()
