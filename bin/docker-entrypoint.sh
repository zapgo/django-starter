#!/bin/bash

if [ $1 == "gunicorn" ] 
then
    echo "Starting gunicorn server..."
    python manage.py migrate
    gunicorn config.wsgi:application \
		--name ${PROJECT_NAME} \
		--bind 0.0.0.0:8000 \
		--workers 3 \
		--log-level=info \
		--log-file=- \
		--pythonpath /app/ \
		--forwarded-allow-ips='*'
fi
