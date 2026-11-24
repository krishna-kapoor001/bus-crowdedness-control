import React, { useState, useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip, Polyline, ZoomControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import {
  ArrowLeftRight,
  Search,
  Clock,
  AlarmClock,
  Calendar,
  MapPin,
  Bus,
  ArrowRight,
  Navigation,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  X,
  Copy,
  Check,
  Users,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { planJourney, fetchStops } from '../services/api';

// Bus Stop & Transit Terminal Location Pin Icons for Leaflet (Hardware Accelerated)
const createBusStopIcon = (isHub) => {
  const w = isHub ? 22 : 18;
  const h = isHub ? 28 : 23;
  const pinColor = '#2563EB'; // All intermediate route stops are consistently blue

  return L.divIcon({
    className: '!bg-transparent !border-0',
    html: `
      <div style="
        width: ${w}px;
        height: ${h}px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        pointer-events: auto;
      ">
        <svg width="${w}" height="${h}" viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="12" cy="28.5" rx="5.5" ry="1.4" fill="rgba(15,23,42,0.3)"/>
          <path d="M12 0C6.48 0 2 4.48 2 10C2 17.5 10.8 28.8 11.2 29.3C11.6 29.8 12.4 29.8 12.8 29.3C13.2 28.8 22 17.5 22 10C22 4.48 17.52 0 12 0Z" 
                fill="${pinColor}" 
                stroke="#FFFFFF" 
                stroke-width="1.8" 
                stroke-linejoin="round"/>
          <circle cx="12" cy="10" r="${isHub ? 4 : 3.2}" fill="#FFFFFF"/>
          ${isHub ? `<circle cx="12" cy="10" r="2" fill="${pinColor}"/>` : ''}
        </svg>
      </div>
    `,
    iconSize: [w, h],
    iconAnchor: [w / 2, h],
    popupAnchor: [0, -h - 2]
  });
};

const createOriginIcon = () => {
  const w = 26;
  const h = 33;
  return L.divIcon({
    className: '!bg-transparent !border-0',
    html: `
      <div style="
        width: ${w}px;
        height: ${h}px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        pointer-events: auto;
      ">
        <svg width="${w}" height="${h}" viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="12" cy="28.5" rx="6" ry="1.5" fill="rgba(5,150,105,0.35)"/>
          <path d="M12 0C6.48 0 2 4.48 2 10C2 17.5 10.8 28.8 11.2 29.3C11.6 29.8 12.4 29.8 12.8 29.3C13.2 28.8 22 17.5 22 10C22 4.48 17.52 0 12 0Z" 
                fill="#059669" 
                stroke="#FFFFFF" 
                stroke-width="2" 
                stroke-linejoin="round"/>
          <circle cx="12" cy="10" r="4.5" fill="#FFFFFF"/>
          <circle cx="12" cy="10" r="2.2" fill="#059669"/>
        </svg>
      </div>
    `,
    iconSize: [w, h],
    iconAnchor: [w / 2, h],
    popupAnchor: [0, -h - 2]
  });
};

const createDestIcon = () => {
  const w = 26;
  const h = 33;
  return L.divIcon({
    className: '!bg-transparent !border-0',
    html: `
      <div style="
        width: ${w}px;
        height: ${h}px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        pointer-events: auto;
      ">
        <svg width="${w}" height="${h}" viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="12" cy="28.5" rx="6" ry="1.5" fill="rgba(15,23,42,0.35)"/>
          <path d="M12 0C6.48 0 2 4.48 2 10C2 17.5 10.8 28.8 11.2 29.3C11.6 29.8 12.4 29.8 12.8 29.3C13.2 28.8 22 17.5 22 10C22 4.48 17.52 0 12 0Z" 
                fill="#0F172A" 
                stroke="#FFFFFF" 
                stroke-width="2" 
                stroke-linejoin="round"/>
          <circle cx="12" cy="10" r="4.5" fill="#FFFFFF"/>
          <circle cx="12" cy="10" r="2.2" fill="#0F172A"/>
        </svg>
      </div>
    `,
    iconSize: [w, h],
    iconAnchor: [w / 2, h],
    popupAnchor: [0, -h - 2]
  });
};

// Inline SVG Teardrop Transit Map Pin matching Leaflet live map exactly
function StopMapPin({ type = 'stop', isHub = false }) {
  const isStart = type === 'origin';
  const isDest = type === 'dest';
  const color = isStart ? '#059669' : isDest ? '#0F172A' : '#2563EB';
  const w = isStart || isDest ? 16 : 14;
  const h = isStart || isDest ? 20 : 18;

  return (
    <svg
      width={w}
      height={h}
      viewBox="0 0 24 30"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0 drop-shadow-xs"
    >
      <path
        d="M12 0C6.48 0 2 4.48 2 10C2 17.5 10.8 28.8 11.2 29.3C11.6 29.8 12.4 29.8 12.8 29.3C13.2 28.8 22 17.5 22 10C22 4.48 17.52 0 12 0Z"
        fill={color}
        stroke="#FFFFFF"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="10" r="4" fill="#FFFFFF" />
      <circle cx="12" cy="10" r="2" fill={color} />
    </svg>
  );
}

// Smooth Map Bounds Controller to auto-fit route in view and prevent gray tiles
function MapBoundsController({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points && points.length >= 2) {
      try {
        map.invalidateSize();
        const bounds = points.map(p => [p[0], p[1]]);
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14, animate: true });
      } catch (e) {
        // Fallback safely if map is not ready
      }
    }
  }, [points, map]);
  return null;
}

function formatTime12H(val24) {
  if (!val24) return '08:30 AM';
  const parts = val24.split(':');
  let h = parseInt(parts[0], 10);
  const m = parts[1] || '00';
  if (isNaN(h)) h = 8;
  const ampm = h >= 12 ? 'PM' : 'AM';
  let h12 = h % 12;
  if (h12 === 0) h12 = 12;
  return `${String(h12).padStart(2, '0')}:${m} ${ampm}`;
}

const DEPARTURE_TIME_OPTIONS = (() => {
  const list = [];
  for (let h = 5; h <= 23; h++) {
    for (let m = 0; m < 60; m += 15) {
      const hStr = String(h).padStart(2, '0');
      const mStr = String(m).padStart(2, '0');
      const val = `${hStr}:${mStr}`;
      list.push({ value: val, label: formatTime12H(val) });
    }
  }
  return list;
})();

