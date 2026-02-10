#!/bin/bash
echo "Brent Oil Analysis Dashboard - Starting"

pkill -f "python app.py" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true

cd /home/nabi/brent-oil-event-analysis/dashboard/backend || exit 1
source venv/bin/activate
python app.py &
BACKEND_PID=$!

sleep 5

cd ../frontend || exit 1
npm start &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait $BACKEND_PID $FRONTEND_PID
