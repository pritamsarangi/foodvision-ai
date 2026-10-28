
import argparse
import json
from pathlib import Path
from statistics import mean, median

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def visualize_dataset(summary_path: Path, output_dir: Path):
    with summary_path.open("r", encoding="utf-8") as file:
        summary = json.load(file)

    class_counts = summary["class_counts"]

    if not class_counts:
        raise ValueError("No classes found in the summary.")

    output_dir.mkdir(parents=True, exist_ok=True)

    sorted_classes = sorted(
        class_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    counts = list(class_counts.values())

    statistics = {
        "total_classes": len(class_counts),
        "total_images": sum(counts),
        "minimum_images_per_class": min(counts),
        "maximum_images_per_class": max(counts),
        "mean_images_per_class": round(mean(counts), 2),
        "median_images_per_class": median(counts),
        "classes_below_100": sum(c < 100 for c in counts),
        "classes_below_500": sum(c < 500 for c in counts),
        "top_15_classes": sorted_classes[:15],
        "bottom_15_classes": sorted_classes[-15:],
    }

    # Plot 1: Top 15 classes
    top = sorted_classes[:15]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(
        [item[0] for item in reversed(top)],
        [item[1] for item in reversed(top)],
    )
    ax.set_title("Top 15 Food Categories by Image Count")
    ax.set_xlabel("Number of Images")
    fig.tight_layout()
    fig.savefig(output_dir / "top_15_classes.png", dpi=150)
    plt.close(fig)

    # Plot 2: Bottom 15 classes
    bottom = sorted(
        class_counts.items(),
        key=lambda item: item[1],
    )[:15]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(
        [item[0] for item in reversed(bottom)],
        [item[1] for item in reversed(bottom)],
    )
    ax.set_title("Bottom 15 Food Categories by Image Count")
    ax.set_xlabel("Number of Images")
    fig.tight_layout()
    fig.savefig(output_dir / "bottom_15_classes.png", dpi=150)
    plt.close(fig)

    # Plot 3: Distribution across all classes
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(counts, bins=30, edgecolor="black")
    ax.set_title("Food-270 Class Distribution")
    ax.set_xlabel("Images per Class")
    ax.set_ylabel("Number of Classes")
    fig.tight_layout()
    fig.savefig(output_dir / "class_distribution.png", dpi=150)
    plt.close(fig)

    stats_path = output_dir / "eda_statistics.json"

    stats_path.write_text(
        json.dumps(statistics, indent=2),
        encoding="utf-8",
    )

    print("\nFOOD-270 EDA RESULTS")
    print("=" * 45)

    for key, value in statistics.items():
        if key not in {"top_15_classes", "bottom_15_classes"}:
            print(f"{key}: {value}")

    print("\nTop 15 classes:")
    for name, count in sorted_classes[:15]:
        print(f"  {name}: {count}")

    print("\nBottom 15 classes:")
    for name, count in bottom:
        print(f"  {name}: {count}")

    print(f"\nReports saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--summary-path",
        type=Path,
        default=Path("ml/reports/clean_manifest_summary.json"),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("ml/reports/figures"),
    )

    args = parser.parse_args()

    visualize_dataset(args.summary_path, args.output_dir)


if __name__ == "__main__":
    main()