function parseTo12Hour(timeStr) {
  if (!timeStr) return { hour: '', minute: '', ampm: '', display: '--:--' };
  const raw = String(timeStr).trim();
  const isPM = raw.toLowerCase().includes('pm');
  const isAM = raw.toLowerCase().includes('am');
  const cleaned = raw.toLowerCase().replace(/am|pm/g, '').trim();
  const parts = cleaned.split(':');
  let h = parseInt(parts[0], 10);
  let m = parts[1] || '00';
  if (isNaN(h)) return { hour: '', minute: '', ampm: '', display: '--:--' };
  if (m.length === 1) m = '0' + m;

  let ampm = '';
  if (isPM) {
    ampm = 'PM';
  } else if (isAM) {
    ampm = 'AM';
  } else {
    ampm = h >= 12 ? 'PM' : 'AM';
  }

  let h12 = h % 12;
  if (h12 === 0) h12 = 12;
  const hStr = String(h12).padStart(2, '0');
  const mClean = m.slice(0, 2);
  return {
    hour: hStr,
    minute: mClean,
    ampm,
    display: `${hStr}:${mClean} ${ampm}`
  };
}

function to24Hour(hour12, minute, ampm) {
  let h = parseInt(hour12, 10);
  if (isNaN(h)) h = 8;
  const safeAmpm = ampm || 'AM';
  if (safeAmpm === 'PM' && h < 12) h += 12;
  if (safeAmpm === 'AM' && h === 12) h = 0;
  const safeMinute = minute || '00';
  return `${String(h).padStart(2, '0')}:${safeMinute}`;
}

// Delhi Transit All 7 Days of the Week
const DAYS_OF_WEEK = [
  { id: 'monday', label: 'Monday', short: 'Mon', rushHint: 'Office Return Rush' },
  { id: 'tuesday', label: 'Tuesday', short: 'Tue', rushHint: 'Steady Commute Flow' },
  { id: 'wednesday', label: 'Wednesday', short: 'Wed', rushHint: 'Mid-Week Steady Transit' },
  { id: 'thursday', label: 'Thursday', short: 'Thu', rushHint: 'Peak Commute Rush' },
  { id: 'friday', label: 'Friday', short: 'Fri', rushHint: 'Pre-Weekend Rush' },
  { id: 'saturday', label: 'Saturday', short: 'Sat', rushHint: 'Commercial & Market Traffic' },
  { id: 'sunday', label: 'Sunday', short: 'Sun', rushHint: 'Leisure Day • Guaranteed Seats' },
];

function getLiveDayOfWeek() {
  const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  return dayNames[new Date().getDay()] || 'monday';
}

function getLiveTime() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, '0');
  const m = String(Math.floor(now.getMinutes() / 5) * 5).padStart(2, '0');
  return `${h}:${m}`;
}

