# Brent Oil Price Analysis Dashboard

A professional, interactive dashboard for analyzing Brent crude prices alongside geopolitical and economic events. It includes a Flask API backend and a React frontend with interactive charts, filters, and event impact analysis.

![Dashboard Preview](../docs/dashboared.gif)

## ✨ Features
- Historical price trends with event highlights
- Event impact analysis (before/after)
- Change point timeline
- Volatility tracking
- Correlation overview
- Date range and resolution filters
- Light/Dark mode

## 🧱 Tech Stack
- **Backend:** Flask, Pandas, NumPy
- **Frontend:** React, Recharts, Axios
- **API:** REST endpoints under `/api/v1`

## 📁 Structure
```
dashboard/
├── backend/
├── frontend/
├── scripts/
└── README.md
```

## ✅ Quick Start

### 1) Setup
```bash
./scripts/setup.sh
```

### 2) Run
```bash
./scripts/run.sh
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:5000  
- API Docs: http://localhost:5000/api-docs

## 🔌 API Overview
- `GET /api/v1/prices/`  
- `GET /api/v1/prices/returns`  
- `GET /api/v1/prices/summary`  
- `GET /api/v1/events/`  
- `GET /api/v1/events/impact`  
- `GET /api/v1/changepoint/`  
- `GET /api/v1/analysis/summary`  
- `GET /api/v1/analysis/correlation`

## 🧪 Troubleshooting
- **react-scripts missing**:  
  ```bash
  cd frontend
  rm -rf node_modules package-lock.json
  npm install
  ```
- **API errors**: confirm backend is running and `REACT_APP_API_HOST` is correct.

## 🖼️ Dashboard Preview
Place the GIF at:
```
/home/nabi/brent-oil-event-analysis/docs/dashboared.gif
```

Then it will render automatically in this README.

## 📌 Notes
- Data files are expected under `/data/`.
- If the requested date range is outside the dataset, the API clamps to the dataset bounds.
