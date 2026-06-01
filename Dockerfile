FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from all services
COPY services/api-gateway/requirements.txt ./requirements-gateway.txt
COPY services/marketing-agent/requirements.txt ./requirements-marketing.txt
COPY services/sound-engine/requirements.txt ./requirements-sound.txt
COPY services/composition-engine/requirements.txt ./requirements-composition.txt
COPY services/mixing-engine/requirements.txt ./requirements-mixing.txt
COPY services/mastering-engine/requirements.txt ./requirements-mastering.txt
COPY services/export-pipeline/requirements.txt ./requirements-export.txt
COPY services/quality-scoring/requirements.txt ./requirements-qc.txt
COPY services/shopify-integration/requirements.txt ./requirements-shopify.txt
COPY services/trend-research/requirements.txt ./requirements-trends.txt
COPY services/adaptive-learning/requirements.txt ./requirements-learning.txt

# Combine and install all dependencies
RUN pip install --no-cache-dir -r requirements-gateway.txt && \
    pip install --no-cache-dir -r requirements-marketing.txt && \
    pip install --no-cache-dir -r requirements-sound.txt && \
    pip install --no-cache-dir -r requirements-composition.txt && \
    pip install --no-cache-dir -r requirements-mixing.txt && \
    pip install --no-cache-dir -r requirements-mastering.txt && \
    pip install --no-cache-dir -r requirements-export.txt && \
    pip install --no-cache-dir -r requirements-qc.txt && \
    pip install --no-cache-dir -r requirements-shopify.txt && \
    pip install --no-cache-dir -r requirements-trends.txt && \
    pip install --no-cache-dir -r requirements-learning.txt

# Copy all service code
COPY services/ ./services/
COPY shared/ ./shared/
COPY scripts/ ./scripts/

# Create output directories
RUN mkdir -p /app/output/beats /app/output/stems /app/output/previews /app/output/midi /app/output/videos /app/output/thumbnails

# Set Python path to include all services
ENV PYTHONPATH=/app:/app/services/api-gateway:/app/services/marketing-agent:/app/services/sound-engine:/app/services/composition-engine:/app/services/mixing-engine:/app/services/mastering-engine:/app/services/export-pipeline:/app/services/quality-scoring:/app/services/shopify-integration:/app/services/trend-research:/app/services/adaptive-learning:/app/services/render-queue

# Expose port
EXPOSE 8000

# Run API gateway - Railway sets PORT env var
CMD uvicorn services.api-gateway.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
