import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Polyline, Popup, ZoomControl, useMap } from 'react-leaflet';
import { 
  ArrowLeftRight, 
  Search, 
  Clock, 
  MapPin, 
  Bus, 
  ArrowRight,
  Navigation,
  Users,
  ChevronDown,
  ChevronUp,
  Zap,
  X
} from 'lucide-react';
import { planJourney, fetchStops } from '../services/api';

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

function parseTo12Hour(time24) {
  if (!time24) return { hour: '08', minute: '30', ampm: 'AM', display: '08:30 AM' };
  const parts = time24.split(':');
  let h = parseInt(parts[0], 10);
  const m = parts[1] || '00';
  if (isNaN(h)) h = 8;
  const ampm = h >= 12 ? 'PM' : 'AM';
  let h12 = h % 12;
  if (h12 === 0) h12 = 12;
  const hStr = String(h12).padStart(2, '0');
  return {
    hour: hStr,
    minute: m,
    ampm,
    display: `${hStr}:${m} ${ampm}`
  };
}

function to24Hour(hour12, minute, ampm) {
  let h = parseInt(hour12, 10);
  if (ampm === 'PM' && h < 12) h += 12;
  if (ampm === 'AM' && h === 12) h = 0;
  return `${String(h).padStart(2, '0')}:${minute}`;
}

