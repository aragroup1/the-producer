FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY tests/ ./tests/

# Create output directories
RUN mkdir -p /app/output/videos /app/output/thumbnails /app/output/videos/shorts /app/credentials

# Expose port
EXPOSE 8005

# Run service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
