const API_BASE = '/api/v1';

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error('Failed to load overview data');
  return res.json();
}

export async function planJourney(params) {
  const res = await fetch(`${API_BASE}/journey/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to plan journey');
  return res.json();
}

export async function fetchStops(query = '') {
  const url = query ? `${API_BASE}/journey/stops?query=${encodeURIComponent(query)}` : `${API_BASE}/journey/stops`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load stops');
  return res.json();
}

export async function fetchRoutes() {
  const res = await fetch(`${API_BASE}/journey/routes`);
  if (!res.ok) throw new Error('Failed to load routes');
  return res.json();
}

export async function fetchHourlyAnalytics(route = 'ALL') {
  const url = route && route !== 'ALL' 
    ? `${API_BASE}/analytics/hourly?route=${encodeURIComponent(route)}`
    : `${API_BASE}/analytics/hourly`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load hourly analytics');
  return res.json();
}

export async function fetchRouteAnalytics(sortBy = 'passengers') {
  const res = await fetch(`${API_BASE}/analytics/routes?sort_by=${sortBy}`);
  if (!res.ok) throw new Error('Failed to load route analytics');
  return res.json();
}

export async function fetchStopAnalytics() {
  const res = await fetch(`${API_BASE}/analytics/stops`);
  if (!res.ok) throw new Error('Failed to load stop analytics');
  return res.json();
}

export async function runSimulation(params) {
  const res = await fetch(`${API_BASE}/simulation/shift`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to execute simulation');
  return res.json();
}

export async function fetchModelInfo() {
  const res = await fetch(`${API_BASE}/models/info`);
  if (!res.ok) throw new Error('Failed to load model benchmarks');
  return res.json();
}

export async function fetchNetworkGeo() {
  const [geoRes, corrRes] = await Promise.all([
    fetch(`${API_BASE}/network/geojson`),
    fetch(`${API_BASE}/network/corridors`)
  ]);
  const geojson = await geoRes.json();
  const corridors = await corrRes.json();
  return { geojson, corridors };
}

