#!/bin/bash
# Production startup script using Gunicorn

# Set environment variables
export ENVIRONMENT=production

# Number of workers (2 * CPU cores + 1)
WORKERS=${WORKERS:-3}

# Start Gunicorn with Uvicorn workers
exec gunicorn main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --log-level info \
    --access-logfile - \
    --error-logfile -