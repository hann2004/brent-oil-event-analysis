import React from 'react';

const ChangePointTimeline = ({ changePoints = [] }) => {
  if (!changePoints.length) return <div>No change points available</div>;

  return (
    <ul>
      {changePoints.map((cp, idx) => (
        <li key={`${cp.date}-${idx}`}>
          <strong>{cp.date}</strong> — {cp.description || 'Change point'}
        </li>
      ))}
    </ul>
  );
};

export default ChangePointTimeline;
