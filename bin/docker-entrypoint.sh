#!/bin/bash

#set -e

echo "Fixing environtment..."

if [ $1 == "django" ] 
then
    echo "Starting django server..."
    source activate ${VIRTUAL_ENV} && python ./src/manage.py migrate
    source activate ${VIRTUAL_ENV} && python ./src/manage.py runserver 0.0.0.0:8000
fi

if [ $1 == "gunicorn" ] 
then
    echo "Starting gunicorn server..."
    source activate ${VIRTUAL_ENV} && python ./src/manage.py migrate
    source activate ${VIRTUAL_ENV} && \
        gunicorn config.wsgi:application \
		--name ${VIRTUAL_ENV} \
		--bind 0.0.0.0:8000 \
		--workers 3 \
		--log-level=info \
		--log-file=- \
		--pythonpath /home/webapp/src/ \
		--forwarded-allow-ips='*'
fi


if [ $1 == "worker" ] 
then
    echo "Starting celery worker..."
    cd src
    source activate ${VIRTUAL_ENV} && celery worker -A config.celery -l DEBUG -c 2
fi

echo "Done..."

#exec "$@"
