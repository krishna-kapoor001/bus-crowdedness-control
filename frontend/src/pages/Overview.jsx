import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Route as RouteIcon, 
  Clock, 
  ShieldCheck, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import { fetchOverview } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function Overview({ onNavigateToJourney }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOverview()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="w-full px-4 sm:px-6 md:px-8 py-6 max-w-[1640px] mx-auto space-y-6 animate-pulse">
        <div className="h-28 bg-[#F5F5F7] rounded-2xl" />
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 bg-[#F5F5F7] rounded-2xl" />
          ))}
        </div>
        <div className="h-72 bg-[#F5F5F7] rounded-2xl" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="w-full px-4 sm:px-6 md:px-8 py-6 max-w-[1640px] mx-auto">
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs">
          Unable to load transit data: {error}
        </div>
      </div>
    );
  }

  const { kpis, demand_trends, peak_comparison, top_crowded_routes } = data;

  return (
    <div className="w-full px-4 sm:px-6 md:px-8 py-6 max-w-[1640px] mx-auto space-y-6">
      {/* 4 Core KPIs Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1 */}
        <div className="bg-white border border-black/[0.06] p-5 rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
          <div className="text-xs text-[#86868B] font-medium">Monthly Verified Volume</div>
          <div className="mt-2 text-3xl font-extrabold text-[#1D1D1F] tracking-tight">
            {kpis.estimated_passenger_demand.toLocaleString()}
          </div>
          <div className="mt-1 text-[11px] text-[#86868B]">
            October 2026 ETM Tickets
          </div>
        </div>

        {/* KPI 2 */}
        <div className="bg-white border border-black/[0.06] p-5 rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
          <div className="text-xs text-[#86868B] font-medium">Monitored Bus Routes</div>
          <div className="mt-2 text-3xl font-extrabold text-[#1D1D1F] tracking-tight">
            {kpis.analyzed_transport_routes.toLocaleString()}
          </div>
          <div className="mt-1 text-[11px] text-[#86868B]">
            DTC & Cluster Networks
          </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-white border border-black/[0.06] p-5 rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
          <div className="text-xs text-[#86868B] font-medium">Morning Peak Window</div>
          <div className="mt-2 text-2xl font-bold text-[#1D1D1F] tracking-tight">
            08:00 AM – 10:00 AM
          </div>
          <div className="mt-1 text-[11px] text-[#86868B]">
            {peak_comparison.morning_share_pct || 33.4}% of daily passenger trips
          </div>
        </div>

        {/* KPI 4 */}
        <div className="bg-white border border-slate-200/80 p-5 rounded-2xl shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Model Forecast Accuracy</div>
          <div className="mt-2 text-3xl font-extrabold text-slate-900 tracking-tight">
            {kpis.model_prediction_confidence}%
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            Validated on Out-of-Time Test Set
          </div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 24-Hour Passenger Flow Curve */}
        <div className="lg:col-span-2 bg-white border border-black/[0.06] p-6 rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-[#1D1D1F]">
                24-Hour Passenger Volume Curve
              </h3>
              <p className="text-xs text-[#86868B]">
                Hourly ticket issuance across all monitored corridors
              </p>
            </div>
            <span className="text-xs text-slate-400 font-medium font-mono">
              12:00 AM – 11:00 PM
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={demand_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis 
                  dataKey="time_label" 
                  tickFormatter={(val) => {
                    const h = parseInt(val, 10);
                    if (h === 0) return '12 AM';
                    if (h < 12) return `${h} AM`;
                    if (h === 12) return '12 PM';
                    return `${h - 12} PM`;
                  }}
                  tick={{ fontSize: 10, fill: '#64748B' }} 
                  axisLine={{ stroke: '#E2E8F0' }}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 11, fill: '#64748B' }} 
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  formatter={(val) => [`${val.toLocaleString()} passengers`, 'Estimated Load']}
                  labelFormatter={(lbl) => {
                    const h = parseInt(lbl, 10);
                    if (isNaN(h)) return lbl;
                    const ampm = h >= 12 ? 'PM' : 'AM';
                    const h12 = h % 12 === 0 ? 12 : h % 12;
                    return `${String(h12).padStart(2, '0')}:00 ${ampm}`;
                  }}
                  contentStyle={{ 
                    backgroundColor: '#FFFFFF', 
                    borderColor: '#E2E8F0', 
                    borderRadius: '8px', 
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.08)',
                    fontSize: '12px' 
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="passengers" 
                  stroke="#0F172A" 
                  strokeWidth={2} 
                  fill="#0F172A"
                  fillOpacity={0.05}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-xs text-[#86868B] pt-3 mt-2 border-t border-black/[0.04]">
            <span>Peak Hour: <strong>08:00 AM (14.6% of daily volume)</strong></span>
            <span>Evening Peak: <strong>06:00 PM (8.3% of daily volume)</strong></span>
          </div>
        </div>

        {/* Operating Window Distribution */}
        <div className="bg-white border border-black/[0.06] p-6 rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.02)] flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-[#1D1D1F]">
              Commute Windows
            </h3>
            <p className="text-xs text-[#86868B] mb-5">
              Average hourly passenger density
            </p>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-[#1D1D1F]">Morning Rush (07:00 AM – 10:00 AM)</span>
                  <span className="font-semibold text-[#1D1D1F]">{peak_comparison.morning_peak_avg.toLocaleString()} pax/hr</span>
                </div>
                <div className="w-full bg-slate-100 h-1.5 rounded-sm overflow-hidden">
                  <div className="bg-slate-900 h-full rounded-sm" style={{ width: '92%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-slate-900">Evening Rush (05:00 PM – 08:00 PM)</span>
                  <span className="font-semibold text-slate-900">{peak_comparison.evening_peak_avg.toLocaleString()} pax/hr</span>
                </div>
                <div className="w-full bg-slate-100 h-1.5 rounded-sm overflow-hidden">
                  <div className="bg-slate-700 h-full rounded-sm" style={{ width: '70%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-slate-500">Midday (11:00 AM – 03:00 PM)</span>
                  <span className="text-slate-500">{peak_comparison.midday_offpeak_avg.toLocaleString()} pax/hr</span>
                </div>
                <div className="w-full bg-slate-100 h-1.5 rounded-sm overflow-hidden">
                  <div className="bg-slate-400 h-full rounded-sm" style={{ width: '30%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-slate-500">Off-Peak / Night (10:00 PM – 05:00 AM)</span>
                  <span className="text-slate-500">{peak_comparison.night_offpeak_avg.toLocaleString()} pax/hr</span>
                </div>
                <div className="w-full bg-slate-100 h-1.5 rounded-sm overflow-hidden">
                  <div className="bg-slate-300 h-full rounded-sm" style={{ width: '8%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 p-3.5 bg-[#F5F5F7] rounded-xl text-xs text-[#515154] leading-relaxed">
            <strong className="text-[#1D1D1F] block mb-0.5">Commuter Guidance:</strong>
            Shifting departure outside the 08:00 AM – 08:45 AM peak reduces boarding crowding by up to 38%.
          </div>
        </div>
      </div>

      {/* High-Demand Bus Corridors */}
      <div className="bg-white border border-black/[0.06] rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.02)] overflow-hidden">
        <div className="p-6 border-b border-black/[0.04] flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-[#1D1D1F]">
              High-Demand Delhi Corridors
            </h3>
            <p className="text-xs text-[#86868B]">
              Top bus routes ranked by verified daily passenger volume
            </p>
          </div>
          <span className="text-xs text-[#86868B]">Top 10 Active Routes</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#F5F5F7] border-b border-black/[0.04] text-[#86868B] font-semibold">
                <th className="py-3 px-5">Rank</th>
                <th className="py-3 px-5">Route</th>
                <th className="py-3 px-5">Start – End Stops</th>
                <th className="py-3 px-5">Daily Passengers</th>
                <th className="py-3 px-5">Propulsion</th>
                <th className="py-3 px-5">Crowd Level</th>
                <th className="py-3 px-5">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.03]">
              {top_crowded_routes.map((r) => (
                <tr key={r.route_id} className="hover:bg-[#F5F5F7]/60 transition-colors">
                  <td className="py-3 px-5 font-mono text-[#86868B]">#{r.rank}</td>
                  <td className="py-3 px-5 font-bold text-[#1D1D1F]">{r.route_id}</td>
                  <td className="py-3 px-5 text-[#515154]">{r.origin} → {r.destination}</td>
                  <td className="py-3 px-5 font-mono font-semibold text-[#1D1D1F]">
                    {Math.round(r.daily_passengers).toLocaleString()} pax/day
                  </td>
                  <td className="py-3 px-5 text-slate-600">
                    {r.is_ac ? 'Electric AC' : 'Standard'}
                  </td>
                  <td className="py-3 px-5">
                    <StatusBadge level={r.crowd_category} size="sm" />
                  </td>
                  <td className="py-3 px-5 font-mono text-[#515154] font-medium">
                    {r.confidence}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
