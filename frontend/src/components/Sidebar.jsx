import React from 'react';
import {
  LayoutDashboard,
  Navigation,
  Map,
  Compass
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'journey-planner', label: 'Route Planner', icon: Navigation },
  { id: 'network-explorer', label: 'Bus Map', icon: Map },
];

export default function Sidebar({ activePage, setActivePage }) {
  return (
    <aside className="w-72 bg-white border-r border-black/[0.06] flex flex-col justify-between h-screen fixed left-0 top-0 select-none z-30">
      <div>
        {/* Brand Header with prominent high-detail logo */}
        <div className="px-4 py-3.5 border-b border-black/[0.05] bg-gradient-to-b from-slate-50/70 to-white flex flex-col items-center">
          <button
            type="button"
            onClick={() => setActivePage && setActivePage('overview')}
            className="w-full flex items-center justify-center p-2.5 rounded-xl bg-white border border-slate-200/80 shadow-2xs hover:border-slate-300 transition-all cursor-pointer group"
            title="DTC Smart Occupancy System — Go to Overview"
          >
            <img
              src="/logo.png"
              alt="DTC Smart Occupancy System (DSOS)"
              className="w-full max-w-[210px] h-auto max-h-28 object-contain group-hover:scale-[1.01] transition-transform"
            />
          </button>
        </div>

        {/* Navigation List */}
        <div className="px-3 py-5">
          <div className="text-[11px] font-semibold text-slate-400 px-3 mb-2">
            Workspace
          </div>
          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActivePage(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all text-left cursor-pointer ${isActive
                      ? 'bg-[#1D1D1F] text-white shadow-xs'
                      : 'text-[#515154] hover:bg-[#F5F5F7] hover:text-[#1D1D1F]'
                    }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-[#86868B]'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </aside>
  );
}
