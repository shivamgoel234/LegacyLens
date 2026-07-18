#!/usr/bin/env bash
# Render build script — runs once before the web process starts.
# Do NOT put secrets here. All secrets come from Render environment variables.

set -o errexit   # Exit immediately if any command fails

echo "=== Installing Python dependencies ==="
pip install -r requirements/base.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== Running database migrations ==="
python manage.py migrate --no-input

echo "=== Build complete ==="
