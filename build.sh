#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pipenv install --deploy

# Install Node.js dependencies and build Tailwind CSS
pipenv run python manage.py tailwind install --no-input
pipenv run python manage.py tailwind build --no-input

# Collect static files (this will now include compiled Tailwind CSS)
pipenv run python manage.py collectstatic --no-input

# Run database migrations
pipenv run python manage.py migrate

# Load CSV data (FIXED COMMAND NAME)
pipenv run python manage.py load_claims_data