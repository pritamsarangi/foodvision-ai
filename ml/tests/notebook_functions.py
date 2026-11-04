"""Load notebook-defined pipeline functions without executing notebook workflows.

Notebook functions are the source of truth. Only selected function definitions and
safe constants are compiled; no training, filesystem scans, or notebook top-level
cells are executed. This is designed for the notebook-first FoodVision project.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import random
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

import numpy as np
from PIL import Image, UnidentifiedImageError

_ROOT = Path(__file__).resolve().parents[2]
_EDA = _ROOT / "ml/notebooks/00_food270_eda_and_split_audit_consolidated.ipynb"
_CNN = _ROOT / "ml/notebooks/01_custom_cnn.ipynb"


def _functions_from_notebook(path: Path, names: set[str], namespace: dict):
    if not path.exists():
        raise FileNotFoundError(f"Required notebook not found: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    found = set()
    for cell in document["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        selected = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
                selected.append(node)
                found.add(node.name)
        if selected:
            isolated = ast.Module(body=selected, type_ignores=[])
            ast.fix_missing_locations(isolated)
            exec(compile(isolated, str(path), "exec"), namespace)
    missing = names - found
    if missing:
        raise RuntimeError(f"Notebook {path.name} missing function(s): {sorted(missing)}")
    return namespace


_eda_context = {
    "__builtins__": __builtins__,
    "Path": Path,
    "PurePosixPath": PurePosixPath,
    "csv": csv,
    "json": json,
    "random": random,
    "hashlib": hashlib,
    "Counter": Counter,
    "defaultdict": defaultdict,
    "Image": Image,
    "UnidentifiedImageError": UnidentifiedImageError,
    "SUPPORTED_EXTENSIONS": {".jpg", ".jpeg", ".png", ".webp", ".bmp"},
    "EXTENSIONS": {".jpg", ".jpeg", ".png", ".webp", ".bmp"},
    "TRAIN_RATIO": 0.70,
    "VAL_RATIO": 0.15,
    "SEED": 42,
    "SPLIT_NAMES": ("train", "val", "test"),
}
_eda_names = {
    "sha256_file", "inspect_dataset", "save_reports", "normalize",
    "create_manifest", "load_manifest", "save_csv", "create_splits", "validate_splits",
}
_functions_from_notebook(_EDA, _eda_names, _eda_context)
inspect_dataset = _eda_context["inspect_dataset"]
save_reports = _eda_context["save_reports"]
create_manifest = _eda_context["create_manifest"]
create_splits = _eda_context["create_splits"]
load_manifest = _eda_context["load_manifest"]
validate_splits = _eda_context["validate_splits"]


def build_dataset(dataset_root: Path, split_path: Path, batch_size: int = 8,
                  image_size: tuple[int, int] = (224, 224),
                  training: bool = False, seed: int = 42):
    """Small test adapter using the Custom CNN notebook's actual image decoder.

    This adapter handles arbitrary temporary split CSVs, while read_image and
    decode_webp come from the Custom CNN notebook itself.
    """
    import tensorflow as tf

    context = {
        "__builtins__": __builtins__,
        "tf": tf,
        "np": np,
        "Image": Image,
        "io": io,
        "IMAGE_SIZE": image_size,
    }
    _functions_from_notebook(_CNN, {"decode_webp", "read_image"}, context)

    dataset_root = Path(dataset_root)
    split_path = Path(split_path)
    paths, labels = [], []
    with split_path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            relative = PurePosixPath(row["relative_path"].replace("\\", "/"))
            paths.append(str(dataset_root.joinpath(*relative.parts)))
            labels.append(int(row["class_index"]))
    if not paths:
        raise ValueError("Split contains no images")
    if training:
        examples = list(zip(paths, labels))
        random.Random(seed).shuffle(examples)
        paths, labels = zip(*examples)
    ds = tf.data.Dataset.from_tensor_slices((list(paths), list(labels)))
    if training:
        ds = ds.shuffle(min(2048, len(paths)), seed=seed,
                        reshuffle_each_iteration=True)
    ds = ds.map(context["read_image"], num_parallel_calls=2)
    return ds.batch(batch_size).prefetch(1)
