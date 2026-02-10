import React, { useState, useEffect, useCallback } from 'react';
import { format, subYears } from 'date-fns';
import { api } from '../services/api';
import SummaryMetrics from '../components/Dashboard/SummaryMetrics';
import PriceChartWithEvents from '../components/Charts/PriceChartWithEvents';
import EventImpactChart from '../components/Charts/EventImpactChart';
import VolatilityChart from '../components/Charts/VolatilityChart';
import ChangePointTimeline from '../components/Charts/ChangePointTimeline';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [priceData, setPriceData] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [filters, setFilters] = useState({
    startDate: format(subYears(new Date(), 5), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd'),
    resolution: 'monthly'
  });
  const [avgVolatility, setAvgVolatility] = useState(null);
  const [correlations, setCorrelations] = useState([]);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const summary = await api.getAnalysisSummary();
      setSummaryData(summary.data);

      const prices = await api.getPrices({
        start_date: filters.startDate,
        end_date: filters.endDate,
        resolution: filters.resolution
      });
      setPriceData(prices.data);

      const eventsData = await api.getEvents();
      setEvents(eventsData.data);

      const cpData = await api.getChangePoints();
      setChangePoints(cpData.data.change_points);

      const returns = await api.getReturns();
      const vol = returns.data.volatility || [];
      setAvgVolatility(vol.length ? (vol.reduce((a, b) => a + b, 0) / vol.length) : null);

      const corr = await api.getEventCorrelation();
      setCorrelations(corr.data.correlations || []);

      setLoading(false);
    } catch (err) {
      setError(err?.message || 'Failed to load data');
      setLoading(false);
    }
  }, [filters]);

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
  };

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  useEffect(() => {
    document.body.classList.toggle('dark-theme', theme === 'dark');
    return () => document.body.classList.remove('dark-theme');
  }, [theme]);

  if (loading) {
    return (
      <div className="text-center py-5">
        <p className="mt-3">Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-5">
        <div className="alert alert-danger">
          <h4 className="alert-heading">Error Loading Dashboard</h4>
          <p>{error}</p>
          <button className="btn btn-danger" onClick={fetchDashboardData}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1>Brent Oil Price Analysis Dashboard</h1>
          <p className="lead">Interactive analysis of geopolitical events and price dynamics</p>
        </div>
        <button
          className="btn btn-outline-secondary"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>

      <div className="filter-section">
        <div className="filter-group">
          <label className="filter-label">Start Date</label>
          <input
            className="filter-input"
            type="date"
            value={filters.startDate}
            onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
          />
        </div>
        <div className="filter-group">
          <label className="filter-label">End Date</label>
          <input
            className="filter-input"
            type="date"
            value={filters.endDate}
            onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
          />
        </div>
        <div className="filter-group">
          <label className="filter-label">Resolution</label>
          <select
            className="filter-select"
            value={filters.resolution}
            onChange={(e) => setFilters({ ...filters, resolution: e.target.value })}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
      </div>

      <SummaryMetrics data={summaryData} avgVolatility={avgVolatility} />

      <div className="row mt-4">
        <div className="col-lg-8">
          <div className="card chart-card">
            <div className="card-body">
              <h5 className="card-title">Price History with Events</h5>
              <PriceChartWithEvents
                priceData={priceData}
                events={events}
                changePoints={changePoints}
                selectedEvent={selectedEvent}
                onEventSelect={handleEventSelect}
                height={400}
              />
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card chart-card">
            <div className="card-body">
              <h5 className="card-title">Event Highlights</h5>
              <div className="event-list">
                {events.slice(0, 10).map((ev) => (
                  <button
                    key={`${ev.date}-${ev.title}`}
                    className={`event-item ${selectedEvent?.title === ev.title ? 'active' : ''}`}
                    onClick={() => handleEventSelect(ev)}
                  >
                    <span>{ev.date}</span> — {ev.title}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="card chart-card mt-3">
            <div className="card-body">
              <h5 className="card-title">Market Volatility</h5>
              <VolatilityChart height={300} />
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-lg-6">
          <div className="card chart-card">
            <div className="card-body">
              <h5 className="card-title">Event Impact Analysis</h5>
              {selectedEvent ? (
                <EventImpactChart event={selectedEvent} height={300} />
              ) : (
                <div className="text-center py-5">
                  <p>Select an event from the chart to see impact analysis</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card chart-card">
            <div className="card-body">
              <h5 className="card-title">Change Point Timeline</h5>
              <ChangePointTimeline changePoints={changePoints} height={300} />
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-md-12">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Event Correlations</h5>
              <div className="correlation-table">
                {correlations.slice(0, 8).map((c) => (
                  <div key={`${c.date}-${c.event}`} className="correlation-row">
                    <span>{c.date}</span>
                    <span>{c.event}</span>
                    <span>{(c.price_correlation * 100).toFixed(2)}%</span>
                  </div>
                ))}
                {correlations.length === 0 && <p>No correlation data available</p>}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-md-12">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Key Insights</h5>
              <div className="insights-grid">
                {summaryData?.insights &&
                  Object.entries(summaryData.insights).map(([key, value]) => (
                    <div key={key} className="insight-item">
                      <div className="insight-label">{key.replace(/_/g, ' ')}</div>
                      <div className="insight-value">{value}</div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;