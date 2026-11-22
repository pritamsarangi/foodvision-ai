FROM python:3.9-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for psycopg2 and Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and required ML artifacts
COPY backend/ .
COPY ml/data/splits/class_to_index.json /app/ml/data/splits/class_to_index.json
COPY ml/experiments/efficientnet_b0/best_finetuned_weights.h5 /app/ml/experiments/efficientnet_b0/best_finetuned_weights.h5

# Expose port and run Uvicorn
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]