export default function JourneyPlanner() {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departureTime, setDepartureTime] = useState('');
  const [dayType, setDayType] = useState('');
  const [preferLessCrowded, setPreferLessCrowded] = useState(false);

  const [stopsList, setStopsList] = useState([]);
  const [originOpen, setOriginOpen] = useState(false);
  const [destOpen, setDestOpen] = useState(false);

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAlternativeId, setSelectedAlternativeId] = useState(null);
  const [showStopsTimeline, setShowStopsTimeline] = useState(true);
  const [copied, setCopied] = useState(false);

  // Load stops
  useEffect(() => {
    fetchStops()
      .then((stops) => setStopsList(stops))
      .catch(() => { });
  }, []);

  // Intelligent search restricted strictly to Delhi Bus Stands, Terminals, Depots & ISBTs
  const getStopSuggestions = (inputText) => {
    if (!stopsList || stopsList.length === 0) return [];
    const text = (inputText || '').trim().toLowerCase();
    const busStands = stopsList.filter((s) => s.is_major_hub);

    if (!text) {
      // Show verified Delhi Bus Stands & Terminals
      return busStands;
    }
    const isBusStandQuery = ['bus stand', 'stand', 'busstand', 'bus-stand', 'bus stands', 'terminal', 'terminals', 'hub', 'hubs'].some((k) => text.includes(k));
    const tokens = text.split(/\s+/).filter(Boolean);

    const scored = [];
    for (const stop of busStands) {
      const name = (stop.name || '').toLowerCase();
      const corridor = (stop.corridor || '').toLowerCase();
      const combined = `${name} ${corridor} bus stand terminal major hub isbt depot`;

      const matchesSearch = isBusStandQuery || tokens.every((tok) => combined.includes(tok));
      if (!matchesSearch) continue;

      let score = 0;
      if (name === text) {
        score += 10000;
      } else if (name.startsWith(text)) {
        score += 5000;
      } else if (name.includes(text)) {
        score += 2000;
      }

      score += Math.min((stop.monthly_boardings || 0) / 1000, 500);

      scored.push({ stop, score });
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.map((item) => item.stop);
  };

  const filteredOriginStops = useMemo(() => getStopSuggestions(origin), [origin, stopsList]);
  const filteredDestStops = useMemo(() => getStopSuggestions(destination), [destination, stopsList]);

  const handleSwap = () => {
    const newOrig = destination;
    const newDest = origin;
    setOrigin(newOrig);
    setDestination(newDest);
    if (results && departureTime && dayType) {
      handleSearch(null, newOrig, newDest, departureTime, dayType);
    }
  };

  const handleTogglePreference = (checked) => {
    setPreferLessCrowded(checked);
    if (results && departureTime && dayType) {
      setLoading(true);
      planJourney({
        origin: (results.origin || origin).trim(),
        destination: (results.destination || destination).trim(),
        departure_time: departureTime,
        day_type: dayType,
        prefer_less_crowded: checked,
      })
        .then((data) => {
          setResults(data);
          setSelectedAlternativeId(null);
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  };

  const handleSearch = async (e, customOrig, customDest, customTime, customDay) => {
    if (e && e.preventDefault) e.preventDefault();
    const origToUse = (customOrig || origin).trim();
    const destToUse = (customDest || destination).trim();
    const timeToUse = customTime !== undefined ? customTime : departureTime;
    const dayToUse = customDay !== undefined ? customDay : dayType;

    // Strict validation: From, To, Time, and Day must all be explicitly chosen
    if (!origToUse || !destToUse) {
      setError('Please select both starting bus stand (From) and destination (To).');
      return;
    }

    if (origToUse.toLowerCase() === destToUse.toLowerCase()) {
      setError('Starting bus stand and destination cannot be the same. Please choose two different locations.');
      setResults(null);
      return;
    }

    if (!timeToUse && !dayToUse) {
      setError('Please select both Departure Time and Travel Day before finding routes.');
      return;
    }

    if (!timeToUse) {
      setError('Please select your Departure Time (Hour, Minute and AM/PM).');
      return;
    }

    if (!dayToUse) {
      setError('Please select a Travel Day (Monday – Sunday).');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await planJourney({
        origin: origToUse,
        destination: destToUse,
        departure_time: timeToUse,
        day_type: dayToUse,
        prefer_less_crowded: preferLessCrowded,
      });
      setResults(data);
      setSelectedAlternativeId(null);
    } catch (err) {
      setError(err.message || 'Error finding routes');
    } finally {
      setLoading(false);
    }
  };

  const selectedAlt = results?.alternatives?.find((a) => a.id === selectedAlternativeId) || results?.alternatives?.[0];

  const handleCopyItinerary = () => {
    if (!selectedAlt) return;
    const origName = results?.origin || origin;
    const destName = results?.destination || destination;
    const text = [
      `DELHI TRANSIT ITINERARY`,
      `========================`,
      `From:        ${origName} (Departs ${selectedAlt.departure_time_label || departureTime})`,
      `To:          ${destName} (ETA ${selectedAlt.arrival_time_label || 'Arrival'})`,
      `Duration:    ${selectedAlt.total_duration_mins} mins • ${selectedAlt.distance_km || '12.3'} km (${selectedAlt.stops_count ?? 4} stops in between)`,
      `Route:       Bus ${selectedAlt.bus_routes.join(' → ')}`,
      `Crowd Level: ${selectedAlt.comfort_label || 'Moderate'}`,
      `Bus Type:    ${selectedAlt.bus_fleet_type || 'DTC AC Electric'}`,
      `Next Bus:    Every ~${selectedAlt.estimated_waiting_time_mins || 4} mins`,
      `========================`,
      `Generated by DTC Smart Occupancy System (DSOS) • Delhi Transport Stack`
    ].join('\n');

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="w-full px-4 sm:px-6 md:px-8 py-6 max-w-[1640px] mx-auto space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Route Planner
        </h2>
      </div>

      {/* Main Search Panel */}
      <div className="bg-white border border-slate-200/90 p-6 rounded-2xl shadow-xs">
        <form onSubmit={handleSearch} className="space-y-5">
          {/* Symmetrical From-Swap-To Layout */}
          <div className="flex flex-col md:flex-row items-stretch md:items-end gap-3">
            {/* Origin Stop */}
            <div className="flex-1 relative">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                From
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
                <input
                  type="text"
                  value={origin}
                  onChange={(e) => {
                    setOrigin(e.target.value);
                    setOriginOpen(true);
                  }}
                  onFocus={() => setOriginOpen(true)}
                  onBlur={() => setTimeout(() => setOriginOpen(false), 200)}
                  placeholder="Starting bus stand or terminal..."
                  className="w-full pl-10 pr-9 py-2.5 bg-slate-50 border border-slate-200 focus:border-slate-900 focus:bg-white rounded-xl text-sm text-slate-900 outline-none transition-colors"
                />
                {origin && (
                  <button
                    type="button"
                    onClick={() => {
                      setOrigin('');
                      setOriginOpen(true);
                    }}
                    title="Clear starting stand"
                    className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                {/* Symmetrical In-Place Suggestions Dropdown */}
                {originOpen && (
                  <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto divide-y divide-slate-100">
                    {filteredOriginStops.length > 0 ? (
                      filteredOriginStops.map((stop) => (
                        <div
                          key={stop.id}
                          onMouseDown={() => {
                            setOrigin(stop.name);
                            setOriginOpen(false);
                          }}
                          className="px-4 py-2.5 hover:bg-slate-50 transition-colors flex items-center justify-between cursor-pointer"
                        >
                          <div>
                            <span className="font-semibold text-xs text-slate-900 block">{stop.name}</span>
                          </div>
                          <span className="text-[10px] font-semibold bg-slate-900 text-white px-2 py-0.5 rounded-full shrink-0 ml-2">Bus Stand</span>
                        </div>
                      ))
                    ) : (
                      <div className="px-4 py-3 text-xs text-slate-400 text-center">
                        No bus stand found matching "{origin}"
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Swap Button */}
            <div className="flex justify-center md:pb-0.5">
              <button
                type="button"
                onClick={handleSwap}
                title="Swap origin and destination"
                className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 flex items-center justify-center text-slate-600 hover:text-slate-900 transition-colors cursor-pointer shrink-0"
              >
                <ArrowLeftRight className="w-4 h-4" />
              </button>
            </div>

            {/* Destination Stop */}
            <div className="flex-1 relative">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                To
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
                <input
                  type="text"
                  value={destination}
                  onChange={(e) => {
                    setDestination(e.target.value);
                    setDestOpen(true);
                  }}
                  onFocus={() => setDestOpen(true)}
                  onBlur={() => setTimeout(() => setDestOpen(false), 200)}
                  placeholder="Destination bus stand or terminal..."
                  className="w-full pl-10 pr-9 py-2.5 bg-slate-50 border border-slate-200 focus:border-slate-900 focus:bg-white rounded-xl text-sm text-slate-900 outline-none transition-colors"
                />
                {destination && (
                  <button
                    type="button"
                    onClick={() => {
                      setDestination('');
                      setDestOpen(true);
                    }}
                    title="Clear destination stand"
                    className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                {/* Symmetrical In-Place Suggestions Dropdown */}
                {destOpen && (
                  <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto divide-y divide-slate-100">
                    {filteredDestStops.length > 0 ? (
                      filteredDestStops.map((stop) => (
                        <div
                          key={stop.id}
                          onMouseDown={() => {
                            setDestination(stop.name);
                            setDestOpen(false);
                          }}
                          className="px-4 py-2.5 hover:bg-slate-50 transition-colors flex items-center justify-between cursor-pointer"
                        >
                          <div>
                            <span className="font-semibold text-xs text-slate-900 block">{stop.name}</span>
                          </div>
                          <span className="text-[10px] font-semibold bg-slate-900 text-white px-2 py-0.5 rounded-full shrink-0 ml-2">Bus Stand</span>
                        </div>
                      ))
                    ) : (
                      <div className="px-4 py-3 text-xs text-slate-400 text-center">
                        No bus stand found matching "{destination}"
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Departure & Optimization Bar */}
          <div className="pt-3.5 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2.5">
              {/* Minimalist Figma-Grade Departure Time Controller */}
              {(() => {
                const parsedTime = parseTo12Hour(departureTime);
                return (
                  <div className={`inline-flex items-center bg-slate-50 border rounded-xl p-1 gap-2 shadow-2xs transition-all ${
                    error && !departureTime ? 'border-rose-400 ring-1 ring-rose-200' : 'border-slate-200'
                  }`}>
                    {/* Left Label Chip */}
                    <div className="flex items-center gap-1.5 pl-2 pr-1 text-slate-700">
                      <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="text-xs font-semibold tracking-tight">Departure</span>
                    </div>

                    {/* Micro Hairline Divider */}
                    <div className="w-px h-4 bg-slate-200 shrink-0" />

                    {/* Digital Alarm Time Display Tiles [ 08 ] : [ 30 ] */}
                    <div className="flex items-center gap-1">
                      {/* Hour Interactive Tile */}
                      <div className="relative w-8 h-7 bg-white rounded-lg border border-slate-200 hover:border-slate-400 shadow-2xs flex items-center justify-center font-mono text-xs transition-colors cursor-pointer group">
                        <span className={`pointer-events-none transition-colors ${parsedTime.hour ? 'text-slate-900 group-hover:text-black font-bold' : 'text-slate-400 font-normal'}`}>
                          {parsedTime.hour || '--'}
                        </span>
                        <select
                          value={parsedTime.hour || ''}
                          onChange={(e) => {
                            const hVal = e.target.value;
                            if (!hVal) return;
                            const mVal = parsedTime.minute || '00';
                            const ampmVal = parsedTime.ampm || 'AM';
                            const newTime = to24Hour(hVal, mVal, ampmVal);
                            setDepartureTime(newTime);
                            setError(null);
                            if (results && dayType) {
                              handleSearch(null, null, null, newTime, dayType);
                            }
                          }}
                          className="clean-time-select absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                          title="Select Hour"
                        >
                          <option value="">--</option>
                          {Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0')).map((h) => (
                            <option key={h} value={h}>{h}</option>
                          ))}
                        </select>
                      </div>

                      {/* Crisp Colon */}
                      <span className="font-mono font-bold text-slate-400 text-xs select-none px-0.5">:</span>

                      {/* Minute Interactive Tile */}
                      <div className="relative w-8 h-7 bg-white rounded-lg border border-slate-200 hover:border-slate-400 shadow-2xs flex items-center justify-center font-mono text-xs transition-colors cursor-pointer group">
                        <span className={`pointer-events-none transition-colors ${parsedTime.minute ? 'text-slate-900 group-hover:text-black font-bold' : 'text-slate-400 font-normal'}`}>
                          {parsedTime.minute || '--'}
                        </span>
                        <select
                          value={parsedTime.minute || ''}
                          onChange={(e) => {
                            const mVal = e.target.value;
                            if (!mVal) return;
                            const hVal = parsedTime.hour || '08';
                            const ampmVal = parsedTime.ampm || 'AM';
                            const newTime = to24Hour(hVal, mVal, ampmVal);
                            setDepartureTime(newTime);
                            setError(null);
                            if (results && dayType) {
                              handleSearch(null, null, null, newTime, dayType);
                            }
                          }}
                          className="clean-time-select absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                          title="Select Minute"
                        >
                          <option value="">--</option>
                          {['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'].map((m) => (
                            <option key={m} value={m}>{m}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Micro Hairline Divider */}
                    <div className="w-px h-4 bg-slate-200 shrink-0" />

                    {/* Segmented AM / PM Switch */}
                    <div className="inline-flex items-center bg-slate-200/70 p-0.5 rounded-lg gap-0.5">
                      <button
                        type="button"
                        onClick={() => {
                          const hVal = parsedTime.hour || '08';
                          const mVal = parsedTime.minute || '00';
                          const newTime = to24Hour(hVal, mVal, 'AM');
                          setDepartureTime(newTime);
                          setError(null);
                          if (results && dayType) {
                            handleSearch(null, null, null, newTime, dayType);
                          }
                        }}
                        className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                          parsedTime.ampm === 'AM'
                            ? 'bg-slate-900 text-white font-bold shadow-2xs'
                            : 'text-slate-500 hover:text-slate-900'
                        }`}
                      >
                        AM
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          const hVal = parsedTime.hour || '12';
                          const mVal = parsedTime.minute || '00';
                          const newTime = to24Hour(hVal, mVal, 'PM');
                          setDepartureTime(newTime);
                          setError(null);
                          if (results && dayType) {
                            handleSearch(null, null, null, newTime, dayType);
                          }
                        }}
                        className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                          parsedTime.ampm === 'PM'
                            ? 'bg-slate-900 text-white font-bold shadow-2xs'
                            : 'text-slate-500 hover:text-slate-900'
                        }`}
                      >
                        PM
                      </button>
                    </div>
                  </div>
                );
              })()}

              {/* Clean Figma-Grade Day Controller (All 7 Days: Mon-Sun) */}
              <div className={`inline-flex items-center bg-slate-50 border rounded-xl p-1 gap-2 shadow-2xs transition-all ${
                error && !dayType ? 'border-rose-400 ring-1 ring-rose-200' : 'border-slate-200'
              }`}>
                {/* Left Label Chip */}
                <div className="flex items-center gap-1.5 pl-2 pr-1 text-slate-700">
                  <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="text-xs font-semibold tracking-tight">Day</span>
                </div>

                {/* Hairline Divider */}
                <div className="w-px h-4 bg-slate-200 shrink-0" />

                {/* Select Dropdown with All 7 Days */}
                <div className="relative">
                  <select
                    value={dayType || ''}
                    onChange={(e) => {
                      const newDay = e.target.value;
                      setDayType(newDay);
                      setError(null);
                      if (newDay && results && departureTime) {
                        handleSearch(null, null, null, departureTime, newDay);
                      }
                    }}
                    className="appearance-none bg-white hover:bg-slate-50 border border-slate-200 hover:border-slate-300 rounded-lg text-xs font-bold text-slate-900 shadow-2xs pl-3 pr-8 py-1 cursor-pointer transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500 capitalize"
                    title="Select Day of the Week"
                  >
                    <option value="">Select Day</option>
                    {DAYS_OF_WEEK.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400 pointer-events-none absolute right-2 top-1/2 -translate-y-1/2" />
                </div>

                {/* Quick 1-Click Day Buttons for all 7 days (Mon to Sun) */}
                <div className="hidden sm:inline-flex items-center bg-slate-200/70 p-0.5 rounded-lg gap-0.5">
                  {DAYS_OF_WEEK.map((d) => {
                    const isSelected = Boolean(dayType && dayType === d.id);
                    return (
                      <button
                        key={d.id}
                        type="button"
                        onClick={() => {
                          const nextDay = dayType === d.id ? '' : d.id;
                          setDayType(nextDay);
                          setError(null);
                          if (nextDay && results && departureTime) {
                            handleSearch(null, null, null, departureTime, nextDay);
                          }
                        }}
                        className={`px-2 py-0.5 rounded-md text-xs font-semibold antialiased transition-all cursor-pointer ${
                          isSelected
                            ? 'bg-slate-900 text-white font-bold shadow-2xs'
                            : 'text-slate-800 hover:text-black font-semibold'
                        }`}
                        title={`${d.label}: ${d.rushHint}`}
                      >
                        {d.short}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Right: Symmetrically Matched Find Routes Button */}
            <div>
              <button
                type="submit"
                disabled={loading}
                className="h-9 px-5 bg-slate-900 hover:bg-black text-white text-xs font-semibold rounded-xl shadow-2xs hover:shadow-xs transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70 shrink-0 min-w-[110px]"
              >
                {loading ? (
                  <Loader2 className="w-3.5 h-3.5 text-white animate-spin shrink-0" />
                ) : (
                  <Search className="w-3.5 h-3.5 text-slate-300 shrink-0" />
                )}
                <span>Find Routes</span>
              </button>
            </div>
          </div>
        </form>
      </div>

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center gap-2.5 shadow-2xs animate-in fade-in">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* Results View */}
      {results && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2.5 flex-wrap">
              <h3 className="text-base font-bold text-slate-900">
                Trip Options for {parseTo12Hour(results.departure_time).display}
              </h3>
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1.5 shadow-2xs">
                <Calendar className="w-3 h-3 text-slate-400" />
                <span className="capitalize">{dayType ? `${dayType} Schedule` : 'Standard Schedule'}</span>
              </span>
            </div>
          </div>

          {/* Night / Off-Hours Operational Service Alert */}
          {results.service_alert && (
            <div className="p-3.5 bg-rose-50/90 border border-rose-200 rounded-xl text-xs text-rose-900 flex items-start gap-2.5 shadow-2xs">
              <Clock className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold block text-rose-950">Late Night Service Closed (Empirical ETM Schedule)</strong>
                <span className="text-rose-800">{results.service_alert}</span>
              </div>
            </div>
          )}

          {/* Cards Grid: Clean Minimalist Transit Styling */}
          {(() => {
            const displayedAlts = results.alternatives;
            return (
              <div className={`grid grid-cols-1 md:grid-cols-2 ${displayedAlts.length === 3 ? 'lg:grid-cols-3' : displayedAlts.length >= 4 ? 'lg:grid-cols-4' : 'lg:grid-cols-2 max-w-4xl'} gap-4`}>
                {displayedAlts.map((alt, idx) => {
                  const isSelected = selectedAlternativeId === alt.id || (!selectedAlternativeId && alt.id === displayedAlts[0]?.id);

                  return (
                    <div
                      key={alt.id}
                      onClick={() => setSelectedAlternativeId(alt.id)}
                      className={`bg-white p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${isSelected
                        ? 'border-slate-900 ring-1.5 ring-slate-900 shadow-sm'
                        : 'border-slate-200 hover:border-slate-300 hover:shadow-xs'
                        }`}
                    >
                      <div className="space-y-3">
                        {/* Header Row: Option Number Badge */}
                        <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 gap-2">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-900 text-white rounded-lg text-xs font-bold shrink-0 shadow-2xs">
                              <Bus className="w-3.5 h-3.5 text-slate-300" />
                              Option {idx + 1}
                            </span>
                          </div>

                          {alt.service_status === "CLOSED_FOR_NIGHT" && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md whitespace-nowrap shrink-0 shadow-2xs bg-rose-900 text-white ring-1 ring-rose-700/50">
                              Closed
                            </span>
                          )}
                          {alt.service_status === "NOT_STARTED" && (
                            <span className="text-[10px] font-medium px-2 py-0.5 rounded-md whitespace-nowrap shrink-0 shadow-2xs bg-amber-50 text-amber-800 ring-1 ring-amber-300">
                              Starts {alt.first_bus_time || alt.departure_time_label}
                            </span>
                          )}
                        </div>

                        {/* Timetable Schedule: Departure -> Arrival with ETA */}
                        <div className="space-y-1">
                          <div className="flex items-center justify-between whitespace-nowrap">
                            <div className="flex items-center gap-1.5 sm:gap-2 font-mono text-[13px] sm:text-[14px] font-bold text-slate-900 tracking-tight">
                              <span>{(alt.departure_time_label || '08:30 AM').replace(/^Tomorrow\s+/i, '')}</span>
                              <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                              <span>{(alt.arrival_time_label || '09:06 AM').replace(/^Tomorrow\s+/i, '')}</span>
                            </div>
                            {alt.service_status === "CLOSED_FOR_NIGHT" ? (
                              <span className="text-[10px] font-bold text-rose-700 font-sans tracking-wide">
                                Next Trip
                              </span>
                            ) : (
                              <span className="text-[10px] font-black text-slate-400 tracking-wider uppercase select-none font-mono">
                                ETA
                              </span>
                            )}
                          </div>

                          {/* Duration, Distance & Stops Count */}
                          <div className="flex items-center justify-between text-xs pt-0.5">
                            <div className="flex items-baseline gap-1.5">
                              <span className="font-bold text-slate-900 font-mono text-[13px]">
                                {alt.total_duration_mins} mins
                              </span>
                              {alt.distance_km && (
                                <span className="font-normal text-slate-400 text-xs font-sans">
                                  ({alt.distance_km} km)
                                </span>
                              )}
                            </div>
                            <span className="text-slate-500 font-medium text-xs whitespace-nowrap">
                              {alt.stops_count === 0
                                ? 'Non-stop'
                                : `${alt.stops_count} stops`}
                            </span>
                          </div>

                          {/* Route Operating Hours from ETM Data */}
                          <div className="pt-2 border-t border-slate-100 text-[11px]">
                            <div className="flex items-center justify-between gap-1">
                              <span className="flex items-center gap-1 text-slate-500 font-medium shrink-0">
                                <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                                <span>Runs</span>
                              </span>
                              <span className="font-mono font-semibold text-slate-800 truncate text-right whitespace-nowrap">
                                {(alt.operating_hours || '06:00 AM – 10:30 PM').split('(')[0].trim()}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Bus Fleet Category & Seating Box */}
                        <div className="flex items-center justify-between py-2 px-3 bg-slate-50 border border-slate-100 rounded-xl text-xs">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <Bus className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                            <span className="font-semibold text-slate-800 text-[11.5px] truncate">
                              {alt.bus_fleet_type || 'DTC AC Electric'}
                            </span>
                          </div>
                          <span className="text-[11px] font-semibold text-slate-600 font-mono whitespace-nowrap ml-2 shrink-0">
                            {alt.seating_capacity || 35} seats
                          </span>
                        </div>
                      </div>

                      {/* Clean Bottom Footer */}
                      <div className="pt-2.5 mt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                        <span className="text-[11px] text-slate-400 font-medium">
                          {alt.total_capacity || 65} pax cap
                        </span>
                        <span className={`font-semibold text-xs ${isSelected ? 'text-blue-600' : 'text-slate-500 hover:text-slate-800'}`}>
                          {isSelected ? 'Viewing map ↓' : 'View map ↓'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}

          {/* Selected Alternative Complete Schedule & Timetable */}
          {selectedAlt && (() => {
            const getCoordinatesForStop = (stopName) => {
              if (!stopName) return [28.6139, 77.2090];
              const clean = stopName.toLowerCase().trim();

              let match = stopsList.find((s) => s.name.toLowerCase() === clean);
              if (match?.latitude && match?.longitude) return [match.latitude, match.longitude];

              match = stopsList.find((s) => s.name.toLowerCase().includes(clean) || clean.includes(s.name.toLowerCase()));
              if (match?.latitude && match?.longitude) return [match.latitude, match.longitude];

              if (clean.includes('anand')) return [28.6502, 77.3155];
              if (clean.includes('shivaji') || clean.includes('connaught') || clean.includes('cp')) return [28.6327, 77.2195];
              if (clean.includes('saket')) return [28.5204, 77.2015];
              if (clean.includes('dhaula')) return [28.5921, 77.1615];
              if (clean.includes('kashmere')) return [28.6675, 77.2285];
              if (clean.includes('aiims')) return [28.5672, 77.2100];
              if (clean.includes('badarpur')) return [28.4975, 77.3025];
              return [28.6139, 77.2090];
            };

            const origStopName = results?.origin || origin;
            const destStopName = results?.destination || destination;

            const timelineStops = selectedAlt.timeline_stops && selectedAlt.timeline_stops.length > 0
              ? selectedAlt.timeline_stops
              : [
                {
                  stop_sequence: 1,
                  stop_name: origStopName,
                  eta_time: selectedAlt.departure_time_label || departureTime,
                  mins_from_start: 0,
                  distance_km: 0.0,
                  hop_distance_km: 0.0,
                  crowd_level: 'LOW'
                },
                {
                  stop_sequence: 2,
                  stop_name: destStopName,
                  eta_time: selectedAlt.arrival_time_label || '09:18 AM',
                  mins_from_start: selectedAlt.total_duration_mins,
                  distance_km: selectedAlt.distance_km || 12.3,
                  hop_distance_km: selectedAlt.distance_km || 12.3,
                  crowd_level: 'LOW'
                }
              ];

            const origCoords = (timelineStops[0]?.latitude && timelineStops[0]?.longitude)
              ? [timelineStops[0].latitude, timelineStops[0].longitude]
              : getCoordinatesForStop(origStopName);
            const destCoords = (timelineStops[timelineStops.length - 1]?.latitude && timelineStops[timelineStops.length - 1]?.longitude)
              ? [timelineStops[timelineStops.length - 1].latitude, timelineStops[timelineStops.length - 1].longitude]
              : getCoordinatesForStop(destStopName);

            const routePoints = selectedAlt.route_coordinates && selectedAlt.route_coordinates.length > 1
              ? selectedAlt.route_coordinates
              : [origCoords, destCoords];

            const mapCenter = [
              (origCoords[0] + destCoords[0]) / 2,
              (origCoords[1] + destCoords[1]) / 2
            ];

            return (
              <div className="bg-white border border-slate-200/90 p-6 rounded-2xl shadow-xs space-y-6">
                {/* Route Map Section */}
                <div className="space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                    <Navigation className="w-3.5 h-3.5 text-slate-500" />
                    <span>Physical Route Map</span>
                  </div>

                  <div className="h-72 rounded-xl overflow-hidden border border-slate-200 relative">
                    <MapContainer
                      center={mapCenter}
                      zoom={12}
                      scrollWheelZoom={true}
                      zoomControl={false}
                      attributionControl={false}
                      preferCanvas={true}
                      wheelDebounceTime={15}
                      wheelPxPerZoomLevel={120}
                      zoomSnap={0.5}
                      zoomDelta={0.5}
                      zoomAnimation={true}
                      markerZoomAnimation={true}
                      fadeAnimation={true}
                      style={{ height: '100%', width: '100%' }}
                    >
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        maxZoom={19}
                        updateWhenZooming={false}
                        updateInterval={100}
                        keepBuffer={4}
                      />
                      <ZoomControl position="topright" />
                      <MapBoundsController points={routePoints} />

                      {/* Physical Road Route Underlay Shadow */}
                      <Polyline
                        positions={routePoints}
                        pathOptions={{
                          color: '#0F172A',
                          weight: 7,
                          opacity: 0.22,
                          lineCap: 'round',
                          lineJoin: 'round'
                        }}
                      />
                      {/* Main Street-Snapped Bus Route */}
                      <Polyline
                        positions={routePoints}
                        pathOptions={{
                          color: selectedAlt.crowd_level === 'HIGH' ? '#E11D48' : (selectedAlt.crowd_level === 'LOW' ? '#059669' : '#2563EB'),
                          weight: 4.5,
                          opacity: 0.95,
                          lineCap: 'round',
                          lineJoin: 'round'
                        }}
                      />

                      {/* Intermediate Physical Roadside Bus Stops */}
                      {timelineStops.slice(1, -1).map((st, idx) => {
                        const stCoords = (st.latitude && st.longitude)
                          ? [st.latitude, st.longitude]
                          : getCoordinatesForStop(st.stop_name);
                        return (
                          <Marker
                            key={`intermediate-stop-${idx}-${st.stop_sequence}-${st.stop_name}`}
                            position={stCoords}
                            icon={createBusStopIcon(st.is_major_hub)}
                          >
                            <Tooltip direction="top" offset={[0, -25]}>
                              <div className="text-xs font-semibold">
                                {st.stop_name} • <span className="font-mono">{st.eta_time}</span> ({Number(st.distance_km).toFixed(1)} km)
                              </div>
                            </Tooltip>
                            <Popup>
                              <div className="text-xs p-1.5 space-y-1.5 min-w-[185px]">
                                <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1">
                                  <strong className="block text-slate-900 font-bold">{st.stop_name}</strong>
                                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider ${st.is_major_hub ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'}`}>
                                    {st.is_major_hub ? 'Major Hub' : 'Bus Stop'}
                                  </span>
                                </div>
                                <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600">
                                  <div>ETA: <strong className="text-slate-900 font-mono block">{st.eta_time}</strong></div>
                                  <div>Dist: <strong className="text-slate-900 font-mono block">{Number(st.distance_km).toFixed(1)} km</strong></div>
                                </div>
                                {st.hop_distance_km !== undefined && (
                                  <div className="text-[10px] text-slate-500 font-mono">
                                    Hop: +{Number(st.hop_distance_km).toFixed(1)} km from prev stop
                                  </div>
                                )}
                                <div className="pt-1 border-t border-slate-100 text-[10px] text-slate-500 flex justify-between">
                                  <span>Passenger Load:</span>
                                  <span className={`font-semibold ${st.crowd_level === 'HIGH' ? 'text-rose-600' : (st.crowd_level === 'LOW' ? 'text-emerald-600' : 'text-amber-600')}`}>
                                    {st.seats_status || st.crowd_action}
                                  </span>
                                </div>
                              </div>
                            </Popup>
                          </Marker>
                        );
                      })}

                      {/* Origin Stop Marker */}
                      <Marker position={origCoords} icon={createOriginIcon()}>
                        <Tooltip direction="top" offset={[0, -32]}>
                          <div className="text-xs font-semibold">Origin: {origStopName} • {selectedAlt.departure_time_label}</div>
                        </Tooltip>
                        <Popup>
                          <div className="text-xs p-1.5 space-y-1 min-w-[150px]">
                            <span className="text-[10px] px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold uppercase tracking-wider inline-block">Journey Origin</span>
                            <strong className="block text-slate-900 font-bold">{origStopName}</strong>
                            <span className="text-slate-600 block text-[11px]">Departure: <strong className="text-slate-900 font-mono">{selectedAlt.departure_time_label}</strong></span>
                          </div>
                        </Popup>
                      </Marker>

                      {/* Destination Stop Marker */}
                      <Marker position={destCoords} icon={createDestIcon()}>
                        <Tooltip direction="top" offset={[0, -32]}>
                          <div className="text-xs font-semibold">Destination: {destStopName} • {selectedAlt.arrival_time_label}</div>
                        </Tooltip>
                        <Popup>
                          <div className="text-xs p-1.5 space-y-1 min-w-[150px]">
                            <span className="text-[10px] px-1.5 py-0.5 bg-slate-900 text-white rounded font-bold uppercase tracking-wider inline-block">Final Destination</span>
                            <strong className="block text-slate-900 font-bold">{destStopName}</strong>
                            <span className="text-slate-600 block text-[11px]">Expected ETA: <strong className="text-slate-900 font-mono">{selectedAlt.arrival_time_label}</strong></span>
                            <span className="text-slate-500 block text-[10px] font-mono">Total: {selectedAlt.total_duration_mins} mins • {selectedAlt.distance_km} km</span>
                          </div>
                        </Popup>
                      </Marker>
                    </MapContainer>
                  </div>
                </div>

                {/* Simple, Human-Friendly Route Stops & Timetable */}
                <div className="pt-4 border-t border-slate-100">
                  <div className="flex items-center justify-between pb-3">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-slate-500" />
                      <span className="text-xs font-bold text-slate-900">
                        Route Stops & Timetable
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => setShowStopsTimeline(!showStopsTimeline)}
                      className="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1 cursor-pointer"
                    >
                      <span>{showStopsTimeline ? 'Collapse timetable' : 'View all stops'}</span>
                      {showStopsTimeline ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  {showStopsTimeline && (
                    <div className="border border-slate-200 rounded-xl overflow-hidden divide-y divide-slate-100 text-xs">
                      <div className="overflow-x-auto">
                        <div className="min-w-[760px]">
                          {/* Refined 6-Column Table Header: Bus Stop -> Time -> ETA -> Distance -> Seats -> Expected Rush */}
                          <div className="bg-slate-50 px-4 py-2.5 font-semibold text-slate-700 grid grid-cols-12 gap-3 text-xs border-b border-slate-100">
                            <div className="col-span-3 flex items-center gap-1.5">
                              <span>Bus Stop</span>
                              <span className="text-[11px] font-normal text-slate-400">
                                ({Math.max(0, timelineStops.length - 2)} in between)
                              </span>
                            </div>
                            <div className="col-span-2">Time</div>
                            <div className="col-span-1">ETA</div>
                            <div className="col-span-2">Distance</div>
                            <div className="col-span-2 text-left">Seats</div>
                            <div className="col-span-2 text-left">Expected Rush</div>
                          </div>

                          {/* Clean Human-Friendly Stop Rows */}
                          {timelineStops.map((st, idx) => {
                            const isStart = idx === 0;
                            const isDest = idx === timelineStops.length - 1;

                            const seatCap = st.seat_capacity || 35;
                            const onboardPax = st.onboard_pax !== undefined ? st.onboard_pax : 0;
                            const seatsAvailable = st.seats_available !== undefined
                              ? st.seats_available
                              : (isDest ? 0 : Math.max(0, seatCap - onboardPax));
                            const seatsFilled = st.seats_filled !== undefined
                              ? st.seats_filled
                              : (isDest ? 0 : Math.min(seatCap, onboardPax));
                            const standingCount = st.standing_pax !== undefined
                              ? st.standing_pax
                              : (isDest ? 0 : Math.max(0, onboardPax - seatCap));

                            // Physically accurate stop rush classification (guaranteed consistency with Seats column)
                            const isLow = !isDest && seatsAvailable > 0;
                            const isHigh = !isDest && !isLow && (standingCount > 12 || st.crowd_level === 'HIGH' || st.crowd_level === 'VERY HIGH');
                            const isModerate = !isDest && !isLow && !isHigh;

                            return (
                              <div
                                key={idx}
                                className="px-4 py-3.5 grid grid-cols-12 gap-3 items-stretch hover:bg-slate-50/80 transition-colors"
                              >
                                {/* Column 1: Bus Stop (Primary Anchor with Continuous Route Line & Location Pins) */}
                                <div className="col-span-3 pr-2 flex items-center gap-2.5">
                                  {/* Vertical Route Spine */}
                                  <div className="relative shrink-0 flex items-center justify-center w-5 self-stretch">
                                    {/* Unbroken Continuous Route Connecting Line */}
                                    <div
                                      className={`absolute w-0.5 bg-slate-300 ${isStart
                                        ? 'top-1/2 bottom-0'
                                        : isDest
                                          ? 'top-0 bottom-1/2'
                                          : 'top-0 bottom-0'
                                        }`}
                                    />
                                    {/* Exact Map Pin SVG (Matching Leaflet Map) */}
                                    <div className="z-10 relative flex items-center justify-center">
                                      <StopMapPin
                                        type={isStart ? 'origin' : isDest ? 'dest' : 'stop'}
                                        isHub={st.is_major_hub}
                                      />
                                    </div>
                                  </div>

                                  {/* Stop Name & Stop Sequence */}
                                  <div className="min-w-0 py-0.5">
                                    <span className="font-semibold text-slate-900 text-xs sm:text-sm truncate block leading-snug">
                                      {st.stop_name}
                                    </span>
                                    {!isStart && !isDest && (
                                      <span className="text-[11px] text-slate-500 font-mono block mt-0.5">
                                        Stop {idx} of {Math.max(1, timelineStops.length - 2)}
                                      </span>
                                    )}
                                  </div>
                                </div>

                                {/* Column 2: Scheduled Time */}
                                <div className="col-span-2">
                                  <span className="font-bold font-mono text-slate-900 text-sm block">
                                    {st.eta_time}
                                  </span>
                                  <span className="text-[10px] text-slate-400 font-mono block">
                                    {isStart ? 'Departure' : isDest ? 'Arrival' : 'Scheduled'}
                                  </span>
                                </div>

                                {/* Column 3: ETA from Start */}
                                <div className="col-span-1">
                                  <span className="font-mono text-slate-800 text-xs font-semibold block">
                                    {isStart ? '0 min' : `+${st.mins_from_start}m`}
                                  </span>
                                  <span className="text-[10px] text-slate-400 font-mono block">
                                    {isStart ? 'Start' : `In ${st.mins_from_start}m`}
                                  </span>
                                </div>

                                {/* Column 4: Distance from Start */}
                                <div className="col-span-2">
                                  <span className="font-mono text-slate-800 text-xs font-semibold block">
                                    {st.distance_km !== undefined ? `${Number(st.distance_km).toFixed(1)} km` : `${(idx * 2.5).toFixed(1)} km`}
                                  </span>
                                  <span className="text-[10px] text-slate-400 font-mono block">
                                    {isStart
                                      ? 'Origin'
                                      : `+${Number(st.hop_distance_km !== undefined ? st.hop_distance_km : (st.distance_km - (timelineStops[idx - 1]?.distance_km || 0))).toFixed(1)} km hop`}
                                  </span>
                                </div>

                                {/* Column 5: Dedicated Seats Column - Simple & Professional */}
                                <div className="col-span-2 text-left">
                                  {isDest ? (
                                    <div>
                                      <span className="font-semibold text-slate-400 text-xs block">—</span>
                                      <span className="text-[11px] text-slate-400 font-normal block">Arrival</span>
                                    </div>
                                  ) : (
                                    <div>
                                      <span className={`font-semibold text-xs block ${seatsAvailable > 0 ? 'text-emerald-700' : 'text-slate-800'}`}>
                                        {seatsAvailable > 0 ? `${seatsAvailable} Seats Free` : 'Seats Full'}
                                      </span>
                                      <span className="text-[11px] text-slate-500 font-normal block">
                                        {seatsAvailable > 0 ? `${seatsFilled} of ${seatCap} filled` : `+${standingCount} standing`}
                                      </span>
                                    </div>
                                  )}
                                </div>

                                {/* Column 6: Expected Rush - Dark Theme Badges */}
                                <div className="col-span-2 text-left">
                                  <div className="space-y-1">
                                    <span className={`inline-flex items-center justify-center w-[114px] py-1 rounded-md text-[11px] font-semibold tracking-tight shadow-xs ${isDest
                                      ? 'bg-slate-800 text-white'
                                      : isLow
                                        ? 'bg-emerald-700 text-white'
                                        : isHigh
                                          ? 'bg-rose-700 text-white'
                                          : 'bg-amber-600 text-white'
                                      }`}>
                                      {isDest ? 'End of Route' : isLow ? 'Seats Available' : isHigh ? 'Crowded' : 'Moderate Rush'}
                                    </span>
                                    <span className="text-[10px] text-slate-400 block w-[114px] text-center font-normal">
                                      {isDest ? 'Trip ends here' : isLow ? 'Seats usually free' : isHigh ? 'Standing only' : 'Normal standing'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Clean Empty State before search */}
      {!results && !loading && (
        <div className="bg-white border border-slate-200/90 rounded-2xl p-10 text-center space-y-3 shadow-xs max-w-xl mx-auto mt-6">
          <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto text-slate-500">
            <Bus className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Plan a Transit Route</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Select your starting bus stand and destination to discover direct routes, arrival ETAs, and empirical seat crowdness.
          </p>
        </div>
      )}
    </div>
  );
}
