const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(errText || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getPlots: (search = "") => {
    const q = search ? `?search=${encodeURIComponent(search)}` : "";
    return request(`/plots/${q}`);
  },
  createPlot: (payload) =>
    request("/plots/", { method: "POST", body: JSON.stringify(payload) }),
  getPlotSummary: (plotId) => request(`/plots/${plotId}/summary/`),
  getActivities: (plotId = "") => {
    const q = plotId ? `?plot=${plotId}` : "";
    return request(`/activities/${q}`);
  },
  createActivity: (payload) =>
    request("/activities/", { method: "POST", body: JSON.stringify(payload) }),
  getAlerts: (resolved = false) => request(`/alerts/?resolved=${resolved}`),
  resolveAlert: (alertId) =>
    request(`/alerts/${alertId}/resolve/`, { method: "POST" }),
  scanInactivity: () =>
    request("/alerts/scan_inactivity/", { method: "POST" }),
};
