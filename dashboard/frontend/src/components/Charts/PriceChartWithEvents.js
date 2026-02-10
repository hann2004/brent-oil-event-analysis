import React, { useState } from 'react';
import {
  ComposedChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Scatter
} from 'recharts';
import { format, parseISO } from 'date-fns';

const PriceChartWithEvents = ({ priceData, events, changePoints, onEventSelect, selectedEvent, height = 400 }) => {
  const [hoveredEvent, setHoveredEvent] = useState(null);

  if (!priceData || !priceData.dates || priceData.dates.length === 0) {
    return (
      <div className="text-center py-5">
        <p>No price data available</p>
      </div>
    );
  }

  // Prepare chart data
  const chartData = priceData.dates.map((date, index) => ({
    date: parseISO(date),
    price: priceData.prices[index],
    formattedDate: format(parseISO(date), 'MMM yyyy')
  }));

  // Prepare event markers
  const eventMarkers = events.map(event => {
    const eventDate = parseISO(event.date);
    const pricePoint = chartData.find(d => 
      d.date.getFullYear() === eventDate.getFullYear() &&
      d.date.getMonth() === eventDate.getMonth()
    );
    
    return pricePoint ? {
      ...event,
      chartDate: pricePoint.date,
      chartPrice: pricePoint.price,
      x: chartData.indexOf(pricePoint),
      y: pricePoint.price
    } : null;
  }).filter(Boolean);

  // Prepare change point markers
  const changePointMarkers = changePoints.map(cp => {
    const cpDate = parseISO(cp.date);
    const pricePoint = chartData.find(d => 
      d.date.getFullYear() === cpDate.getFullYear() &&
      d.date.getMonth() === cpDate.getMonth()
    );
    
    return pricePoint ? {
      ...cp,
      chartDate: pricePoint.date,
      chartPrice: pricePoint.price,
      x: chartData.indexOf(pricePoint),
      y: pricePoint.price
    } : null;
  }).filter(Boolean);

  const handleEventClick = (event) => {
    if (onEventSelect) {
      onEventSelect(event);
    }
  };

  const CustomTooltipContent = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const eventsAtDate = eventMarkers.filter(e => 
        e.chartDate.getTime() === data.date.getTime()
      );
      
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">{format(data.date, 'MMMM d, yyyy')}</p>
          <p className="tooltip-price">
            Price: <strong>${data.price.toFixed(2)}</strong>
          </p>
          {eventsAtDate.length > 0 && (
            <div className="tooltip-events">
              <p className="tooltip-events-title">Events:</p>
              {eventsAtDate.map(event => (
                <p 
                  key={event.title}
                  className="tooltip-event"
                  onClick={() => handleEventClick(event)}
                  style={{ cursor: 'pointer', color: '#1890ff' }}
                >
                  • {event.title}
                </p>
              ))}
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart
        data={chartData}
        margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="formattedDate"
          angle={-45}
          textAnchor="end"
          height={60}
          tick={{ fontSize: 12 }}
          interval="preserveStartEnd"
        />
        <YAxis
          label={{ value: 'Price (USD)', angle: -90, position: 'insideLeft' }}
          tickFormatter={(value) => `$${value.toFixed(0)}`}
        />
        <Tooltip content={<CustomTooltipContent />} />
        
        {/* Price line */}
        <Line
          type="monotone"
          dataKey="price"
          stroke="#4A6FA5"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6, onClick: (e, payload) => console.log(payload) }}
          name="Brent Crude Price"
        />
        
        {/* Event markers */}
        <Scatter
          data={eventMarkers}
          fill="#FF6B6B"
          name="Events"
          shape={(props) => {
            const { cx, cy, payload } = props;
            const isSelected = selectedEvent?.title === payload.title;
            return (
              <g>
                <circle
                  cx={cx}
                  cy={cy}
                  r={isSelected ? 9 : 6}
                  fill={isSelected ? '#F59E0B' : '#FF6B6B'}
                  stroke="#fff"
                  strokeWidth={2}
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleEventClick(payload)}
                />
              </g>
            );
          }}
        />
        
        {/* Change point reference lines */}
        {changePointMarkers.map((cp, index) => (
          <ReferenceLine
            key={index}
            x={cp.formattedDate}
            stroke="#8B5CF6"
            strokeWidth={2}
            strokeDasharray="3 3"
            label={{
              value: `CP ${index + 1}`,
              position: 'top',
              fill: '#8B5CF6',
              fontSize: 12,
              fontWeight: 'bold'
            }}
          />
        ))}
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default PriceChartWithEvents;