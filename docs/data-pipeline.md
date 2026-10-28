
# FoodVision AI — Data Pipeline

## Overview

This pipeline prepares the cleaned Food-270 dataset
for image classification using TensorFlow.

## Dataset

- Total images: 225,437
- Classes: 270
- Train: 157,800 images
- Validation: 33,813 images
- Test: 33,824 images
- Split seed: 42

## Data Splitting

The dataset uses class-stratified splitting:

- 70% training
- 15% validation
- 15% testing

Each category is split separately.

The same partitions will be used for Custom CNN
and EfficientNet-B0 experiments.

## Leakage Prevention

Validation checks:

- No overlapping image paths
- All cleaned images assigned once
- Consistent class labels
- No known exact-duplicate conflicts

The validation uses the previously generated
SHA-256 audit.

Near-duplicate photographs and unrecognized
label errors are not fully ruled out.

## TensorFlow Data Loading

- Framework: TensorFlow 2.10.1
- Image size: 224 × 224 RGB
- Initial batch size: 8
- Output image dtype: float32
- Output pixel range: 0–255
- Training data shuffled
- Validation/test data not shuffled
- Two parallel image-loading calls
- Prefetch buffer: 1 batch

## Supported Image Formats

- JPEG
- PNG
- BMP
- WebP through Pillow fallback

## Model Preprocessing

The data loader outputs pixels in the 0–255 range.

Custom CNN will use a Rescaling layer.

EfficientNet-B0 will use its built-in preprocessing
and must not receive duplicate rescaling.

## Running the Pipeline

Generate splits:

    python ml/src/create_splits.py

Validate splits:

    python ml/src/validate_splits.py

Run the smoke test:

    python -m ml.src.smoke_test_tf_data --dataset-root "PATH_TO_IMAGES"

Run unit tests:

    python -m pytest ml/tests -v

## Limitations

- The source dataset must exist locally.
- Generated CSV files remain excluded from Git.
- The GPU smoke test checks sample batches, not
  every image in the dataset.
- Model training throughput has not been benchmarked.
- The class-to-index mapping must be preserved
  with exported models for consistent inference.
