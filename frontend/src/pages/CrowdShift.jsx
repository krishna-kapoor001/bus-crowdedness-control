import React, { useState } from 'react';
import { 
  Sliders, 
  RotateCcw, 
  Play, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Activity,
  BarChart3,
  ArrowRight
} from 'lucide-react';
import { runSimulation } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function CrowdShift() {
  const [demandMultiplier, setDemandMultiplier] = useState(1.15); // +15%
  const [peakShiftFactor, setPeakShiftFactor] = useState(-0.15); // 15% shift to off-peak
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const data = await runSimulation({
        demand_multiplier: demandMultiplier,
        peak_shift_factor: peakShiftFactor,
      });
      setResults(data);
      setHasRun(true);
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDemandMultiplier(1.0);
    setPeakShiftFactor(0.0);
    setResults(null);
    setHasRun(false);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-7 shadow-xs card-hover">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-800 border border-slate-200/80 uppercase tracking-wider">
            Counterfactual Simulator
          </span>
          <span className="text-xs text-slate-500 font-medium">Policy & Elasticity Testing</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          CrowdShift: Transit Policy & Demand Elasticity Simulator
        </h2>
        <p className="text-sm text-slate-500 max-w-3xl mt-1">
          Model how city-wide demand surges, fare policy changes, or peak-hour staggering policies impact corridor volume-to-capacity (V/C) ratios and commuter crowding across Delhi's arterial transit grid.
        </p>
      </div>

      {/* Control Sliders & Run Panel */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-6 card-hover">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Sliders className="w-4 h-4 text-slate-700" />
          <span>Simulation Scenario Parameters</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Slider 1: Overall Demand Multiplier */}
          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-xs font-semibold">
              <span className="text-slate-700">Network Ridership Growth Multiplier</span>
              <span className="text-slate-900 font-bold text-sm bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200">
                {(demandMultiplier * 100 - 100) >= 0 ? `+${(demandMultiplier * 100 - 100).toFixed(0)}%` : `${(demandMultiplier * 100 - 100).toFixed(0)}%`} ({demandMultiplier.toFixed(2)}x)
              </span>
            </div>
            <input 
              type="range" 
              min="0.70" 
              max="1.60" 
              step="0.05"
              value={demandMultiplier}
              onChange={(e) => setDemandMultiplier(parseFloat(e.target.value))}
              className="w-full accent-slate-900 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-30% (Severe Contraction)</span>
              <span className="font-semibold text-slate-700">1.0x (Baseline)</span>
              <span>+60% (Rapid Expansion)</span>
            </div>
          </div>

          {/* Slider 2: Peak Hour Shift Factor */}
          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-xs font-semibold">
              <span className="text-slate-700">Peak-to-Off-Peak Shift Factor</span>
              <span className="text-slate-900 font-bold text-sm bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200">
                {(peakShiftFactor * 100).toFixed(0)}%
              </span>
            </div>
            <input 
              type="range" 
              min="-0.30" 
              max="0.30" 
              step="0.05"
              value={peakShiftFactor}
              onChange={(e) => setPeakShiftFactor(parseFloat(e.target.value))}
              className="w-full accent-slate-900 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-30% (Heavy Peak Flattening)</span>
              <span className="font-semibold text-slate-700">0% (No Policy Shift)</span>
              <span>+30% (Concentrated Peak Spike)</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 pt-2">
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="px-6 py-3 bg-slate-900 hover:bg-black text-white text-xs font-semibold rounded-xl transition-all shadow-xs flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-white" />
            <span>{loading ? 'Simulating Dynamic Network...' : 'Run Simulation'}</span>
          </button>

          <button
            onClick={handleReset}
            className="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition-all flex items-center gap-1.5 cursor-pointer border border-slate-200/60"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Baseline</span>
          </button>
        </div>
      </div>

      {/* Simulation Results Display */}
      {hasRun && results && (
        <div className="space-y-6 animate-fade-in">
          {/* Top Level Summary Banner - High End Solid Dark */}
          <div className="bg-slate-900 text-white border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 card-hover">
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wide">
                Simulation Projection Outcome
              </span>
              <h3 className="text-xl font-bold text-white mt-1">
                System-Wide Passenger Flow Delta: {results.system_wide_delta_pct > 0 ? `+${results.system_wide_delta_pct}%` : `${results.system_wide_delta_pct}%`}
              </h3>
              <p className="text-xs text-slate-300 mt-1">
                Projected total daily passenger load: <span className="font-bold text-white">{results.total_simulated_demand?.toLocaleString()}</span> (from baseline {results.total_baseline_demand?.toLocaleString()}).
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <div className="p-3 bg-slate-800/80 rounded-xl border border-slate-700 text-center min-w-[120px]">
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Demand Scaling</div>
                <div className="text-base font-bold text-white font-mono mt-0.5">{demandMultiplier.toFixed(2)}x</div>
              </div>
              <div className="p-3 bg-slate-800/80 rounded-xl border border-slate-700 text-center min-w-[120px]">
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Peak Headway Shift</div>
                <div className="text-base font-bold text-white font-mono mt-0.5">{(peakShiftFactor * 100).toFixed(0)}%</div>
              </div>
            </div>
          </div>

          {/* Corridor by Corridor Impact Matrix */}
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs card-hover">
            <h3 className="text-base font-bold text-slate-900 mb-4">
              Corridor Capacity & Crowding Impact Matrix
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                    <th className="py-3 px-4">Transit Corridor</th>
                    <th className="py-3 px-4">Baseline Daily Pax</th>
                    <th className="py-3 px-4">Simulated Daily Pax</th>
                    <th className="py-3 px-4">Pax Delta (%)</th>
                    <th className="py-3 px-4">Baseline Crowd</th>
                    <th className="py-3 px-4">Simulated Crowd</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.corridors?.map((c) => {
                    const isWorse = c.delta_pct > 0;
                    return (
                      <tr 
                        key={c.corridor_name} 
                        className={`transition-colors ${
                          isWorse ? 'hover:bg-rose-50/40' : 'hover:bg-emerald-50/40'
                        }`}
                      >
                        <td className="py-3.5 px-4 font-semibold text-slate-900">{c.corridor_name}</td>
                        <td className="py-3.5 px-4 text-slate-600 font-mono">{c.baseline_daily?.toLocaleString()}</td>
                        <td className="py-3.5 px-4 font-bold text-slate-900 font-mono">{c.simulated_daily?.toLocaleString()}</td>
                        <td className="py-3.5 px-4 font-mono font-bold">
                          <span className={c.delta_pct >= 0 ? 'text-rose-700' : 'text-emerald-700'}>
                            {c.delta_pct >= 0 ? `+${c.delta_pct}%` : `${c.delta_pct}%`}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge level={c.baseline_crowd_level} size="sm" />
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge level={c.simulated_crowd_level} size="sm" />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
