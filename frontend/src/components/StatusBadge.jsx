import React from 'react';

export default function StatusBadge({ level }) {
  const norm = String(level || 'MODERATE').toUpperCase().trim();
  
  let label = 'Standing room';
  let colorClass = 'text-slate-600 font-medium';

  if (norm.includes('SEAT') || norm.includes('LOW')) {
    label = 'Seats available';
    colorClass = 'text-emerald-700 font-semibold';
  } else if (norm.includes('VERY HIGH') || norm.includes('HEAVY') || norm.includes('CRUSH')) {
    label = 'Heavy rush';
    colorClass = 'text-rose-700 font-semibold';
  } else if (norm.includes('HIGH') || norm.includes('CROWD')) {
    label = 'Crowded';
    colorClass = 'text-amber-800 font-semibold';
  }

  return (
    <span className={`text-xs ${colorClass} select-none`}>
      {label}
    </span>
  );
}
