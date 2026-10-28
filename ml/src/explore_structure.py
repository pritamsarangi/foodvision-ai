
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=Path, required=True)
    args = parser.parse_args()

    root = args.dataset_path.expanduser().resolve()

    if not root.is_dir():
        raise SystemExit(f"Dataset directory not found: {root}")

    print(f"\nDataset root: {root}")

    def show_children(folder: Path, level: int = 0):
        children = sorted(folder.iterdir(), key=lambda p: p.name.lower())
        dirs = [p for p in children if p.is_dir()]
        files = [p for p in children if p.is_file()]

        indent = "  " * level
        print(f"{indent}{folder.name}/ "
              f"({len(dirs)} folders, {len(files)} files)")

        for file in files[:8]:
            print(f"{indent}  {file.name}")

        for directory in dirs[:12]:
            print(f"{indent}  {directory.name}/")

        if level == 0:
            for directory in dirs[:8]:
                show_children(directory, level + 1)

    show_children(root)


if __name__ == "__main__":
    main()
