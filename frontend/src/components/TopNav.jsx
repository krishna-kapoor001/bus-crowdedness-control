import React from 'react';
import { Database, ShieldCheck } from 'lucide-react';

export default function TopNav({ activePageTitle }) {
  return (
    <header className="h-16 bg-white/70 backdrop-blur-xl border-b border-black/[0.05] px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-bold text-[#1D1D1F] tracking-tight">
          {activePageTitle}
        </h1>
        <span className="text-[#D2D2D7] hidden sm:block">•</span>
        <span className="text-xs text-[#86868B] hidden sm:block">
          Delhi NCT Transit Operations
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500 font-medium">
          <Database className="w-3.5 h-3.5 text-slate-400" />
          <span>October 2026 ETM</span>
        </div>

        <img
          src="/favicon.png"
          alt="DTC Smart Occupancy System"
          className="w-8 h-8 rounded-lg border border-slate-200 object-contain shadow-2xs bg-white p-0.5"
          title="DTC Smart Occupancy System"
        />
      </div>
    </header>
  );
}
