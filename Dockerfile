# Production Dockerfile for BSMA GeoAI FastAPI Backend
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for GDAL/geospatial operations
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize DB tables on container startup
RUN python -m backend.init_db

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
