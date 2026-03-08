#!/bin/sh
set -e

# Espera a que la base de datos esté lista
until python manage.py showmigrations >/dev/null 2>&1; do
    echo "Esperando a la base de datos..."
    sleep 1
done

python3 manage.py migrate
python3 manage.py collectstatic --noinput
python3 manage.py createsuperuser --noinput || echo "Superuser ya existe o no se pudo crear"

gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120