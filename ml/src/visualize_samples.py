
import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from PIL import Image, ImageOps


def create_sample_gallery(
    dataset_path: Path,
    manifest_path: Path,
    output_path: Path,
    seed: int = 42,
):
    class_images = defaultdict(list)

    with manifest_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            class_images[row["class_name"]].append(
                row["relative_path"]
            )

    rng = random.Random(seed)

    available_classes = sorted(class_images)
    selected_classes = rng.sample(
        available_classes,
        min(12, len(available_classes)),
    )

    fig, axes = plt.subplots(3, 4, figsize=(14, 11))
    axes = axes.flatten()

    for ax in axes:
        ax.axis("off")

    for ax, class_name in zip(axes, selected_classes):
        relative_path = rng.choice(
            sorted(class_images[class_name])
        )

        image_path = dataset_path / relative_path

        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            image.thumbnail((350, 350))

            ax.imshow(image)

        ax.set_title(
            class_name.replace("_", " "),
            fontsize=11,
        )
        ax.axis("off")

    fig.suptitle(
        "Food-270: Sample Images from Clean Manifest",
        fontsize=16,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.96))

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Gallery saved to: {output_path}")
    print(f"Classes shown: {len(selected_classes)}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-path",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("ml/reports/clean_manifest.csv"),
    )

    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path(
            "ml/reports/figures/sample_gallery.png"
        ),
    )

    args = parser.parse_args()

    create_sample_gallery(
        dataset_path=args.dataset_path,
        manifest_path=args.manifest_path,
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()
