import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

const EventImpactChart = ({ event }) => {
  const [impact, setImpact] = useState(null);

  useEffect(() => {
    const load = async () => {
      if (!event?.date) return;
      const res = await api.getEventImpact({ event_date: event.date });
      setImpact(res.data);
    };
    load();
  }, [event]);

  if (!impact) return <div>Loading impact...</div>;

  return (
    <div>
      <p><strong>{impact.event.title}</strong> ({impact.event.date})</p>
      <p>Price Impact: {impact.impact.price_impact.percent_change.toFixed(2)}%</p>
      <p>Volatility Impact: {impact.impact.volatility_impact.percent_change.toFixed(2)}%</p>
    </div>
  );
};

export default EventImpactChart;
