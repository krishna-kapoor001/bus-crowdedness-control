import React from 'react';
import { 
  LayoutDashboard, 
  Navigation, 
  Map, 
  Compass,
  BarChart3,
  Sliders,
  FileCode2
} from 'lucide-react';

const COMMUTER_NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'journey-planner', label: 'Route Planner', icon: Navigation },
  { id: 'network-explorer', label: 'Live Map', icon: Map },
];

const OPERATOR_NAV_ITEMS = [
  { id: 'operator-analytics', label: 'Operator Analytics', icon: BarChart3 },
  { id: 'crowd-shift', label: 'CrowdShift Simulator', icon: Sliders },
  { id: 'methodology', label: 'ML Methodology', icon: FileCode2 },
];

export default function Sidebar({ activePage, setActivePage }) {
  return (
    <aside className="w-60 bg-white border-r border-slate-200/80 flex flex-col justify-between h-screen fixed left-0 top-0 select-none z-30">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-xs">
              <Compass className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-bold text-slate-900 text-[15px] tracking-tight block leading-tight">
                BusRoute
              </span>
              <span className="text-[10px] text-slate-500 font-medium block">
                Delhi Transit Stack
              </span>
            </div>
          </div>
        </div>

        {/* Navigation List */}
        <div className="px-3 py-4 space-y-5">
          <div>
            <div className="text-[10px] font-bold text-slate-400 px-3 mb-2 uppercase tracking-wider">
              Commuter Suite
            </div>
            <nav className="space-y-1">
              {COMMUTER_NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                const isActive = activePage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActivePage(item.id)}
                    className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all text-left cursor-pointer ${
                      isActive
                        ? 'bg-slate-900 text-white shadow-xs'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 px-3 mb-2 uppercase tracking-wider">
              Transit Planners
            </div>
            <nav className="space-y-1">
              {OPERATOR_NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                const isActive = activePage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActivePage(item.id)}
                    className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all text-left cursor-pointer ${
                      isActive
                        ? 'bg-slate-900 text-white shadow-xs'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* High-end System Status Footer */}
      <div className="p-4 border-t border-slate-100">
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
          <div className="flex items-center gap-2 font-semibold text-slate-900">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
            <span>Delhi Transit Platform</span>
          </div>
          <div className="text-[10px] text-slate-500">
            2,559,899 ETM Tickets Processed
          </div>
        </div>
      </div>
    </aside>
  );
}