export default function JourneyPlanner() {
  const [origin, setOrigin] = useState('Saket Bus Stop');
  const [destination, setDestination] = useState('Dhaula Kuan');
  const [departureTime, setDepartureTime] = useState('08:30');
  const [preferLessCrowded, setPreferLessCrowded] = useState(false);

  const [stopsList, setStopsList] = useState([]);
  const [originOpen, setOriginOpen] = useState(false);
  const [destOpen, setDestOpen] = useState(false);

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAlternativeId, setSelectedAlternativeId] = useState(null);
  const [showStopsTimeline, setShowStopsTimeline] = useState(true);

  // Load stops
  useEffect(() => {
    fetchStops()
      .then((stops) => setStopsList(stops))
      .catch(() => {});
  }, []);

  // Filter stops for custom symmetrical autocomplete (sorted by bus boardings & hub status)
  const filteredOriginStops = origin.trim()
    ? stopsList
        .filter((s) => s.name.toLowerCase().includes(origin.toLowerCase().trim()))
        .sort((a, b) => (b.monthly_boardings || 0) - (a.monthly_boardings || 0))
        .slice(0, 8)
    : stopsList.slice(0, 8);

  const filteredDestStops = destination.trim()
    ? stopsList
        .filter((s) => s.name.toLowerCase().includes(destination.toLowerCase().trim()))
        .sort((a, b) => (b.monthly_boardings || 0) - (a.monthly_boardings || 0))
        .slice(0, 8)
    : stopsList.slice(0, 8);

  // Initial search
  useEffect(() => {
    handleSearch();
  }, []);

  const handleSwap = () => {
    const newOrig = destination;
    const newDest = origin;
    setOrigin(newOrig);
    setDestination(newDest);
    handleSearch(null, newOrig, newDest);
  };

  const handleTogglePreference = (checked) => {
    setPreferLessCrowded(checked);
    if (results) {
      setLoading(true);
      planJourney({
        origin: (results.origin || origin).trim(),
        destination: (results.destination || destination).trim(),
        departure_time: departureTime,
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

  const handleSearch = async (e, customOrig, customDest, customTime) => {
    if (e && e.preventDefault) e.preventDefault();
    const origToUse = (customOrig || origin).trim();
    const destToUse = (customDest || destination).trim();
    const timeToUse = customTime || departureTime;
    if (!origToUse || !destToUse) return;

    setLoading(true);
    setError(null);
    try {
      const data = await planJourney({
        origin: origToUse,
        destination: destToUse,
        departure_time: timeToUse,
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

  const handleCorridorSelect = (orig, dest, customTime = null) => {
    setOrigin(orig);
    setDestination(dest);
    if (customTime) {
      setDepartureTime(customTime);
      handleSearch(null, orig, dest, customTime);
    } else {
      handleSearch(null, orig, dest);
    }
  };

  const selectedAlt = results?.alternatives?.find((a) => a.id === selectedAlternativeId) || results?.alternatives?.[0];

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Route Planner
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          Direct bus routes and crowding predictions based on Delhi ETM ticketing patterns.
        </p>
      </div>

      {/* Main Search Panel */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs card-hover">
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
                  placeholder="Starting bus stop or bus stand..."
                  className="w-full pl-10 pr-9 py-2.5 bg-slate-50 border border-slate-200 focus:border-slate-900 focus:bg-white rounded-xl text-sm text-slate-900 outline-none transition-colors"
                />
                {origin && (
                  <button
                    type="button"
                    onClick={() => {
                      setOrigin('');
                      setOriginOpen(true);
                    }}
                    title="Clear starting stop"
                    className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                {/* Symmetrical In-Place Suggestions Dropdown */}
                {originOpen && filteredOriginStops.length > 0 && (
                  <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-lg z-50 max-h-56 overflow-y-auto divide-y divide-slate-100">
                    {filteredOriginStops.map((stop) => (
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
                          <span className="text-[11px] text-slate-400 block">{stop.corridor}</span>
                        </div>
                        {stop.is_major_hub && (
                          <span className="text-[10px] font-mono text-slate-500 font-medium">Bus Stand</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Swap Button: Perfectly Symmetrical & Centered */}
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
                  placeholder="Destination bus stop or bus stand..."
                  className="w-full pl-10 pr-9 py-2.5 bg-slate-50 border border-slate-200 focus:border-slate-900 focus:bg-white rounded-xl text-sm text-slate-900 outline-none transition-colors"
                />
                {destination && (
                  <button
                    type="button"
                    onClick={() => {
                      setDestination('');
                      setDestOpen(true);
                    }}
                    title="Clear destination stop"
                    className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                {/* Symmetrical In-Place Suggestions Dropdown */}
                {destOpen && filteredDestStops.length > 0 && (
                  <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-lg z-50 max-h-56 overflow-y-auto divide-y divide-slate-100">
                    {filteredDestStops.map((stop) => (
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
                          <span className="text-[11px] text-slate-400 block">{stop.corridor}</span>
                        </div>
                        {stop.is_major_hub && (
                          <span className="text-[10px] font-mono text-slate-500 font-medium">Bus Stand</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Departure & Optimization Bar */}
          <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Direct Simple Time Selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-700">Time:</span>
              
              <div className="inline-flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs shadow-2xs">
                <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                
                {/* Hour */}
                <select
                  value={parseTo12Hour(departureTime).hour}
                  onChange={(e) => {
                    const parsed = parseTo12Hour(departureTime);
                    const newTime = to24Hour(e.target.value, parsed.minute, parsed.ampm);
                    setDepartureTime(newTime);
                    handleSearch(null, null, null, newTime);
                  }}
                  className="bg-transparent font-semibold text-slate-900 outline-none cursor-pointer text-xs"
                >
                  {['01','02','03','04','05','06','07','08','09','10','11','12'].map(h => (
                    <option key={h} value={h}>{h}</option>
                  ))}
                </select>

                <span className="text-slate-400 font-bold">:</span>

                {/* Minute */}
                <select
                  value={parseTo12Hour(departureTime).minute}
                  onChange={(e) => {
                    const parsed = parseTo12Hour(departureTime);
                    const newTime = to24Hour(parsed.hour, e.target.value, parsed.ampm);
                    setDepartureTime(newTime);
                    handleSearch(null, null, null, newTime);
                  }}
                  className="bg-transparent font-semibold text-slate-900 outline-none cursor-pointer text-xs"
                >
                  {['00','05','10','15','20','25','30','35','40','45','50','55'].map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>

                {/* AM / PM Select */}
                <select
                  value={parseTo12Hour(departureTime).ampm}
                  onChange={(e) => {
                    const parsed = parseTo12Hour(departureTime);
                    const newTime = to24Hour(parsed.hour, parsed.minute, e.target.value);
                    setDepartureTime(newTime);
                    handleSearch(null, null, null, newTime);
                  }}
                  className="ml-1 bg-white border border-slate-200 rounded-md px-1.5 py-0.5 font-bold text-slate-900 outline-none cursor-pointer text-[11px] shadow-2xs"
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
            </div>

            {/* Right: Comfort Preference & Find Routes Button */}
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer select-none text-xs font-medium text-slate-700">
                <input
                  type="checkbox"
                  checked={preferLessCrowded}
                  onChange={(e) => handleTogglePreference(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-0 cursor-pointer accent-slate-900"
                />
                <span>Prioritize less crowded</span>
              </label>

              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2.5 bg-slate-900 hover:bg-black text-white text-xs font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 shadow-xs shrink-0"
              >
                <Search className="w-3.5 h-3.5" />
                <span>{loading ? 'Routing...' : 'Find Routes'}</span>
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Quick Test Links (Plain text, no bubbles) */}
      <div className="flex items-center gap-2 text-xs text-slate-500 flex-wrap">
        <span className="font-semibold text-slate-900">Popular corridors:</span>
        <button
          type="button"
          onClick={() => handleCorridorSelect('Saket Bus Stop', 'Dhaula Kuan')}
          className="text-slate-600 hover:text-slate-900 underline underline-offset-2 cursor-pointer"
        >
          Saket → Dhaula Kuan
        </button>
        <span>•</span>
        <button
          type="button"
          onClick={() => handleCorridorSelect('Hamdard Nagar / Sangam Vihar', 'Badarpur Border')}
          className="text-slate-600 hover:text-slate-900 underline underline-offset-2 cursor-pointer"
        >
          Sangam Vihar → Badarpur
        </button>
        <span>•</span>
        <button
          type="button"
          onClick={() => handleCorridorSelect('Kashmere Gate', 'AIIMS')}
          className="text-slate-600 hover:text-slate-900 underline underline-offset-2 cursor-pointer"
        >
          Kashmere Gate → AIIMS
        </button>
        <span>•</span>
        <button
          type="button"
          onClick={() => handleCorridorSelect('Anand Vihar', 'Connaught Place', '18:00')}
          className="text-slate-900 font-medium hover:text-black underline underline-offset-2 cursor-pointer flex items-center gap-1"
        >
          <span>Anand Vihar → Connaught Place (6:00 PM)</span>
          <span className="text-[10px] bg-slate-100 text-slate-800 px-1.5 py-0.2 rounded font-semibold">Arterial Corridor</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs">
          {error}
        </div>
      )}

      {/* Results View */}
      {results && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">
              Suggested routes at {results.departure_time}
            </h3>
            <span className="text-xs text-slate-500">
              {results.alternatives.length} options evaluated
            </span>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {results.alternatives.map((alt) => {
              const isSelected = selectedAlternativeId === alt.id;
              const badgeLabel = alt.badge === 'FASTEST' 
                ? 'Fastest Trip' 
                : (alt.badge === 'SEATS AVAILABLE' 
                    ? 'Comfort Option' 
                    : (alt.badge === 'RECOMMENDED' ? 'Recommended' : (alt.badge === 'DIRECT' ? 'Direct Regular' : 'Alternative')));
              const comfortText = alt.comfort_label || (
                alt.crowd_level === 'LOW' 
                  ? 'Seats Available' 
                  : (alt.crowd_level === 'HIGH' ? 'Crowded' : 'Standing Room')
              );

              return (
                <div
                  key={alt.id}
                  onClick={() => setSelectedAlternativeId(alt.id)}
                  className={`bg-white p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between card-hover ${
                    isSelected
                      ? 'border-slate-400 bg-slate-50/40 shadow-xs'
                      : 'border-slate-200/90 hover:border-slate-300 hover:shadow-xs'
                  }`}
                >
                  <div>
                    {/* Clean text header */}
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-xs font-semibold text-slate-800 tracking-tight">
                          {badgeLabel}
                        </span>
                        {alt.service_type === 'DIRECT_EXPRESS' ? (
                          <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200/80 rounded font-bold text-[10px]">
                            <Zap className="w-2.5 h-2.5 text-emerald-600 shrink-0" />
                            <span>Express (-{alt.time_saved_mins || 12}m)</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium">
                            All Stops
                          </span>
                        )}
                      </div>
                      <span className={`text-xs font-medium flex items-center gap-1.5 ${
                        alt.crowd_level === 'LOW' ? 'text-emerald-700' : (alt.crowd_level === 'HIGH' ? 'text-amber-700' : 'text-slate-600')
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          alt.crowd_level === 'LOW' ? 'bg-emerald-600' : (alt.crowd_level === 'HIGH' ? 'bg-amber-600' : 'bg-slate-400')
                        }`} />
                        {comfortText}
                      </span>
                    </div>

                    {/* Time & Departure */}
                    <div className="pt-3.5 pb-2">
                      <div className="flex items-baseline justify-between">
                        <div className="flex items-baseline gap-1">
                          <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                            {alt.total_duration_mins}
                          </span>
                          <span className="text-xs text-slate-500 font-medium">min</span>
                        </div>
                        {alt.departure_time_label && (
                          <span className="text-xs text-slate-500 font-mono">
                            {alt.departure_shift_mins > 0 ? `Departs ${alt.departure_time_label}` : `Departs ${alt.departure_time_label}`}
                          </span>
                        )}
                      </div>

                      {/* Route Details Strip */}
                      <div className="mt-3 flex items-center gap-2 text-xs flex-wrap">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 text-slate-900 rounded font-bold font-mono text-[11px]">
                          <Bus className="w-3 h-3 text-slate-600" />
                          {alt.bus_routes.join(' → ')}
                        </span>
                        <span className="text-slate-300">•</span>
                        <span className="text-slate-600">
                          {alt.service_type === 'DIRECT_EXPRESS' ? 'Direct (Limited Stops)' : 'Regular (All Stops)'}
                        </span>
                        <span className="text-slate-300">•</span>
                        <span className="text-slate-600">
                          {alt.stops_count || 6} stops
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Clean Bottom Footer */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
                    <span className="text-slate-500 truncate max-w-[170px]">
                      {alt.departure_shift_mins > 0 ? `+${alt.departure_shift_mins}m avoids peak rush` : 'Direct service'}
                    </span>
                    <span className={`font-medium ${isSelected ? 'text-slate-900 font-semibold' : 'text-slate-400'}`}>
                      {isSelected ? 'Viewing map ↓' : 'View map ↓'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detailed Selected Route Steps & Visual Route Map */}
          {selectedAlt && (() => {
            const getCoordinatesForStop = (stopName) => {
              if (!stopName) return [28.6139, 77.2090];
              const clean = stopName.toLowerCase().trim();
              
              // 1. Exact match
              let match = stopsList.find((s) => s.name.toLowerCase() === clean);
              if (match?.latitude && match?.longitude) return [match.latitude, match.longitude];

              // 2. Substring match
              match = stopsList.find((s) => s.name.toLowerCase().includes(clean) || clean.includes(s.name.toLowerCase()));
              if (match?.latitude && match?.longitude) return [match.latitude, match.longitude];

              // 3. Meaningful token match (> 3 characters)
              const tokens = clean.split(/\s+/).filter((w) => w.length > 3);
              for (const tok of tokens) {
                const tokMatch = stopsList.find((s) => s.name.toLowerCase().includes(tok));
                if (tokMatch?.latitude && tokMatch?.longitude) {
                  return [tokMatch.latitude, tokMatch.longitude];
                }
              }

              // 4. Primary landmark fallback map
              if (clean.includes('anand')) return [28.6502, 77.3155];
              if (clean.includes('shivaji') || clean.includes('connaught') || clean.includes('cp')) return [28.6327, 77.2195];
              if (clean.includes('saket')) return [28.5204, 77.2015];
              if (clean.includes('dhaula')) return [28.5921, 77.1615];
              if (clean.includes('kashmere')) return [28.6675, 77.2285];
              if (clean.includes('aiims')) return [28.5672, 77.2100];
              if (clean.includes('badarpur')) return [28.4975, 77.3025];
              if (clean.includes('sangam') || clean.includes('hamdard')) return [28.5145, 77.2580];
              if (clean.includes('uttam')) return [28.6210, 77.0620];
              if (clean.includes('nehru')) return [28.5495, 77.2515];
              if (clean.includes('janakpuri')) return [28.6295, 77.0815];
              if (clean.includes('dwarka')) return [28.5921, 77.0460];
              if (clean.includes('rohini')) return [28.7150, 77.1120];
              if (clean.includes('lajpat')) return [28.5700, 77.2400];
              if (clean.includes('nizamuddin')) return [28.5880, 77.2530];
              if (clean.includes('hauz')) return [28.5494, 77.2001];
              if (clean.includes('pitampura')) return [28.6989, 77.1384];

              return [28.6139, 77.2090];
            };

            const origStopName = results?.origin || origin;
            const destStopName = results?.destination || destination;
            const origCoords = getCoordinatesForStop(origStopName);
            const destCoords = getCoordinatesForStop(destStopName);
            
            // Build real route points: intermediate transfer stops if any
            const transferPoints = [];
            if (selectedAlt.steps && selectedAlt.steps.length > 1) {
              for (let i = 0; i < selectedAlt.steps.length - 1; i++) {
                const transferStop = selectedAlt.steps[i].to_stop;
                if (transferStop) {
                  transferPoints.push({
                    name: transferStop,
                    coords: getCoordinatesForStop(transferStop)
                  });
                }
              }
            }

            const routePoints = selectedAlt.route_coordinates && selectedAlt.route_coordinates.length > 1
              ? selectedAlt.route_coordinates
              : [origCoords, ...transferPoints.map(t => t.coords), destCoords];

            const mapCenter = [
              (origCoords[0] + destCoords[0]) / 2,
              (origCoords[1] + destCoords[1]) / 2
            ];

            return (
              <div className="bg-white border border-slate-200/80 p-6 rounded-2xl shadow-xs space-y-6 card-hover">
                <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      Route Details • Bus {selectedAlt.bus_routes.join(' & ')}
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {selectedAlt.recommendation_explanation}
                    </p>
                  </div>

                  <div className="text-right">
                    <span className="text-[11px] text-slate-400 block">Crowd Index</span>
                    <span className="text-base font-bold text-slate-900 font-mono">
                      {selectedAlt.crowd_score}/100
                    </span>
                  </div>
                </div>

                {/* Interactive Leaflet Route Trace Map */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                    <div className="flex items-center gap-1.5">
                      <Navigation className="w-3.5 h-3.5 text-slate-500" />
                      <span>Route Map</span>
                    </div>
                    <span className="text-[11px] font-normal text-slate-500">
                      Green: Origin • Amber: Transfer • Dark: Destination
                    </span>
                  </div>

                  <div className="h-72 rounded-xl overflow-hidden border border-slate-200 relative">
                    <MapContainer
                      center={mapCenter}
                      zoom={12}
                      scrollWheelZoom={true}
                      zoomControl={false}
                      attributionControl={false}
                      preferCanvas={true}
                      style={{ height: '100%', width: '100%' }}
                    >
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        maxZoom={19}
                      />
                      <ZoomControl position="topright" />
                      <MapBoundsController points={routePoints} />
                      <Polyline
                        positions={routePoints}
                        pathOptions={{
                          color: selectedAlt.crowd_level === 'HIGH' ? '#DC2626' : (selectedAlt.crowd_level === 'LOW' ? '#059669' : '#2563EB'),
                          weight: 4,
                          opacity: 0.85
                        }}
                      />
                      <CircleMarker center={origCoords} radius={7} pathOptions={{ color: '#FFFFFF', fillColor: '#059669', fillOpacity: 1, weight: 2 }}>
                        <Popup>
                          <div className="text-xs p-1">
                            <strong className="block text-slate-900">Origin Stop</strong>
                            <span className="text-slate-600">{origStopName}</span>
                          </div>
                        </Popup>
                      </CircleMarker>
                      {transferPoints.map((tp, idx) => (
                        <CircleMarker key={idx} center={tp.coords} radius={6} pathOptions={{ color: '#FFFFFF', fillColor: selectedAlt.crowd_level === 'HIGH' ? '#DC2626' : '#EAB308', fillOpacity: 1, weight: 2 }}>
                          <Popup>
                            <div className="text-xs p-1">
                              <strong className="block text-slate-900">Transfer Stop</strong>
                              <span className="text-slate-600">{tp.name}</span>
                            </div>
                          </Popup>
                        </CircleMarker>
                      ))}
                      <CircleMarker center={destCoords} radius={7} pathOptions={{ color: '#FFFFFF', fillColor: '#0F172A', fillOpacity: 1, weight: 2 }}>
                        <Popup>
                          <div className="text-xs p-1">
                            <strong className="block text-slate-900">Destination Stop</strong>
                            <span className="text-slate-600">{destStopName}</span>
                          </div>
                        </Popup>
                      </CircleMarker>
                    </MapContainer>
                  </div>
                </div>

                {/* Sequenced Intermediate Stops Timeline */}
                <div className="pt-4 border-t border-slate-100">
                  <div className="flex items-center justify-between pb-3">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span className="text-xs font-bold text-slate-900">
                        Stop Sequence ({selectedAlt.stops_count || selectedAlt.stops_list?.length || 2} stops)
                      </span>
                      {selectedAlt.service_type === 'DIRECT_EXPRESS' ? (
                        <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200/80 rounded font-semibold text-[10px] flex items-center gap-1">
                          <Zap className="w-2.5 h-2.5 text-emerald-600" />
                          Direct Express • Saves {selectedAlt.time_saved_mins || 12}m
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium">
                          Regular Local • All Intermediate Stops
                        </span>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={() => setShowStopsTimeline(!showStopsTimeline)}
                      className="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1 cursor-pointer"
                    >
                      <span>{showStopsTimeline ? 'Collapse stops' : 'View all intermediate stops'}</span>
                      {showStopsTimeline ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  {showStopsTimeline && (
                    <div className="relative pl-6 space-y-3 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                      {/* Origin Stop */}
                      <div className="relative flex items-start gap-2.5">
                        <span className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-emerald-600 ring-4 ring-emerald-50" />
                        <div>
                          <span className="text-xs font-bold text-slate-900 block">{origStopName}</span>
                          <span className="text-[11px] text-slate-500">Origin Stand • Board Bus {selectedAlt.bus_routes[0]}</span>
                        </div>
                      </div>

                      {/* Intermediate Stops */}
                      {(selectedAlt.intermediate_stops && selectedAlt.intermediate_stops.length > 0
                        ? selectedAlt.intermediate_stops
                        : (selectedAlt.stops_list && selectedAlt.stops_list.length > 2 ? selectedAlt.stops_list.slice(1, -1) : [])
                      ).map((stopName, sIdx) => (
                        <div key={sIdx} className="relative flex items-start gap-2.5">
                          <span className="absolute -left-6 top-1.5 w-2 h-2 rounded-full bg-slate-400 ring-2 ring-slate-100" />
                          <div className="flex items-center justify-between w-full pr-2">
                            <span className="text-xs text-slate-700 font-medium">{stopName}</span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              {selectedAlt.service_type === 'DIRECT_EXPRESS' ? 'Express Hub Stop' : `Stop #${sIdx + 2}`}
                            </span>
                          </div>
                        </div>
                      ))}

                      {/* Skipped Stops Banner if Express */}
                      {selectedAlt.service_type === 'DIRECT_EXPRESS' && selectedAlt.skipped_stops && selectedAlt.skipped_stops.length > 0 && (
                        <div className="text-[11px] text-emerald-700 bg-emerald-50/70 border border-emerald-100 rounded-lg p-2.5 ml-1">
                          <span className="font-semibold block">Direct Express Bypass:</span>
                          <span className="text-emerald-600">
                            Skips minor local stops ({selectedAlt.skipped_stops.join(', ')}) to maintain high speed and save {selectedAlt.time_saved_mins || 12} minutes.
                          </span>
                        </div>
                      )}

                      {/* Destination Stop */}
                      <div className="relative flex items-start gap-2.5 pt-1">
                        <span className="absolute -left-6 top-1.5 w-2.5 h-2.5 rounded-full bg-slate-900 ring-4 ring-slate-100" />
                        <div>
                          <span className="text-xs font-bold text-slate-900 block">{destStopName}</span>
                          <span className="text-[11px] text-slate-500">Destination Stand • Alight</span>
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
    </div>
  );
}
