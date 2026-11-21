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

        <div className="w-7 h-7 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-[11px] font-bold text-slate-900">
          DT
        </div>
      </div>
    </header>
  );
}
