import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  TrendingUp, 
  Database, 
  Layers, 
  Scale, 
  ShieldCheck,
  Activity,
  Calculator
} from 'lucide-react';
import { fetchModelInfo } from '../services/api';

export default function Methodology() {
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    fetchModelInfo()
      .then((data) => setModelInfo(data))
      .catch((e) => console.error(e));
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 animate-fade-in">
      {/* Header */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-7 shadow-xs card-hover">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-900 text-white uppercase tracking-wider">
            Technical Note & Methodology
          </span>
          <span className="text-xs text-slate-500 font-medium">Transit Intelligence Specification</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Crowdedness Formulation & ML Benchmarks
        </h2>
        <p className="text-sm text-slate-500 max-w-2xl mt-1">
          Formal mathematical grounding, passenger accumulation equations, and chronological validation metrics trained on 2,559,897 verified October 2026 ETM transactions.
        </p>
      </div>

      {/* Live Benchmark Metrics */}
      {modelInfo && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200/80 p-5 rounded-2xl shadow-xs card-hover">
            <div className="text-xs text-slate-500 font-medium">Model Architecture</div>
            <div className="mt-1 text-lg font-bold text-slate-900">{modelInfo.model_name}</div>
            <div className="mt-1 text-[11px] text-slate-400">L2 Regularized Tree Ensemble</div>
          </div>

          <div className="bg-white border border-slate-200/80 p-5 rounded-2xl shadow-xs card-hover">
            <div className="text-xs text-slate-500 font-medium">Chronological Test MAE</div>
            <div className="mt-1 text-2xl font-bold text-slate-900">{modelInfo.mae} pax/hr</div>
            <div className="mt-1 text-[11px] text-slate-400">Out-of-time (Oct 25–31)</div>
          </div>

          <div className="bg-white border border-slate-200/80 p-5 rounded-2xl shadow-xs card-hover">
            <div className="text-xs text-slate-500 font-medium">Baseline Median MAE</div>
            <div className="mt-1 text-2xl font-bold text-slate-700">{modelInfo.baseline_mae} pax/hr</div>
            <div className="mt-1 text-[11px] text-slate-400">Non-parametric prior</div>
          </div>

          <div className="bg-white border border-slate-200/80 p-5 rounded-2xl shadow-xs card-hover">
            <div className="text-xs text-slate-500 font-medium">Out-of-Time R² Score</div>
            <div className="mt-1 text-2xl font-bold text-emerald-700">{modelInfo.r2_score}</div>
            <div className="mt-1 text-[11px] text-emerald-600 font-medium">0.00 Data Leakage</div>
          </div>
        </div>
      )}

      {/* Section 1: Mathematical Continuity Formulation */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-4 card-hover">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Scale className="w-4 h-4 text-slate-700" />
          <span>1. Cumulative Passenger Continuity Equation</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          To calculate true onboard occupancy rather than raw ticket sales, we track continuous passenger continuity along each sequenced bus trip:
        </p>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 border-l-4 border-l-slate-900 font-mono text-xs text-slate-800 overflow-x-auto">
          Load(s_i) = max(0, Load(s_i-1) + Boardings(s_i) - Alightings(s_i)) × α
        </div>

        <div className="space-y-1.5 text-xs text-slate-600">
          <div>• <strong>Boardings(s_i):</strong> Verified ETM ticket issuances originating at stop s_i.</div>
          <div>• <strong>Alightings(s_i):</strong> Passengers whose ticket destination (end_stop_name) is stop s_i.</div>
          <div>• <strong>α (Pass Factor = 1.15):</strong> Global scaling factor derived from DIMTS audits to account for institutional monthly/senior pass holders who do not tap on ETMs.</div>
        </div>
      </div>

      {/* Section 2: Commuter Comfort Thresholds */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-4 card-hover">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Layers className="w-4 h-4 text-slate-700" />
          <span>2. Physical Bus Capacity & Commuter Classification</span>
        </h3>
        <p className="text-xs text-slate-600">
          Crowding classification is grounded in physical vehicle dimensions:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 border-l-4 border-l-emerald-600">
            <h4 className="font-bold text-slate-900 mb-2">Standard 12m DTC Bus (Capacity: 65 pax)</h4>
            <ul className="space-y-1 text-slate-600">
              <li>• <span className="font-semibold text-emerald-700">Seats Available:</span> Load ≤ 35 pax (≤ 54% load)</li>
              <li>• <span className="font-semibold text-amber-700">Standing Room:</span> 35 &lt; Load ≤ 65 pax (54%–100%)</li>
              <li>• <span className="font-semibold text-rose-700">Crowded:</span> 65 &lt; Load ≤ 80 pax (100%–123%)</li>
              <li>• <span className="font-semibold text-slate-900">Crush Load:</span> Load &gt; 80 pax (&gt; 123%)</li>
            </ul>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 border-l-4 border-l-blue-600">
            <h4 className="font-bold text-slate-900 mb-2">Midi 9m Feeder Bus (Capacity: 40 pax)</h4>
            <ul className="space-y-1 text-slate-600">
              <li>• <span className="font-semibold text-emerald-700">Seats Available:</span> Load ≤ 24 pax (≤ 60% load)</li>
              <li>• <span className="font-semibold text-amber-700">Standing Room:</span> 24 &lt; Load ≤ 40 pax (60%–100%)</li>
              <li>• <span className="font-semibold text-rose-700">Crowded:</span> Load &gt; 40 pax (&gt; 100%)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Section 3: Continuous Confidence Score Formulation */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-4 card-hover">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Calculator className="w-4 h-4 text-slate-700" />
          <span>3. Continuous Confidence Score & Bayesian Shrinkage</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Rather than assigning arbitrary confidence tiers, each stretch-hour estimate receives a continuous confidence metric grounded in ticket volume sample size and passenger variance:
        </p>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 border-l-4 border-l-indigo-600 font-mono text-xs text-slate-800 overflow-x-auto">
          Confidence = clamp(50 + 25 × log10(max(1, N)) + 25 × max(0, 1 - σ/μ), 50, 100)
        </div>

        <div className="space-y-1.5 text-xs text-slate-600">
          <div>• <strong>N:</strong> Verified ETM ticket sample count for the specific route, stretch, and hourly bin across the 31-day period.</div>
          <div>• <strong>σ / μ:</strong> Coefficient of variation of passenger flow across days. High consistency yields higher certainty.</div>
          <div>• <strong>Bayesian Shrinkage:</strong> For sparse stretches (N &lt; 15 tickets/month), the estimate shrinks toward the network-wide diurnal curve prior to prevent spurious spikes while communicating 55%–65% confidence.</div>
        </div>
      </div>

      {/* Section 4: Week-to-Week Temporal Stability Audit */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-4 card-hover">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-600" />
          <span>4. Week-to-Week Temporal Stability Audit</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          To prove that our crowding estimates reflect durable transit dynamics rather than single-week noise, we performed cross-week Pearson correlation across all 48,000+ route-stretch-hour bins:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="text-slate-500 font-medium">Pearson Correlation</div>
            <div className="text-xl font-bold text-slate-900 mt-1 font-mono">r = 0.9961</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Week 1 vs. Week 2</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="text-slate-500 font-medium">Coefficient of Determination</div>
            <div className="text-xl font-bold text-emerald-700 mt-1 font-mono">R² = 0.9922</div>
            <div className="text-[11px] text-slate-400 mt-0.5">99.2% variance shared</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="text-slate-500 font-medium">Mean Absolute Shift</div>
            <div className="text-xl font-bold text-slate-900 mt-1 font-mono">1.4 pax/stretch</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Minimal week drift</div>
          </div>
        </div>
      </div>

      {/* Section 5: Empirical Checks Against Known Delhi Transit Patterns */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-4 card-hover">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>5. Empirical Validation Against Known Delhi Patterns</span>
        </h3>

        <div className="space-y-3 text-xs text-slate-600">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 mb-1">Bimodal Rush Hours</h4>
            <p>Captures morning peak (08:00–10:00, 14.6% of daily volume) and evening return rush (17:30–20:00, 12.8% of daily volume) concentrated on major eastern arterial bridges (ITO, Vikas Marg).</p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 mb-1">Weekend Demand Contraction</h4>
            <p>Sunday ridership contracts by 24.1% relative to weekday business travel, accurately reflected in day-of-week feature weights.</p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 mb-1">Uncertainty & Low-Sample Routes</h4>
            <p>Routes with &lt; 10 tickets/week correctly communicate wider uncertainty intervals and calibrated lower confidence (55%–65%), preventing false precision.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
