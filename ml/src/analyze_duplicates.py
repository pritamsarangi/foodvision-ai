
import json
from pathlib import Path
from collections import Counter


REPORT_PATH = Path("ml/reports/dataset_summary.json")


def main():
    with REPORT_PATH.open("r", encoding="utf-8") as file:
        report = json.load(file)

    groups = report["duplicate_groups"]

    same_class_groups = 0
    cross_class_groups = 0
    redundant_copies = 0
    cross_class_examples = []

    for group in groups:
        classes = {
            Path(image_path).parts[0]
            for image_path in group
        }

        redundant_copies += len(group) - 1

        if len(classes) == 1:
            same_class_groups += 1
        else:
            cross_class_groups += 1
            if len(cross_class_examples) < 10:
                cross_class_examples.append(group)

    print("\nFOOD-270 DUPLICATE ANALYSIS")
    print("=" * 45)
    print(f"Total duplicate groups: {len(groups)}")
    print(f"Same-class groups: {same_class_groups}")
    print(f"Cross-class groups: {cross_class_groups}")
    print(f"Redundant file copies: {redundant_copies}")

    print("\nCross-class duplicate examples:")

    for group in cross_class_examples:
        print("-" * 45)
        for path in group:
            print(path)


if __name__ == "__main__":
    main()
