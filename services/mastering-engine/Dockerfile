FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY shared/ ./shared/

CMD ["celery", "-A", "app.tasks", "worker", "-Q", "master", "-c", "2", "--loglevel=info"]
