
# FoodVision AI — FastAPI Backend

FastAPI backend for the FoodVision AI food image classification application.

## Features

- Food classification using fine-tuned EfficientNet-B0
- 270 food categories
- Top-5 prediction results with confidence scores
- Prediction history stored in Neon PostgreSQL
- JPEG, PNG and WebP image uploads (maximum 10 MB)
- Flutter Web CORS support
- Automated API tests

## Requirements

- Python 3.9
- PostgreSQL database (Neon)
- Fine-tuned EfficientNet-B0 checkpoint

## Local Setup (Windows)

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Use your own Neon PostgreSQL connection string. Never commit `.env`.

The inference service loads the model checkpoint from:

```text
ml/experiments/efficientnet_b0/best_finetuned_weights.h5
```

And the 270-class mapping from:

```text
ml/data/splits/class_to_index.json
```

Both files are included in the repository.

## Run the API

From the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- API documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/api/v1/health

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Health status |
| POST | `/api/v1/predict` | Upload an image and classify food |
| GET | `/api/v1/predictions` | Get 100 most recent predictions |
| GET | `/api/v1/predictions/{prediction_id}` | Retrieve a prediction |

## Model Performance

Fine-tuned EfficientNet-B0 evaluated on 33,824 test images:

- Top-1 accuracy: 80.40%
- Top-5 accuracy: 94.08%
- Number of food classes: 270
- Model version: `efficientnet-b0-finetuned-v1`

## Testing

From the backend directory:

```powershell
python -m pytest tests -v
```

The test suite mocks inference and database access to avoid external requests.

## Notes

- The API uses real model inference, not mock predictions.
- Successful predictions are saved to Neon PostgreSQL.
- Database errors return HTTP 503.
- Unsupported image types return HTTP 415.
- Invalid image data returns HTTP 400.
- Oversized images return HTTP 413.
- CORS is configured for local Flutter Web development.
