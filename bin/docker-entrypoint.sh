#!/bin/bash

#set -e

echo "Fixing environtment..."

VIRTUAL_ENV=dstack

#mkdir -p var/logs
#touch var/logs/django.log

if [ $1 == "django" ] 
then
    echo "Starting django server..."
    source activate dstack && python ./src/manage.py migrate
    source activate dstack && python ./src/manage.py runserver 0.0.0.0:8000
    echo "Done..."
fi

if [ $1 == "gunicorn" ] 
then
    echo "Starting gunicorn server..."
    source activate dstack && python ./src/manage.py migrate
    source activate dstack && \
        gunicorn config.wsgi:application \
		--name tpam \
		--bind 0.0.0.0:8000 \
		--workers 3 \
		--log-level=info \
		--log-file=- \
		--pythonpath /home/webapp/src/ \
		--forwarded-allow-ips='*' 
#		"$@"
    echo "Done..."
fi


if [ $1 == "worker" ] 
then
    echo "Starting celery worker..."
    cd src
    source activate dstack && celery worker -A config.celery -l DEBUG -c 2
    echo "Done..."
fi

#exec "$@"
