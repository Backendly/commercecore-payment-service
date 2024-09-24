web: uvicorn api.main:app --host=0.0.0.0 --port=${PORT:-8000}
worker: celery -A celery_config.celery_app worker --loglevel=info --concurrency=2