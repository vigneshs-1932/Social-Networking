#!/bin/sh

# Wait for the PostgreSQL database to be available
while ! nc -z db 5432; do
  echo "Waiting for PostgreSQL database..."
  sleep 1
done

# Navigate to the Django project directory
cd /Social-Networking

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
