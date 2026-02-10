import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const VolatilityChart = ({ height = 300 }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const load = async () => {
      const res = await api.getReturns();
      const rows = res.data.dates.map((d, i) => ({
        date: d,
        volatility: res.data.volatility[i]
      }));
      setData(rows);
    };
    load();
  }, []);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" hide />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="volatility" stroke="#166088" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default VolatilityChart;
