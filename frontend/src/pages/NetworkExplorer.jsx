import React, { useState, useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip, Polyline, ZoomControl, useMap } from 'react-leaflet';
import {
  Search,
  X,
  MapPin,
  RotateCcw,
  Navigation,
  Bus,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import { fetchNetworkGeo } from '../services/api';

const DELHI_DEFAULT_CENTER = [28.6139, 77.2090];
const DELHI_DEFAULT_ZOOM = 11;

// Controller component to smoothly fly map view ONLY when explicitly requested (click/select/reset)
function MapController({ targetView }) {
  const map = useMap();
  useEffect(() => {
    if (targetView && targetView.center) {
      map.flyTo(targetView.center, targetView.zoom || DELHI_DEFAULT_ZOOM, { duration: 0.8 });
    }
  }, [targetView, map]);

  return null;
}

export default function NetworkExplorer() {
  const [geoData, setGeoData] = useState(null);
  const [corridors, setCorridors] = useState([]);
  const [selectedCorridorId, setSelectedCorridorId] = useState(null);
  const [selectedStop, setSelectedStop] = useState(null);
  const [stopFilter, setStopFilter] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(true);
  const [targetView, setTargetView] = useState(null);

  const searchContainerRef = useRef(null);

  useEffect(() => {
    fetchNetworkGeo()
      .then(({ geojson, corridors }) => {
        setGeoData(geojson);
        setCorridors(corridors);
        // Clean map by default — no corridor pre-drawn
        setSelectedCorridorId(null);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Network geo load error:', err);
        setLoading(false);
      });
  }, []);

  // Close search dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const activeCorridor = useMemo(() => {
    return corridors.find((c) => c.id === selectedCorridorId) || null;
  }, [corridors, selectedCorridorId]);

  // Set of lowercase stop names belonging to active corridor/route
  const activeStopNamesSet = useMemo(() => {
    if (!activeCorridor || !activeCorridor.stops) return null;
    return new Set(activeCorridor.stops.map((s) => s.toLowerCase().trim()));
  }, [activeCorridor]);

  // Stops on the active corridor/route with their geo features
  const activeCorridorStops = useMemo(() => {
    if (!activeStopNamesSet || !geoData?.features) return [];
    return geoData.features.filter((f) =>
      activeStopNamesSet.has(f.properties.name.toLowerCase().trim())
    );
  }, [activeStopNamesSet, geoData]);

  // Filtered stops for search dropdown (searches all Delhi stops or prioritizes corridor stops)
  const searchResults = useMemo(() => {
    if (!geoData?.features) return { corridorMatches: [], otherMatches: [] };
    const query = stopFilter.toLowerCase().trim();

    if (!query) {
      // If no query entered, show stops belonging to active corridor if one is selected
      if (activeCorridor) {
        return { corridorMatches: activeCorridorStops, otherMatches: [] };
      }
      return { corridorMatches: [], otherMatches: [] };
    }

    const allMatches = geoData.features.filter((f) =>
      f.properties.name.toLowerCase().includes(query) ||
      f.properties.corridor.toLowerCase().includes(query)
    );

    if (activeStopNamesSet) {
      const corridorMatches = allMatches.filter((f) =>
        activeStopNamesSet.has(f.properties.name.toLowerCase().trim())
      );
      const otherMatches = allMatches.filter((f) =>
        !activeStopNamesSet.has(f.properties.name.toLowerCase().trim())
      );
      return {
        corridorMatches: corridorMatches.slice(0, 8),
        otherMatches: otherMatches.slice(0, 8),
      };
    }

    return {
      corridorMatches: [],
      otherMatches: allMatches.slice(0, 12),
    };
  }, [geoData, stopFilter, activeCorridor, activeStopNamesSet, activeCorridorStops]);

  const handleRecenter = () => {
    setTargetView({ center: DELHI_DEFAULT_CENTER, zoom: DELHI_DEFAULT_ZOOM, id: Date.now() });
    setSelectedStop(null);
    setSelectedCorridorId(null);
    setStopFilter('');
    setShowDropdown(false);
  };

  const handleCorridorChange = (corridorId) => {
    if (!corridorId) {
      setSelectedCorridorId(null);
      setTargetView({ center: DELHI_DEFAULT_CENTER, zoom: DELHI_DEFAULT_ZOOM, id: Date.now() });
      setShowDropdown(false);
      return;
    }
    setSelectedCorridorId(corridorId);
    setShowDropdown(false);
    const corr = corridors.find((c) => c.id === corridorId);
    if (corr && corr.coordinates && corr.coordinates.length > 0) {
      const midIdx = Math.floor(corr.coordinates.length / 2);
      setTargetView({ center: corr.coordinates[midIdx], zoom: 12, id: Date.now() });
    }
  };

  const handleSelectStop = (feature) => {
    const [lon, lat] = feature.geometry.coordinates;
    setSelectedStop({
      ...feature.properties,
      coordinates: [lon, lat],
    });
    setTargetView({ center: [lat, lon], zoom: 14, id: Date.now() });
    setShowDropdown(false);
  };

  return (
    <div className="h-screen w-full relative select-none">
      {/* Top-Right Floating Reset View Action */}
      <button
        onClick={handleRecenter}
        title="Reset map view to Delhi center"
        className="absolute top-3 right-14 z-[400] bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm text-xs font-semibold text-slate-700 flex items-center gap-1.5 hover:bg-white cursor-pointer transition-all hover:border-slate-300"
      >
        <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
        <span>Reset View</span>
      </button>

      {/* Main Map Canvas — 100% Full Screen */}
      <div className="w-full h-full relative bg-white overflow-hidden">
        {loading ? (
          <div className="w-full h-full flex items-center justify-center bg-slate-50 text-xs text-slate-500 font-medium">
            Loading Delhi NCT Spatial Layer & Corridors...
          </div>
        ) : (
          <MapContainer
            center={DELHI_DEFAULT_CENTER}
            zoom={DELHI_DEFAULT_ZOOM}
            scrollWheelZoom={true}
            zoomControl={false}
            attributionControl={false}
            preferCanvas={true}
            className="w-full h-full"
          >
            <MapController targetView={targetView} />

            {/* Top-Right Visible Zoom Control */}
            <ZoomControl position="topright" />

            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />

            {/* Active Corridor / Route Polyline with Demand-Aware Dynamic Color */}
            {activeCorridor && activeCorridor.coordinates && (
              <Polyline
                positions={activeCorridor.coordinates}
                pathOptions={{
                  color:
                    activeCorridor.crowd_level === 'VERY HIGH'
                      ? '#DC2626'
                      : activeCorridor.crowd_level === 'HIGH'
                      ? '#2563EB'
                      : '#059669',
                  weight: 5,
                  opacity: 0.9,
                  lineCap: 'round',
                  lineJoin: 'round',
                }}
              />
            )}

            {/* Stop Vector Markers with Smart Highlighting */}
            {geoData?.features?.map((feature) => {
              const [lon, lat] = feature.geometry.coordinates;
              const { name, corridor, boardings, is_hub, id } = feature.properties;
              const isSelected = selectedStop?.id === id;

              // Check if stop belongs to the active corridor/route
              const belongsToActive = activeStopNamesSet
                ? activeStopNamesSet.has(name.toLowerCase().trim())
                : false;

              // Clutter-free route view:
              // When a corridor/route is selected, display ONLY its stops (and any clicked stop)
              if (activeCorridor && !belongsToActive && !isSelected) {
                return null;
              }

              // Visual styling logic:
              // Major Bus Stands: Black Dots (#0F172A, radius 7.5)
              // Regular Bus Stops: Blue Dots (#2563EB, radius 4.5)
              let radius = is_hub ? 7.5 : 4.5;
              let fillColor = is_hub ? '#0F172A' : '#2563EB';
              let fillOpacity = is_hub ? 0.95 : 0.85;
              let strokeColor = '#FFFFFF';
              let strokeWidth = 1.5;

              if (activeCorridor && belongsToActive) {
                radius = is_hub ? 8.5 : 6.5;
                fillColor =
                  activeCorridor.crowd_level === 'VERY HIGH'
                    ? '#DC2626'
                    : activeCorridor.crowd_level === 'HIGH'
                    ? '#2563EB'
                    : '#059669';
                fillOpacity = 1.0;
                strokeWidth = 2.5;
                strokeColor = '#FFFFFF';
              }

              if (isSelected) {
                radius = 9.5;
                fillColor = '#EF4444';
                strokeColor = '#FFFFFF';
                strokeWidth = 3;
                fillOpacity = 1.0;
              }

              return (
                <CircleMarker
                  key={id}
                  center={[lat, lon]}
                  radius={radius}
                  pathOptions={{
                    color: strokeColor,
                    fillColor: fillColor,
                    fillOpacity: fillOpacity,
                    weight: strokeWidth,
                  }}
                  eventHandlers={{
                    click: () => {
                      setSelectedStop({
                        id,
                        name,
                        corridor,
                        boardings,
                        is_hub,
                        coordinates: [lon, lat],
                      });
                      setTargetView({ center: [lat, lon], zoom: 13, id: Date.now() });
                    },
                  }}
                >
                  <Tooltip direction="top" offset={[0, -6]} opacity={0.95}>
                    <div className="font-semibold text-xs text-slate-900">{name}</div>
                    <div className="text-[10px] text-slate-500 font-medium">
                      {is_hub ? '● Major Bus Stand' : '● Bus Stop'}
                    </div>
                  </Tooltip>
                </CircleMarker>
              );
            })}
          </MapContainer>
        )}

        {/* Unified Merged Search Bar & Corridor/Route Selector (Top-Left) */}
        <div ref={searchContainerRef} className="absolute top-3 left-3 z-[400] flex flex-col gap-2 max-w-[calc(100vw-80px)]">
          {/* Merged Sleek Container */}
          <div className="bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200/90 shadow-md flex items-center divide-x divide-slate-200 transition-all hover:border-slate-300">
            {/* Left Segment: Stop Search Input */}
            <div className="relative flex items-center min-w-[260px] sm:min-w-[320px] px-3.5 py-2">
              <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
              <input
                type="text"
                placeholder={
                  activeCorridor
                    ? `Search stops on ${activeCorridor.name}...`
                    : 'Search bus stops across Delhi...'
                }
                value={stopFilter}
                onChange={(e) => {
                  setStopFilter(e.target.value);
                  setShowDropdown(true);
                }}
                onFocus={() => setShowDropdown(true)}
                className="w-full bg-transparent text-xs text-slate-900 placeholder:text-slate-400 font-medium outline-none"
              />
              {stopFilter && (
                <button
                  onClick={() => {
                    setStopFilter('');
                    setShowDropdown(false);
                  }}
                  className="text-slate-400 hover:text-slate-600 p-0.5 ml-1 cursor-pointer"
                  title="Clear search"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Right Segment: Corridor & Route Dropdown */}
            <div className="relative flex items-center px-3 py-2 bg-slate-50/70 hover:bg-slate-50 transition-colors rounded-r-2xl">
              <Navigation className="w-3.5 h-3.5 text-slate-500 mr-1.5 shrink-0" />
              <select
                value={selectedCorridorId || ''}
                onChange={(e) => handleCorridorChange(e.target.value)}
                className="bg-transparent font-semibold text-slate-800 text-xs outline-none cursor-pointer pr-1 max-w-[220px] sm:max-w-[320px] truncate"
              >
                <option value="">All Corridors & Routes (Delhi)</option>
                <optgroup label="Transit Corridors">
                  {corridors
                    .filter((c) => c.type === 'corridor')
                    .map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                </optgroup>
                <optgroup label="Bus Routes">
                  {corridors
                    .filter((c) => c.type === 'route')
                    .map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                </optgroup>
              </select>
              {selectedCorridorId && (
                <button
                  onClick={() => handleCorridorChange('')}
                  className="text-slate-400 hover:text-slate-700 p-0.5 ml-1 cursor-pointer"
                  title="Clear selected corridor/route"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Autocomplete Search Dropdown */}
          {showDropdown && (searchResults.corridorMatches.length > 0 || searchResults.otherMatches.length > 0) && (
            <div className="bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-xl p-1.5 max-h-72 overflow-y-auto divide-y divide-slate-100 text-xs w-full sm:w-[480px]">
              {/* Group 1: Stops on Selected Corridor/Route */}
              {searchResults.corridorMatches.length > 0 && (
                <div className="pb-1">
                  <div className="px-2 py-1 text-[10px] font-bold text-blue-600 uppercase tracking-wider flex items-center justify-between">
                    <span>Stops on {activeCorridor?.name || 'Active Corridor'}</span>
                    <span className="font-normal text-slate-400">{searchResults.corridorMatches.length} stops</span>
                  </div>
                  {searchResults.corridorMatches.map((f) => (
                    <button
                      key={f.properties.id}
                      onClick={() => handleSelectStop(f)}
                      className="w-full text-left py-1.5 px-2.5 hover:bg-blue-50/70 flex items-center justify-between text-slate-800 cursor-pointer rounded-lg transition-colors group"
                    >
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-blue-500 group-hover:scale-110 transition-transform" />
                        <div>
                          <span className="font-semibold text-slate-900 block">{f.properties.name}</span>
                          <span className="text-[10px] text-slate-500">{f.properties.corridor}</span>
                        </div>
                      </div>
                      <span className="text-[10px] text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded font-mono font-medium">
                        {f.properties.boardings.toLocaleString()} pax
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {/* Group 2: All Other Delhi Bus Stops */}
              {searchResults.otherMatches.length > 0 && (
                <div className="pt-1">
                  {searchResults.corridorMatches.length > 0 && (
                    <div className="px-2 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Other Delhi Bus Stops
                    </div>
                  )}
                  {searchResults.otherMatches.map((f) => (
                    <button
                      key={f.properties.id}
                      onClick={() => handleSelectStop(f)}
                      className="w-full text-left py-1.5 px-2.5 hover:bg-slate-50 flex items-center justify-between text-slate-800 cursor-pointer rounded-lg transition-colors group"
                    >
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600" />
                        <div>
                          <span className="font-semibold text-slate-800 block">{f.properties.name}</span>
                          <span className="text-[10px] text-slate-400">{f.properties.corridor}</span>
                        </div>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {f.properties.boardings.toLocaleString()} pax
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Active Corridor & Route Info Floating Bar — Clean, Minimal & Clutter-Free */}
          {activeCorridor && (
            <div className="bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl px-3 py-1.5 shadow-sm flex items-center justify-between gap-2.5 max-w-[420px] transition-all hover:border-slate-300">
              <div className="flex items-center gap-2 min-w-0">
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${
                    activeCorridor.crowd_level === 'VERY HIGH'
                      ? 'bg-rose-500'
                      : activeCorridor.crowd_level === 'HIGH'
                      ? 'bg-blue-600'
                      : 'bg-emerald-600'
                  }`}
                />
                <span className="font-semibold text-slate-800 text-xs truncate">
                  {activeCorridor.name}
                </span>
              </div>

              <div className="flex items-center gap-1.5 shrink-0">
                <span
                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                    activeCorridor.crowd_level === 'VERY HIGH'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : activeCorridor.crowd_level === 'HIGH'
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  }`}
                >
                  {activeCorridor.crowd_level}
                </span>
                <button
                  onClick={() => handleCorridorChange('')}
                  className="text-slate-400 hover:text-slate-700 p-0.5 rounded hover:bg-slate-100 cursor-pointer transition-colors"
                  title="Clear active route"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Ultra-Clean Minimal Horizontal Legend (Bottom-Left) */}
        <div className="absolute bottom-3 left-3 z-[400] bg-white/95 backdrop-blur-md px-3.5 py-1.5 rounded-xl border border-slate-200 shadow-xs flex items-center gap-3 text-[11px] text-slate-600">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-900 inline-block" />
            <span className="font-medium text-slate-700">Bus Stand</span>
          </div>
          <span className="text-slate-300">•</span>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block" />
            <span className="font-medium text-slate-700">Bus Stop</span>
          </div>
          {activeCorridor && (
            <>
              <span className="text-slate-300">•</span>
              <div className="flex items-center gap-1.5">
                <span
                  className={`w-3.5 h-1 rounded-full inline-block ${
                    activeCorridor.crowd_level === 'VERY HIGH'
                      ? 'bg-rose-600'
                      : activeCorridor.crowd_level === 'HIGH'
                      ? 'bg-blue-600'
                      : 'bg-emerald-600'
                  }`}
                />
                <span className="font-medium text-slate-800">{activeCorridor.name}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
