import React from 'react';

const SummaryMetrics = ({ data, avgVolatility }) => {
  const price = data?.summary?.price;
  const events = data?.summary?.events;

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-value">{price ? `$${price.mean.toFixed(2)}` : '—'}</div>
        <div className="metric-label">Average Price</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{events?.total ?? '—'}</div>
        <div className="metric-label">Events</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{avgVolatility != null ? avgVolatility.toFixed(4) : '—'}</div>
        <div className="metric-label">Avg Volatility</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{events?.avg_impact != null ? `${events.avg_impact.toFixed(2)}%` : '—'}</div>
        <div className="metric-label">Avg Event Impact</div>
      </div>
    </div>
  );
};

export default SummaryMetrics;
