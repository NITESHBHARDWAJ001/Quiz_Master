#!/bin/bash

# Start Celery worker
celery -A celery_worker worker --loglevel=info
