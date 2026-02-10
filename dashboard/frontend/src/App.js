import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis
} from 'recharts';
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardText,
  CardTitle,
  Col,
  Container,
  FormGroup,
  Input,
  Label,
  Nav,
  NavItem,
  NavLink,
  Navbar,
  NavbarBrand,
  Row,
  Spinner,
  TabContent,
  TabPane
} from 'reactstrap';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `${window.location.origin}/api`;

const formatDate = (dateString, options = {}) => {
  if (!dateString) return 'N/A';
  const parsed = new Date(dateString);
  if (Number.isNaN(parsed.getTime())) return 'N/A';
  return parsed.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  });
};

const fetchJson = async (url, allowNotFound = false) => {
  const response = await fetch(url);
  if (!response.ok) {
    if (allowNotFound && response.status === 404) {
      return null;
    }
    const body = await response.text();
    throw new Error(`Request failed ${response.status}: ${body.slice(0, 200)}`);
  }
  return response.json();
};

const formatNumber = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '0.00';
  }
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(value);
};

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    prices: { dates: [], prices: [], stats: {}, count: 0, date_range: {} },
    events: { events: [], type_distribution: {}, count: 0 },
    analysis: null,
    changePoints: [],
    volatility: null,
    correlations: []
  });
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventImpact, setEventImpact] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [filters, setFilters] = useState({
    startDate: '2000-01-01',
    endDate: '2022-12-31',
    eventType: 'all',
    windowDays: 30,
    resample: 'D'
  });

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const priceParams = new URLSearchParams({
        start_date: filters.startDate,
        end_date: filters.endDate,
        resample: filters.resample
      });

      const eventParams = new URLSearchParams();
      if (filters.eventType && filters.eventType !== 'all') {
        eventParams.set('event_type', filters.eventType);
      }
      const eventsUrl = eventParams.toString()
        ? `${API_BASE_URL}/events?${eventParams.toString()}`
        : `${API_BASE_URL}/events`;

      const [pricesResult, eventsResult, summaryResult, cpResult, volResult, corrResult] = await Promise.allSettled([
        fetchJson(`${API_BASE_URL}/prices?${priceParams.toString()}`),
        fetchJson(eventsUrl),
        fetchJson(`${API_BASE_URL}/analysis/summary`, true),
        fetchJson(`${API_BASE_URL}/analysis/changepoints`, true),
        fetchJson(`${API_BASE_URL}/analysis/volatility?window=30&start_date=${filters.startDate}&end_date=${filters.endDate}`, true),
        fetchJson(`${API_BASE_URL}/analysis/correlation`, true)
      ]);

      const nextData = {
        prices: pricesResult.status === 'fulfilled' && pricesResult.value
          ? pricesResult.value
          : { dates: [], prices: [], stats: {}, count: 0, date_range: {} },
        events: eventsResult.status === 'fulfilled' && eventsResult.value
          ? eventsResult.value
          : { events: [], type_distribution: {}, count: 0 },
        analysis: summaryResult.status === 'fulfilled' ? summaryResult.value : null,
        changePoints: cpResult.status === 'fulfilled'
          ? (cpResult.value?.change_points || [])
          : [],
        volatility: volResult.status === 'fulfilled' ? volResult.value : null,
        correlations: corrResult.status === 'fulfilled'
          ? (corrResult.value?.correlations || [])
          : []
      };

      const errors = [];
      if (pricesResult.status === 'rejected') errors.push('price');
      if (eventsResult.status === 'rejected') errors.push('event');
      if (summaryResult.status === 'rejected') errors.push('summary');
      if (cpResult.status === 'rejected') errors.push('change point');
      if (volResult.status === 'rejected') errors.push('volatility');
      if (corrResult.status === 'rejected') errors.push('correlation');

      const criticalErrors = errors.filter((item) => item === 'price' || item === 'event');
      if (criticalErrors.length > 0) {
        setError(`Partial data load: ${criticalErrors.join(', ')}.`);
      }

      setData(nextData);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load dashboard data. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  }, [filters.startDate, filters.endDate, filters.eventType, filters.resample]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const applyFilters = () => {
    fetchAllData();
  };

  const handleEventClick = async (event) => {
    const normalizedEvent = {
      ...event,
      title: event.title || event.event,
      date: event.date
    };

    setSelectedEvent(normalizedEvent);

    try {
      const response = await fetch(
        `${API_BASE_URL}/analysis/event-impact/${encodeURIComponent(normalizedEvent.title)}?window_days=${filters.windowDays}`
      );
      const impactData = await response.json();
      setEventImpact(impactData);
    } catch (err) {
      console.error('Error fetching event impact:', err);
      setEventImpact(null);
    }
  };

  const priceSeries = useMemo(() => {
    const dates = data.prices?.dates || [];
    const prices = data.prices?.prices || [];
    const count = Math.min(dates.length, prices.length);

    return Array.from({ length: count }, (_, index) => ({
      date: dates[index],
      dateLabel: formatDate(dates[index], { month: 'short', year: '2-digit' }),
      price: prices[index]
    }));
  }, [data.prices]);

  const priceMap = useMemo(() => {
    const map = new Map();
    priceSeries.forEach((point) => {
      map.set(point.date, point.price);
    });
    return map;
  }, [priceSeries]);

  const eventMarkers = useMemo(() => {
    return (data.events?.events || [])
      .map((eventItem) => {
        const price = priceMap.get(eventItem.date);
        if (price === undefined) return null;
        return {
          date: eventItem.date,
          dateLabel: formatDate(eventItem.date, { month: 'short', year: '2-digit' }),
          price,
          title: eventItem.title,
          type: eventItem.type
        };
      })
      .filter(Boolean);
  }, [data.events, priceMap]);

  const volatilitySeries = useMemo(() => {
    const dates = data.volatility?.volatility_series?.dates || [];
    const values = data.volatility?.volatility_series?.volatility || [];
    const count = Math.min(dates.length, values.length);
    return Array.from({ length: count }, (_, index) => ({
      date: dates[index],
      dateLabel: formatDate(dates[index], { month: 'short', year: '2-digit' }),
      volatility: values[index]
    }));
  }, [data.volatility]);

  const impactSeries = useMemo(() => {
    return (data.correlations || []).map((eventItem) => ({
      title: eventItem.event || eventItem.title,
      date: eventItem.date,
      dateLabel: formatDate(eventItem.date, { month: 'short', year: '2-digit' }),
      price_change: eventItem.price_change,
      magnitude: eventItem.magnitude,
      type: eventItem.type,
      size: Math.max(4, Math.min(40, Math.abs(eventItem.magnitude || 0)))
    }));
  }, [data.correlations]);

  const changePoint = data.changePoints?.[0] || null;

  if (loading) {
    return (
      <div className="loading-screen">
        <Spinner color="light" />
        <p>Loading the Brent Oil intelligence hub...</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Navbar expand="md" className="main-nav">
        <Container>
          <NavbarBrand href="/" className="brand-title">
            Brent Intelligence
          </NavbarBrand>
          <div className="nav-meta">Bayesian change point analysis</div>
          <Nav className="ms-auto nav-pills" navbar>
            {['overview', 'change', 'events', 'volatility'].map((tab) => (
              <NavItem key={tab}>
                <NavLink
                  className={activeTab === tab ? 'active' : ''}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab === 'overview' && 'Overview'}
                  {tab === 'change' && 'Change Points'}
                  {tab === 'events' && 'Event Impact'}
                  {tab === 'volatility' && 'Volatility'}
                </NavLink>
              </NavItem>
            ))}
          </Nav>
        </Container>
      </Navbar>

      <header className="hero">
        <Container>
          <div className="hero-content">
            <div>
              <p className="eyebrow">Birhan Energies</p>
              <h1>Change Point Analysis and Statistical Modeling of Brent Oil Prices</h1>
              <p className="hero-subtitle">
                Track structural breaks, quantify event impacts, and connect market regimes to geopolitical triggers.
              </p>
              <div className="hero-meta">
                <span>Price records: {data.prices?.count || 0}</span>
                <span>
                  Range: {formatDate(data.prices?.date_range?.start)} - {formatDate(data.prices?.date_range?.end)}
                </span>
                <span>Updated: {formatDate(lastUpdated)}</span>
              </div>
            </div>
            <div className="hero-card">
              <h3>Change Point Snapshot</h3>
              {changePoint ? (
                <>
                  <div className="hero-stat">
                    <span>Detected date</span>
                    <strong>{formatDate(changePoint.date)}</strong>
                  </div>
                  <div className="hero-stat">
                    <span>95% HDI</span>
                    <strong>
                      {formatDate(changePoint.hdi_95?.[0])} - {formatDate(changePoint.hdi_95?.[1])}
                    </strong>
                  </div>
                  <div className="hero-stat">
                    <span>Posterior probability</span>
                    <strong>{((changePoint.probability || 0) * 100).toFixed(1)}%</strong>
                  </div>
                </>
              ) : (
                <p>No change point detected in the current window.</p>
              )}
            </div>
          </div>
        </Container>
      </header>

      <Container className="filters-section">
        <Card className="glass-card">
          <CardBody>
            <Row className="g-3 align-items-end">
              <Col md={3}>
                <FormGroup>
                  <Label for="startDate">Start date</Label>
                  <Input
                    type="date"
                    name="startDate"
                    id="startDate"
                    value={filters.startDate}
                    onChange={handleFilterChange}
                  />
                </FormGroup>
              </Col>
              <Col md={3}>
                <FormGroup>
                  <Label for="endDate">End date</Label>
                  <Input
                    type="date"
                    name="endDate"
                    id="endDate"
                    value={filters.endDate}
                    onChange={handleFilterChange}
                  />
                </FormGroup>
              </Col>
              <Col md={2}>
                <FormGroup>
                  <Label for="resample">Resample</Label>
                  <Input
                    type="select"
                    name="resample"
                    id="resample"
                    value={filters.resample}
                    onChange={handleFilterChange}
                  >
                    <option value="D">Daily</option>
                    <option value="W">Weekly</option>
                    <option value="M">Monthly</option>
                  </Input>
                </FormGroup>
              </Col>
              <Col md={2}>
                <FormGroup>
                  <Label for="eventType">Event type</Label>
                  <Input
                    type="select"
                    name="eventType"
                    id="eventType"
                    value={filters.eventType}
                    onChange={handleFilterChange}
                  >
                    <option value="all">All</option>
                    {data.events.type_distribution &&
                      Object.keys(data.events.type_distribution).map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                  </Input>
                </FormGroup>
              </Col>
              <Col md={2}>
                <FormGroup>
                  <Label for="windowDays">Impact window</Label>
                  <Input
                    type="select"
                    name="windowDays"
                    id="windowDays"
                    value={filters.windowDays}
                    onChange={handleFilterChange}
                  >
                    <option value={14}>14 days</option>
                    <option value={30}>30 days</option>
                    <option value={60}>60 days</option>
                    <option value={90}>90 days</option>
                  </Input>
                </FormGroup>
              </Col>
              <Col md={12} className="d-flex justify-content-end">
                <Button color="primary" className="cta-button" onClick={applyFilters}>
                  Refresh insights
                </Button>
              </Col>
            </Row>
          </CardBody>
        </Card>
      </Container>

      <Container className="main-content">
        {error && (
          <Alert color="danger" className="mb-4">
            {error}
          </Alert>
        )}

        <TabContent activeTab={activeTab}>
          <TabPane tabId="overview">
            <Row className="g-4">
              <Col md={3}>
                <Card className="stat-card">
                  <CardBody>
                    <CardTitle tag="h6">Average price</CardTitle>
                    <CardText tag="h4">${formatNumber(data.prices.stats?.mean || 0)}</CardText>
                    <p className="stat-sub">Median ${formatNumber(data.prices.stats?.median || 0)}</p>
                  </CardBody>
                </Card>
              </Col>
              <Col md={3}>
                <Card className="stat-card">
                  <CardBody>
                    <CardTitle tag="h6">Price range</CardTitle>
                    <CardText tag="h4">
                      ${formatNumber(data.prices.stats?.min || 0)} - ${formatNumber(data.prices.stats?.max || 0)}
                    </CardText>
                    <p className="stat-sub">Std dev ${formatNumber(data.prices.stats?.std || 0)}</p>
                  </CardBody>
                </Card>
              </Col>
              <Col md={3}>
                <Card className="stat-card">
                  <CardBody>
                    <CardTitle tag="h6">Events tracked</CardTitle>
                    <CardText tag="h4">{data.events.count || 0}</CardText>
                    <p className="stat-sub">Across {Object.keys(data.events.type_distribution || {}).length} types</p>
                  </CardBody>
                </Card>
              </Col>
              <Col md={3}>
                <Card className="stat-card">
                  <CardBody>
                    <CardTitle tag="h6">Average volatility</CardTitle>
                    <CardText tag="h4">{formatNumber(data.volatility?.average_volatility || 0)}</CardText>
                    <p className="stat-sub">Max {formatNumber(data.volatility?.max_volatility || 0)}</p>
                  </CardBody>
                </Card>
              </Col>
            </Row>

            <Row className="g-4 mt-1">
              <Col md={8}>
                <Card className="chart-card">
                  <CardBody>
                    <div className="card-header">
                      <div>
                        <CardTitle tag="h5">Historical price with event overlay</CardTitle>
                        <p className="card-subtitle">Event markers highlight dates with recorded geopolitical shocks.</p>
                      </div>
                    </div>
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={priceSeries} margin={{ top: 10, right: 16, bottom: 20, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                          <XAxis dataKey="dateLabel" angle={-25} textAnchor="end" height={60} stroke="#c6c9d1" />
                          <YAxis stroke="#c6c9d1" />
                          <Tooltip
                            contentStyle={{ background: '#0f172a', border: '1px solid #1f2937' }}
                            labelFormatter={(label) => `Date: ${label}`}
                            formatter={(value) => [`$${formatNumber(value)}`, 'Price']}
                          />
                          <Area type="monotone" dataKey="price" stroke="#60a5fa" fill="#2563eb" fillOpacity={0.3} />
                          <Line type="monotone" dataKey="price" stroke="#93c5fd" strokeWidth={2} dot={false} />
                          {changePoint?.date && (
                            <ReferenceLine
                              x={formatDate(changePoint.date, { month: 'short', year: '2-digit' })}
                              stroke="#f59e0b"
                              strokeDasharray="4 4"
                              label={{ value: 'Change point', position: 'top', fill: '#f59e0b' }}
                            />
                          )}
                          <Scatter data={eventMarkers} dataKey="price" fill="#f97316" />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>
              </Col>

              <Col md={4}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Recent events</CardTitle>
                    <p className="card-subtitle">Click an event to open impact analysis.</p>
                    <div className="events-list">
                      {data.events.events?.slice(0, 6).map((eventItem, index) => (
                        <button
                          type="button"
                          key={`${eventItem.title}-${index}`}
                          className="event-chip"
                          onClick={() => handleEventClick(eventItem)}
                        >
                          <div>
                            <span className="event-date">{formatDate(eventItem.date)}</span>
                            <strong>{eventItem.title}</strong>
                          </div>
                          <span className="event-tag">{eventItem.type}</span>
                        </button>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane tabId="change">
            <Row className="g-4">
              <Col md={8}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Bayesian change point analysis</CardTitle>
                    {changePoint ? (
                      <div className="change-summary">
                        <div className="summary-block">
                          <span>Detected change point</span>
                          <strong>{formatDate(changePoint.date)}</strong>
                        </div>
                        <div className="summary-block">
                          <span>95% HDI interval</span>
                          <strong>
                            {formatDate(changePoint.hdi_95?.[0])} - {formatDate(changePoint.hdi_95?.[1])}
                          </strong>
                        </div>
                        <div className="summary-block">
                          <span>Posterior probability</span>
                          <strong>{((changePoint.probability || 0) * 100).toFixed(1)}%</strong>
                        </div>
                      </div>
                    ) : (
                      <Alert color="warning">No change point detected for this filtered range.</Alert>
                    )}

                    <Row className="g-3 mt-3">
                      <Col md={6}>
                        <Card className="metric-card">
                          <CardBody>
                            <h6>Mean returns shift</h6>
                            <p className="metric-value">
                              {formatNumber(changePoint?.parameter_changes?.mean_change?.mean || 0)}
                            </p>
                            <p className="metric-sub">
                              Probability of increase: {((changePoint?.parameter_changes?.mean_change?.probability_positive || 0) * 100).toFixed(1)}%
                            </p>
                          </CardBody>
                        </Card>
                      </Col>
                      <Col md={6}>
                        <Card className="metric-card">
                          <CardBody>
                            <h6>Volatility shift</h6>
                            <p className="metric-value">
                              {formatNumber(changePoint?.parameter_changes?.volatility_change?.mean || 0)}
                            </p>
                            <p className="metric-sub">
                              Probability of increase: {((changePoint?.parameter_changes?.volatility_change?.probability_increase || 0) * 100).toFixed(1)}%
                            </p>
                          </CardBody>
                        </Card>
                      </Col>
                    </Row>
                  </CardBody>
                </Card>
              </Col>
              <Col md={4}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Events near change point</CardTitle>
                    <div className="events-list">
                      {changePoint?.nearby_events?.length ? (
                        changePoint.nearby_events.map((eventItem, index) => (
                          <div key={`${eventItem.title}-${index}`} className="event-row">
                            <div>
                              <strong>{eventItem.title}</strong>
                              <span>{formatDate(eventItem.date)} ({eventItem.days_from_cp} days)</span>
                            </div>
                            <span className="event-tag">{eventItem.type}</span>
                          </div>
                        ))
                      ) : (
                        <p>No nearby events found for this change point.</p>
                      )}
                    </div>
                  </CardBody>
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane tabId="events">
            <Row className="g-4">
              <Col md={8}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Event impact map</CardTitle>
                    <p className="card-subtitle">Size shows magnitude; vertical axis shows percent price change.</p>
                    <div className="chart-wrap tall">
                      <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 16, right: 16, bottom: 40, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                          <XAxis dataKey="dateLabel" angle={-35} textAnchor="end" height={60} stroke="#c6c9d1" />
                          <YAxis dataKey="price_change" stroke="#c6c9d1" />
                          <ZAxis dataKey="size" range={[60, 400]} />
                          <Tooltip
                            contentStyle={{ background: '#0f172a', border: '1px solid #1f2937' }}
                            formatter={(value, name, props) => {
                              if (name === 'price_change') return [`${formatNumber(value)}%`, 'Change'];
                              return [value, name];
                            }}
                            labelFormatter={(label) => `Date: ${label}`}
                          />
                          <Legend />
                          <Scatter
                            name="Event impacts"
                            data={impactSeries}
                            fill="#22d3ee"
                            onClick={(payload) => handleEventClick(payload.payload)}
                          />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>
              </Col>
              <Col md={4}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Top impact events</CardTitle>
                    <div className="events-list">
                      {impactSeries
                        .slice()
                        .sort((a, b) => Math.abs(b.price_change) - Math.abs(a.price_change))
                        .slice(0, 6)
                        .map((eventItem, index) => (
                          <button
                            type="button"
                            key={`${eventItem.title}-${index}`}
                            className="event-chip"
                            onClick={() => handleEventClick(eventItem)}
                          >
                            <div>
                              <span className="event-date">{formatDate(eventItem.date)}</span>
                              <strong>{eventItem.title}</strong>
                            </div>
                            <span className={`event-tag ${eventItem.price_change > 0 ? 'positive' : 'negative'}`}>
                              {eventItem.price_change > 0 ? '+' : ''}{formatNumber(eventItem.price_change, 1)}%
                            </span>
                          </button>
                        ))}
                    </div>
                  </CardBody>
                </Card>
              </Col>
            </Row>

            {selectedEvent && eventImpact?.impact && eventImpact?.price_data && (
              <Row className="g-4 mt-1">
                <Col md={12}>
                  <Card className="chart-card">
                    <CardBody>
                      <CardTitle tag="h5">Impact analysis: {selectedEvent.title}</CardTitle>
                      <Row className="g-4 mt-2">
                        <Col md={4}>
                          <Card className="metric-card">
                            <CardBody>
                              <h6>Price change</h6>
                              <p className={`metric-value ${eventImpact.impact.percent_change > 0 ? 'positive' : 'negative'}`}>
                                {eventImpact.impact.percent_change > 0 ? '+' : ''}
                                {formatNumber(eventImpact.impact.percent_change)}%
                              </p>
                              <p className="metric-sub">
                                ${formatNumber(eventImpact.impact.pre_avg)} to ${formatNumber(eventImpact.impact.post_avg)}
                              </p>
                              <p className="metric-sub">Significance: {eventImpact.analysis?.significance}</p>
                            </CardBody>
                          </Card>
                        </Col>
                        <Col md={8}>
                          <div className="chart-wrap medium">
                            <ResponsiveContainer width="100%" height="100%">
                              <LineChart data={eventImpact.price_data.dates.map((date, index) => ({
                                dateLabel: formatDate(date, { month: 'short', day: 'numeric' }),
                                date,
                                price: eventImpact.price_data.prices[index],
                                isEvent: date === selectedEvent.date
                              }))}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                                <XAxis dataKey="dateLabel" stroke="#c6c9d1" />
                                <YAxis stroke="#c6c9d1" />
                                <Tooltip
                                  contentStyle={{ background: '#0f172a', border: '1px solid #1f2937' }}
                                  formatter={(value) => [`$${formatNumber(value)}`, 'Price']}
                                />
                                <Line type="monotone" dataKey="price" stroke="#a78bfa" strokeWidth={2} dot={false} />
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                        </Col>
                      </Row>
                    </CardBody>
                  </Card>
                </Col>
              </Row>
            )}
          </TabPane>

          <TabPane tabId="volatility">
            <Row className="g-4">
              <Col md={8}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Rolling volatility</CardTitle>
                    {volatilitySeries.length === 0 && (
                      <Alert color="warning" className="mt-3">
                        No volatility data available for the selected range. Try expanding the dates.
                      </Alert>
                    )}
                    <div className="chart-wrap tall">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={volatilitySeries} margin={{ top: 16, right: 16, bottom: 40, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                          <XAxis dataKey="dateLabel" angle={-35} textAnchor="end" height={60} stroke="#c6c9d1" />
                          <YAxis stroke="#c6c9d1" />
                          <Tooltip
                            contentStyle={{ background: '#0f172a', border: '1px solid #1f2937' }}
                            formatter={(value) => [formatNumber(value), 'Volatility']}
                          />
                          <Area type="monotone" dataKey="volatility" stroke="#34d399" fill="#10b981" fillOpacity={0.25} />
                          <Line type="monotone" dataKey="volatility" stroke="#6ee7b7" strokeWidth={2} dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>
              </Col>
              <Col md={4}>
                <Card className="chart-card">
                  <CardBody>
                    <CardTitle tag="h5">Event volatility impact</CardTitle>
                    <div className="chart-wrap medium">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={(data.volatility?.event_volatility || []).slice(0, 6).map((eventItem) => ({
                          name: eventItem.event.length > 16 ? `${eventItem.event.substring(0, 16)}...` : eventItem.event,
                          volatilityChange: eventItem.volatility_change || 0
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                          <XAxis dataKey="name" angle={-35} textAnchor="end" height={60} stroke="#c6c9d1" />
                          <YAxis stroke="#c6c9d1" />
                          <Tooltip
                            contentStyle={{ background: '#0f172a', border: '1px solid #1f2937' }}
                            formatter={(value) => [`${formatNumber(value)}%`, 'Volatility change']}
                          />
                          <Bar dataKey="volatilityChange" fill="#f472b6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </TabContent>
      </Container>

      <footer className="footer">
        <Container>
          <div className="footer-inner">
            <span>Brent Oil Price Analysis Dashboard</span>
            <span>Bayesian Change Point Detection</span>
          </div>
        </Container>
      </footer>
    </div>
  );
}

export default App;
