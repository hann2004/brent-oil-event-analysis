#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DASHBOARD_DIR="$ROOT_DIR/dashboard"
BACKEND_DIR="$DASHBOARD_DIR/backend"
FRONTEND_DIR="$DASHBOARD_DIR/frontend"

echo "=========================================="
echo "TASK 3: Dashboard Setup"
echo "=========================================="

mkdir -p "$BACKEND_DIR" "$FRONTEND_DIR/src" "$FRONTEND_DIR/public"

if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
  echo "Missing backend requirements.txt at $BACKEND_DIR/requirements.txt"
  exit 1
fi

echo "Installing Flask backend dependencies..."
cd "$BACKEND_DIR"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
  echo "Initializing React frontend..."
  cd "$FRONTEND_DIR"
  npx create-react-app .
else
  echo "React frontend already initialized."
  cd "$FRONTEND_DIR"
fi

echo "Installing React dependencies..."
npm install recharts reactstrap bootstrap axios

echo "Building React app..."
npm run build

cd "$ROOT_DIR"

echo ""
echo "=========================================="
echo "DASHBOARD SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "To run the dashboard:"
echo "1. Start Flask backend:"
echo "   cd dashboard/backend && source venv/bin/activate && python app.py"
echo "2. Start React frontend (development mode):"
echo "   cd dashboard/frontend && npm start"
