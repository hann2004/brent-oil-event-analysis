# Task 3: Interactive Dashboard Development

## Objectives
1. Build a Flask backend API serving analysis results
2. Create a React frontend dashboard for interactive exploration
3. Visualize Bayesian change point analysis results
4. Enable event impact analysis and filtering
5. Provide a stakeholder-friendly interface for insights

## Project Structure

```
dashboard/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── build/
```

## Quick Start

### Option 1: Automated Setup
```bash
chmod +x scripts/setup_dashboard.sh
./scripts/setup_dashboard.sh
```

### Option 2: Manual Setup

#### Backend
```bash
cd dashboard/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd dashboard/frontend
npm install
npm start
```

## Access URLs
- Backend API: http://localhost:5000
- React Dev Server: http://localhost:3000
- Production Dashboard: http://localhost:5000/dashboard
- Health Check: http://localhost:5000/api/health

## API Endpoints

### Data Endpoints
- GET /api/prices
- GET /api/events
- GET /api/analysis/summary

### Analysis Endpoints
- GET /api/analysis/changepoints
- GET /api/analysis/event-impact/<event_title>
- GET /api/analysis/volatility
- GET /api/analysis/correlation

### Parameters
- start_date, end_date: Date filtering
- event_type: Filter events by type
- window_days: Analysis window (default: 30)
- resample: Data resampling (D, W, M)

## Dashboard Features

### 1. Main Dashboard
- Price visualization with key statistics
- Recent events timeline
- Interactive date range selection

### 2. Bayesian Analysis Tab
- Change point summary with HDI interval
- Parameter change quantification
- Nearby events correlation

### 3. Events Impact Tab
- Scatter plot of event impacts
- Top impact events ranking
- Detailed event impact analysis

### 4. Volatility Analysis Tab
- Rolling volatility visualization
- Event volatility impact summary

## Troubleshooting

### CORS Errors
Ensure the proxy is set in dashboard/frontend/package.json:
```json
"proxy": "http://localhost:5000"
```

### Data Not Loading
- Verify Flask server is running
- Check file paths in dashboard/backend/app.py
- Review API errors in the browser console

### React Build Issues
```bash
rm -rf node_modules package-lock.json
npm install
```

## Deployment

### Docker (Backend)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY dashboard/backend/requirements.txt /app/dashboard/backend/requirements.txt
RUN pip install -r /app/dashboard/backend/requirements.txt
COPY . /app
CMD ["python", "/app/dashboard/backend/app.py"]
```

### docker-compose
```yaml
version: "3.8"
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./models:/app/models

  frontend:
    build: ./dashboard/frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Testing

### Backend
```bash
cd dashboard/backend
python -m pytest tests/
```

### Frontend
```bash
cd dashboard/frontend
npm test
```
