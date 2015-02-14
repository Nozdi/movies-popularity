#!/usr/bin/env bash

cd process
./repair.py fromHtml.csv > repaired.csv
./relevant.py
rm repaired.csv
cd ..
./collect.py
celery -A tasks worker &
CELERY_PID=$!
./results.py
kill $CELERY_PID
