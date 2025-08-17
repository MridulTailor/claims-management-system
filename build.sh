#!/usr/bin/env bash
# exit on error
set -o errexit

# Install pipenv if not available
pip install pipenv

# Install dependencies
pipenv install --deploy

# Collect static files and run migrations
pipenv run python manage.py collectstatic --no-input
pipenv run python manage.py migrate
