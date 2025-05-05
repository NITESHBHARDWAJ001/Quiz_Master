#!/bin/bash

# Start Celery Beat for scheduled tasks
celery -A celery_worker beat --loglevel=info
