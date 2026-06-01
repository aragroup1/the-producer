web: cd services/api-gateway && uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd services/api-gateway && celery -A shared.celery_config worker --loglevel=info --concurrency=2
beat: cd services/api-gateway && celery -A shared.celery_config beat --loglevel=info
