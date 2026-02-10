# Brent Oil Event Analysis

A full-stack data analysis project for Brent crude oil prices, combining statistical analysis, event impacts, and a modern interactive dashboard.

![Dashboard Preview](docs/dashboared.gif)

## Highlights
- Time series analysis with event context
- Change point detection insights
- Interactive dashboard (React + Flask)
- Filters, event highlights, and impact drill-downs

## Project Structure
```
brent-oil-event-analysis/
├── dashboard/
├── data/
├── models/
├── reports/
└── README.md
```

## Dashboard
See `/dashboard/README.md` for setup and usage.

## Quick Start
```bash
cd dashboard
./scripts/setup.sh
./scripts/run.sh
```

## Data
Expected datasets:
- `data/raw/BrentOilPrices.csv`
- `data/events/key_events.csv`
- `data/events/enhanced_events.csv`

## License
MIT