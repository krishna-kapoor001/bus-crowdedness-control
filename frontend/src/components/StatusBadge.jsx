import React from 'react';

export default function StatusBadge({ level, size = 'md' }) {
  const norm = String(level || 'MODERATE').toUpperCase().trim();

  let label = 'Standing room';
  let dotClass = 'bg-slate-500';
  let bgClass = 'bg-slate-100';
  let textClass = 'text-slate-800';
  let borderClass = 'border-slate-300';

  if (norm.includes('SEAT') || norm.includes('LOW')) {
    label = 'Seats available';
    dotClass = 'bg-emerald-500';
    bgClass = 'bg-emerald-50';
    textClass = 'text-emerald-800';
    borderClass = 'border-emerald-200';
  } else if (norm.includes('VERY HIGH') || norm.includes('HEAVY') || norm.includes('CRUSH')) {
    label = 'Heavy rush';
    dotClass = 'bg-rose-500';
    bgClass = 'bg-rose-50';
    textClass = 'text-rose-800';
    borderClass = 'border-rose-200';
  } else if (norm.includes('HIGH') || norm.includes('CROWD')) {
    label = 'Crowded';
    dotClass = 'bg-amber-500';
    bgClass = 'bg-amber-50';
    textClass = 'text-amber-800';
    borderClass = 'border-amber-200';
  }

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  }[size] || 'text-xs px-2.5 py-1 gap-1.5';

  const dotSize = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  }[size] || 'w-2 h-2';

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${sizeClasses} ${bgClass} ${textClass} ${borderClass} select-none shrink-0 tracking-tight`}
    >
      <span className={`rounded-full shrink-0 ${dotSize} ${dotClass}`} />
      <span>{label}</span>
    </span>
  );
}
