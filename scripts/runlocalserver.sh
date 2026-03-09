#!/bin/sh
set -e


echo "Running migrations..."
python manage.py migrate

python manage.py runserver 0.0.0.0:8000
