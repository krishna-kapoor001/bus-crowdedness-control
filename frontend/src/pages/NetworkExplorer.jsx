import React, { useState, useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Tooltip, Polyline, ZoomControl, useMap } from 'react-leaflet';
import L from 'leaflet';
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

// Location Pin Icon cache for high-performance Leaflet marker rendering
const iconCache = new Map();

function getStopLocationPinIcon({ isHub, isSelected, belongsToActive, corridorCrowdLevel, zoom }) {
  const isLarge = zoom >= 14;
  let color = isHub ? '#0F172A' : '#2563EB';
  let w = isHub ? (isLarge ? 22 : 18) : (isLarge ? 17 : 14);
  let h = isHub ? (isLarge ? 28 : 23) : (isLarge ? 22 : 18);

  if (belongsToActive) {
    color =
      corridorCrowdLevel === 'VERY HIGH'
        ? '#DC2626'
        : corridorCrowdLevel === 'HIGH'
        ? '#2563EB'
        : '#059669';
    w = isHub ? 24 : 18;
    h = isHub ? 30 : 23;
  }

  if (isSelected) {
    color = '#EF4444';
    w = 26;
    h = 33;
  }

  const key = `${color}-${w}-${h}-${isHub}-${isSelected}`;
  if (iconCache.has(key)) {
    return iconCache.get(key);
  }

  // Hardware-accelerated SVG with vector shadow (zero blur filter pass = 60 FPS)
  const icon = L.divIcon({
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
                fill="${color}" 
                stroke="#FFFFFF" 
                stroke-width="1.8" 
                stroke-linejoin="round"/>
          <circle cx="12" cy="10" r="${isHub || isSelected ? 4 : 3}" fill="#FFFFFF"/>
          ${(isHub || isSelected) ? `<circle cx="12" cy="10" r="2" fill="${color}"/>` : ''}
        </svg>
      </div>
    `,
    iconSize: [w, h],
    iconAnchor: [w / 2, h],
    popupAnchor: [0, -h - 2],
  });

  iconCache.set(key, icon);
  return icon;
}

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

// High-performance viewport tracker with debounced spatial bounds updates (Zero frame drops)
function MapViewportTracker({ onViewportChange }) {
  const map = useMap();
  const timerRef = useRef(null);

  useEffect(() => {
    const syncViewport = () => {
      clearTimeout(timerRef.current);
      // 100ms debounce ensures smooth continuous 60fps wheel zooming
      timerRef.current = setTimeout(() => {
        if (!map) return;
        const b = map.getBounds();
        onViewportChange({
          zoom: map.getZoom(),
          north: b.getNorth(),
          south: b.getSouth(),
          east: b.getEast(),
          west: b.getWest()
        });
      }, 100);
    };

    map.on('moveend', syncViewport);
    map.on('zoomend', syncViewport);
    syncViewport(); // Initial trigger

    return () => {
      clearTimeout(timerRef.current);
      map.off('moveend', syncViewport);
      map.off('zoomend', syncViewport);
    };
  }, [map, onViewportChange]);

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
  const [viewport, setViewport] = useState({
    zoom: DELHI_DEFAULT_ZOOM,
    north: 28.90,
    south: 28.40,
    east: 77.45,
    west: 76.95
  });

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

  // Filtered stops for search dropdown (searches all 757 verified Delhi stops & 38 Major Bus Stands)
  const searchResults = useMemo(() => {
    if (!geoData?.features) return { corridorMatches: [], otherMatches: [] };
    const query = stopFilter.toLowerCase().trim();

    if (!query) {
      // If no query entered, show stops belonging to active corridor if one is selected
      if (activeCorridor) {
        return { corridorMatches: activeCorridorStops, otherMatches: [] };
      }
      const hubs = geoData.features.filter((f) => f.properties.is_hub);
      const regulars = geoData.features.filter((f) => !f.properties.is_hub);
      return { corridorMatches: [], otherMatches: [...hubs, ...regulars].slice(0, 50) };
    }

    const isBusStandQuery = ['bus stand', 'stand', 'busstand', 'bus-stand', 'bus stands', 'terminal', 'terminals', 'hub', 'hubs'].some((k) => query.includes(k));

    const allMatches = geoData.features.filter((f) => {
      if (isBusStandQuery && f.properties.is_hub) return true;
      const combined = `${f.properties.name.toLowerCase()} ${f.properties.corridor.toLowerCase()} ${f.properties.is_hub ? 'bus stand terminal major hub' : ''}`;
      return combined.includes(query);
    });

    // Prioritize major bus stands at top
    allMatches.sort((a, b) => {
      if (a.properties.is_hub && !b.properties.is_hub) return -1;
      if (!a.properties.is_hub && b.properties.is_hub) return 1;
      return (b.properties.boardings || 0) - (a.properties.boardings || 0);
    });

    if (activeStopNamesSet) {
      const corridorMatches = allMatches.filter((f) =>
        activeStopNamesSet.has(f.properties.name.toLowerCase().trim())
      );
      const otherMatches = allMatches.filter((f) =>
        !activeStopNamesSet.has(f.properties.name.toLowerCase().trim())
      );
      return {
        corridorMatches: corridorMatches.slice(0, 20),
        otherMatches: otherMatches.slice(0, 40),
      };
    }

    return {
      corridorMatches: [],
      otherMatches: allMatches.slice(0, 50),
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
    setTargetView({ center: [lat, lon], zoom: 15, id: Date.now() });
    setShowDropdown(false);
  };

  // Viewport-culled, Level-of-Detail (LOD) filtered bus stops for 60 FPS performance
  const visibleStops = useMemo(() => {
    if (!geoData?.features) return [];
    const { zoom, north, south, east, west } = viewport;

    // 25% viewport buffer so markers don't pop abruptly while panning
    const latBuffer = Math.max(0.015, (north - south) * 0.25);
    const lonBuffer = Math.max(0.015, (east - west) * 0.25);
    const minLat = south - latBuffer;
    const maxLat = north + latBuffer;
    const minLon = west - lonBuffer;
    const maxLon = east + lonBuffer;

    return geoData.features.filter((feature) => {
      const [lon, lat] = feature.geometry.coordinates;
      const { name, is_hub, id, boardings } = feature.properties;
      const isSelected = selectedStop?.id === id;

      // 1. Selected stop is always preserved and rendered
      if (isSelected) return true;

      // 2. Spatial Culling: Ignore stops outside visible screen area
      if (lat < minLat || lat > maxLat || lon < minLon || lon > maxLon) {
        return false;
      }

      // 3. When an active corridor is selected, display only stops belonging to it
      if (activeCorridor) {
        return activeStopNamesSet
          ? activeStopNamesSet.has(name.toLowerCase().trim())
          : false;
      }

      // 4. Adaptive Level-of-Detail (LOD) by Zoom:
      // City Overview (zoom < 12): Show ONLY the 38 Major Bus Stands / Terminals
      if (zoom < 12) {
        return is_hub;
      }

      // Sub-city level (zoom 12 - 13.5): Show hubs + major high-frequency stops
      if (zoom < 13.5) {
        return is_hub || (boardings || 0) >= 400;
      }

      // Neighborhood / Street level (zoom >= 13.5): Show all stops in current viewport
      return true;
    });
  }, [geoData, viewport, selectedStop, activeCorridor, activeStopNamesSet]);

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
            wheelDebounceTime={15}
            wheelPxPerZoomLevel={120}
            zoomSnap={0.5}
            zoomDelta={0.5}
            zoomAnimation={true}
            markerZoomAnimation={true}
            fadeAnimation={true}
            className="w-full h-full"
          >
            <MapController targetView={targetView} />
            <MapViewportTracker onViewportChange={setViewport} />

            {/* Top-Right Visible Zoom Control */}
            <ZoomControl position="topright" />

            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
              updateWhenZooming={false}
              updateInterval={100}
              keepBuffer={4}
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

            {/* Stop Vector Markers with Viewport Culling & Smart Highlighting */}
            {visibleStops.map((feature) => {
              const [lon, lat] = feature.geometry.coordinates;
              const { name, corridor, boardings, is_hub, id } = feature.properties;
              const isSelected = selectedStop?.id === id;
              const belongsToActive = activeStopNamesSet
                ? activeStopNamesSet.has(name.toLowerCase().trim())
                : false;

              const pinIcon = getStopLocationPinIcon({
                isHub: is_hub,
                isSelected,
                belongsToActive,
                corridorCrowdLevel: activeCorridor?.crowd_level,
                zoom: viewport.zoom
              });

              return (
                <Marker
                  key={id}
                  position={[lat, lon]}
                  icon={pinIcon}
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
                      setTargetView({ center: [lat, lon], zoom: 14.5, id: Date.now() });
                    },
                  }}
                >
                  <Tooltip direction="top" offset={[0, -(is_hub ? 26 : 21)]} opacity={0.95}>
                    <div className="font-semibold text-xs text-slate-900">{name}</div>
                    <div className="text-[10px] text-slate-500 font-medium flex items-center gap-1 mt-0.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${is_hub ? 'bg-slate-900' : 'bg-blue-600'}`} />
                      <span>{is_hub ? 'Major Bus Stand' : 'Bus Stop'}</span>
                    </div>
                  </Tooltip>
                </Marker>
              );
            })}
          </MapContainer>
        )}

        {/* Sleek Stop Search Bar (Top-Left) */}
        <div ref={searchContainerRef} className="absolute top-3 left-3 z-[400] flex flex-col gap-2 max-w-[calc(100vw-80px)]">
          {/* Sleek Search Container */}
          <div className="bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200/90 shadow-md flex items-center transition-all hover:border-slate-300">
            <div className="relative flex items-center min-w-[280px] sm:min-w-[360px] px-3.5 py-2">
              <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
              <input
                type="text"
                placeholder="Search bus stops across Delhi..."
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

              {/* Group 2: Matching Delhi Bus Stops */}
              {searchResults.otherMatches.length > 0 && (
                <div className="p-1">
                  {searchResults.otherMatches.map((f) => (
                    <button
                      key={f.properties.id}
                      onClick={() => handleSelectStop(f)}
                      className="w-full text-left py-2 px-2.5 hover:bg-slate-50 flex items-center justify-between text-slate-800 cursor-pointer rounded-xl transition-colors group"
                    >
                      <div className="flex items-center gap-2">
                        <MapPin className={`w-3.5 h-3.5 ${f.properties.is_hub ? 'text-blue-600' : 'text-slate-400'} group-hover:text-blue-600 transition-colors`} />
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="font-semibold text-slate-800 block text-xs">{f.properties.name}</span>
                            {f.properties.is_hub && (
                              <span className="text-[9px] font-mono font-bold text-blue-600 bg-blue-50 px-1 py-0.2 rounded shrink-0">
                                Bus Stand
                              </span>
                            )}
                          </div>
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

          {/* Empty Search State */}
          {showDropdown && stopFilter.trim() && searchResults.corridorMatches.length === 0 && searchResults.otherMatches.length === 0 && (
            <div className="bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-xl p-3 text-xs text-slate-400 text-center w-full sm:w-[360px]">
              No bus stops found matching "{stopFilter}"
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
            <MapPin className="w-3.5 h-3.5 text-slate-900 fill-slate-900" />
            <span className="font-medium text-slate-700">Major Bus Stand</span>
          </div>
          <span className="text-slate-300">•</span>
          <div className="flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-blue-600 fill-blue-600" />
            <span className="font-medium text-slate-700">Bus Stop</span>
          </div>
          {viewport.zoom < 12.5 && !activeCorridor && (
            <>
              <span className="text-slate-300">•</span>
              <span className="text-[10px] text-slate-400 font-medium">Zoom in for street stops</span>
            </>
          )}
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
