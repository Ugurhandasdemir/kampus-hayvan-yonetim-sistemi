#!/bin/bash
set -e

echo "BUILD START"

python3.12 -m pip install --break-system-packages --upgrade pip
python3.12 -m pip install --break-system-packages -r requirements.txt

python3.12 manage.py collectstatic --noinput --clear

if [ -n "$RUN_MIGRATIONS" ]; then
  python3.12 manage.py migrate --noinput
fi

echo "BUILD END"
