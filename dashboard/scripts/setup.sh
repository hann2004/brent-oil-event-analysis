#!/bin/bash
echo "Brent Oil Analysis Dashboard - Setup"

cd /home/nabi/brent-oil-event-analysis/dashboard/backend || exit 1
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cd ../frontend || exit 1
npm install
