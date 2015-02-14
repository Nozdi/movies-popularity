#!/usr/bin/env bash

cd process
./repair.py fromHtml.csv > repaired.csv
./relevant.py
