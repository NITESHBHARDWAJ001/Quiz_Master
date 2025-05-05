#!/bin/bash

# Start Flower for monitoring Celery tasks
celery -A celery_worker flower --port=5555
