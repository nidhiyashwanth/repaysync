#!/bin/sh

# Wait for the database to be ready
echo "Waiting for PostgreSQL to start..."
while ! pg_isready -h db -U repaysync -q; do
    sleep 1
done
echo "PostgreSQL started"

# Apply database migrations with a custom approach to handle the problematic migrations
echo "Running migrations..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate admin

# Apply user migrations with specific versions
python manage.py migrate users 0001
python manage.py migrate users 0002
python manage.py migrate users 0003
python manage.py migrate users 0004
python manage.py migrate users 0005

# Apply customers migrations with specific versions
python manage.py migrate customers 0001
python manage.py migrate customers 0002
python manage.py migrate customers 0003

# Apply other app migrations
python manage.py migrate interactions
python manage.py migrate loans
python manage.py migrate api
python manage.py migrate core

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000 