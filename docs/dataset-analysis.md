
# FoodVision AI — Dataset Analysis

## 1. Dataset Overview

- Dataset: Food-270
- Source: https://www.kaggle.com/datasets/berkerveyik/food-270-dataset
- Task: Multiclass food image classification
- Original valid images: 229,245
- Food categories: 270
- Corrupted images detected: 0

## 2. Dataset Structure

The dataset uses a class-first directory structure.

Each food category has a separate folder containing its images.

No predefined train, validation, or test directories
were found in the extracted dataset.

## 3. Data Quality Analysis

SHA-256 hashing identified:

- Total duplicate groups: 3,371
- Same-class duplicate groups: 3,072
- Cross-class duplicate groups: 299
- Redundant file copies: 3,509

Cross-class duplicates may indicate ambiguous or
inconsistent labels.

## 4. Cleaning Strategy

The original dataset was preserved without modification.

A reproducible CSV manifest was created using these rules:

1. Exclude corrupted or unsupported images.
2. Retain one copy of identical same-class images.
3. Exclude cross-class duplicate groups pending label review.

Cleaning results:

- Same-class copies excluded: 3,177
- Cross-class files excluded: 631
- Final retained images: 225,437
- Remaining categories: 270

## 5. Exploratory Data Analysis

- Mean images per class: 834.95
- Median images per class: 1,000
- Minimum images per class: 65
- Maximum images per class: 3,034
- Classes with fewer than 100 images: 12
- Classes with fewer than 500 images: 53

Smallest category: ginger (65 images)
Largest category: pizza (3,034 images)

The dataset contains significant class imbalance.

## 6. Planned Model Experiments

Two CNN approaches will be evaluated:

1. Custom CNN trained from scratch.
2. EfficientNet-B0 using transfer learning.

Both models will use consistent cleaned data
and train/validation/test partitions.

Evaluation will include:

- Top-1 accuracy
- Top-5 accuracy
- Macro F1-score
- Precision and recall
- Confusion matrix
- Inference latency
- Model size

## 7. Limitations

- SHA-256 detects identical files, not perceptually similar images.
- Cross-class duplicates were excluded conservatively.
- Some classes have substantially fewer training examples.
- Data splitting and model training have not yet been performed.
- No model performance results are available yet.

## 8. Next Steps

- Create a reproducible, leakage-aware data split.
- Implement a TensorFlow data-loading pipeline.
- Train a custom CNN baseline.
- Train an EfficientNet-B0 transfer-learning model.
- Compare both architectures.
