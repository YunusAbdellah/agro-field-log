import React, { useEffect, useState } from "react";
import { api } from "./api";

const INITIAL_PLOT_FORM = {
  name: "",
  area_ha: "10.00",
  soil_type: "Lehm",
  current_crop: "Winterweizen",
  season_year: 2026,
  notes: "",
};

const INITIAL_ACTIVITY_FORM = {
  plot: "",
  activity_type: "fertilization",
  activity_date: new Date().toISOString().slice(0, 10),
  product_or_input: "",
  quantity: "100.00",
  unit: "kg/ha",
  notes: "",
};

export default function App() {
  const [plots, setPlots] = useState([]);
  const [selectedPlotId, setSelectedPlotId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [activities, setActivities] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [search, setSearch] = useState("");
  const [plotForm, setPlotForm] = useState(INITIAL_PLOT_FORM);
  const [activityForm, setActivityForm] = useState(INITIAL_ACTIVITY_FORM);
  const [statusMsg, setStatusMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  async function loadAll(targetPlotId = selectedPlotId, searchTerm = search) {
    try {
      setErrorMsg("");
      const [plotList, alertList] = await Promise.all([
        api.getPlots(searchTerm),
        api.getAlerts(false),
      ]);
      setPlots(plotList);
      setAlerts(alertList);

      const activeId = targetPlotId || (plotList[0] ? plotList[0].id : null);
      setSelectedPlotId(activeId);

      if (activeId) {
        const [plotSummary, plotActivities] = await Promise.all([
          api.getPlotSummary(activeId),
          api.getActivities(activeId),
        ]);
        setSummary(plotSummary);
        setActivities(plotActivities);
        setActivityForm((prev) => ({ ...prev, plot: String(activeId) }));
      } else {
        setSummary(null);
        setActivities([]);
      }
    } catch (err) {
      setErrorMsg(`Failed to load data: ${err.message}`);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleSearchSubmit(e) {
    e.preventDefault();
    await loadAll(selectedPlotId, search);
  }

  async function handleCreatePlot(e) {
    e.preventDefault();
    try {
      setErrorMsg("");
      const created = await api.createPlot({
        ...plotForm,
        area_ha: Number(plotForm.area_ha),
        season_year: Number(plotForm.season_year),
      });
      setPlotForm(INITIAL_PLOT_FORM);
      setStatusMsg(`Added plot "${created.name}".`);
      await loadAll(created.id, search);
    } catch (err) {
      setErrorMsg(`Could not create plot: ${err.message}`);
    }
  }

  async function handleCreateActivity(e) {
    e.preventDefault();
    const targetId = activityForm.plot || selectedPlotId;
    if (!targetId) return;
    try {
      setErrorMsg("");
      await api.createActivity({
        ...activityForm,
        plot: Number(targetId),
        quantity: Number(activityForm.quantity),
      });
      setActivityForm((prev) => ({
        ...INITIAL_ACTIVITY_FORM,
        plot: String(targetId),
        activity_date: prev.activity_date,
      }));
      setStatusMsg("Logged activity and evaluated agronomic/weather alert rules.");
      await loadAll(Number(targetId), search);
    } catch (err) {
      setErrorMsg(`Could not log activity: ${err.message}`);
    }
  }

  async function handleResolveAlert(alertId) {
    try {
      await api.resolveAlert(alertId);
      setStatusMsg("Alert marked as resolved.");
      await loadAll(selectedPlotId, search);
    } catch (err) {
      setErrorMsg(`Could not resolve alert: ${err.message}`);
    }
  }

  async function handleScanInactivity() {
    try {
      await api.scanInactivity();
      setStatusMsg("Ran plot inactivity check across all plots.");
      await loadAll(selectedPlotId, search);
    } catch (err) {
      setErrorMsg(`Inactivity scan failed: ${err.message}`);
    }
  }

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <h1>AgroLog</h1>
          <p className="subtitle">Digitale Ackerschlagkartei · Plot Logs, Input Totals & Threshold Alerts</p>
        </div>
        <form onSubmit={handleSearchSubmit} className="search-box">
          <input
            type="text"
            placeholder="Search plot or crop (e.g. Weizen)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit">Filter</button>
        </form>
      </header>

      {statusMsg && <div className="banner success">{statusMsg}</div>}
      {errorMsg && <div className="banner error">{errorMsg}</div>}

      <div className="grid-main">
        {/* Left Column: Plots & Create Plot */}
        <section className="card">
          <h2>Field Plots ({plots.length})</h2>
          <div className="plot-list">
            {plots.map((p) => (
              <div
                key={p.id}
                className={`plot-item ${p.id === selectedPlotId ? "active" : ""}`}
                onClick={() => loadAll(p.id, search)}
              >
                <div className="plot-title-row">
                  <strong>{p.name}</strong>
                  {p.open_alerts_count > 0 && (
                    <span className="badge warn">{p.open_alerts_count} alert</span>
                  )}
                </div>
                <div className="muted">
                  {p.current_crop} · {p.area_ha} ha · Soil: {p.soil_type} ({p.season_year})
                </div>
              </div>
            ))}
            {plots.length === 0 && <p className="muted">No plots match your filter.</p>}
          </div>

          <h3 className="mt-16">Add Field Plot</h3>
          <form onSubmit={handleCreatePlot} className="stack-form">
            <input
              type="text"
              placeholder="Plot name (e.g. Schlag West)"
              value={plotForm.name}
              onChange={(e) => setPlotForm({ ...plotForm, name: e.target.value })}
              required
            />
            <div className="row-2">
              <input
                type="number"
                step="0.01"
                placeholder="Area (ha)"
                value={plotForm.area_ha}
                onChange={(e) => setPlotForm({ ...plotForm, area_ha: e.target.value })}
                required
              />
              <select
                value={plotForm.soil_type}
                onChange={(e) => setPlotForm({ ...plotForm, soil_type: e.target.value })}
              >
                <option value="Lehm">Lehm</option>
                <option value="Sand">Sand</option>
                <option value="Ton">Ton</option>
                <option value="Schluff">Schluff</option>
                <option value="Mischboden">Mischboden</option>
              </select>
            </div>
            <div className="row-2">
              <input
                type="text"
                placeholder="Crop (e.g. Wintergerste)"
                value={plotForm.current_crop}
                onChange={(e) => setPlotForm({ ...plotForm, current_crop: e.target.value })}
                required
              />
              <input
                type="number"
                value={plotForm.season_year}
                onChange={(e) => setPlotForm({ ...plotForm, season_year: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="primary">Save Plot</button>
          </form>
        </section>

        {/* Middle Column: Selected Plot Summary & Activity Log */}
        <section className="card">
          {summary ? (
            <>
              <h2>{summary.plot_name} — Season {summary.season_year}</h2>
              <div className="kpi-row">
                <div className="kpi">
                  <span>Crop</span>
                  <strong>{summary.current_crop}</strong>
                </div>
                <div className="kpi">
                  <span>Area</span>
                  <strong>{summary.area_ha} ha</strong>
                </div>
                <div className="kpi">
                  <span>Activities</span>
                  <strong>{summary.total_activities}</strong>
                </div>
              </div>

              <div className="totals-box">
                <strong>Logged Input Totals by Unit:</strong>{" "}
                {Object.keys(summary.totals_by_unit).length > 0
                  ? Object.entries(summary.totals_by_unit)
                      .map(([unit, val]) => `${val} ${unit}`)
                      .join(" · ")
                  : "No activities logged yet."}
              </div>

              <h3 className="mt-16">Log Field Activity</h3>
              <form onSubmit={handleCreateActivity} className="stack-form">
                <div className="row-2">
                  <select
                    value={activityForm.activity_type}
                    onChange={(e) => setActivityForm({ ...activityForm, activity_type: e.target.value })}
                  >
                    <option value="sowing">Sowing / Aussaat</option>
                    <option value="fertilization">Fertilization / Düngung</option>
                    <option value="crop_protection">Crop Protection / Pflanzenschutz</option>
                    <option value="irrigation">Irrigation / Bewässerung</option>
                    <option value="harvest">Harvest / Ernte</option>
                    <option value="soil_check">Soil Check / Bodenprobe</option>
                  </select>
                  <input
                    type="date"
                    value={activityForm.activity_date}
                    onChange={(e) => setActivityForm({ ...activityForm, activity_date: e.target.value })}
                    required
                  />
                </div>
                <input
                  type="text"
                  placeholder="Product / Input (e.g. KAS 27, NPK, Tropfbewässerung)"
                  value={activityForm.product_or_input}
                  onChange={(e) => setActivityForm({ ...activityForm, product_or_input: e.target.value })}
                  required
                />
                <div className="row-2">
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Quantity"
                    value={activityForm.quantity}
                    onChange={(e) => setActivityForm({ ...activityForm, quantity: e.target.value })}
                    required
                  />
                  <select
                    value={activityForm.unit}
                    onChange={(e) => setActivityForm({ ...activityForm, unit: e.target.value })}
                  >
                    <option value="kg/ha">kg/ha</option>
                    <option value="L/ha">L/ha</option>
                    <option value="mm">mm</option>
                    <option value="t/ha">t/ha</option>
                    <option value="unit">unit</option>
                  </select>
                </div>
                <button type="submit" className="primary">Record Activity</button>
              </form>

              <h3 className="mt-16">Activity History</h3>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Input / Note</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activities.map((a) => (
                      <tr key={a.id}>
                        <td>{a.activity_date}</td>
                        <td>{a.activity_type_label}</td>
                        <td>{a.product_or_input}</td>
                        <td>{a.quantity} {a.unit}</td>
                      </tr>
                    ))}
                    {activities.length === 0 && (
                      <tr>
                        <td colSpan="4" className="muted">No activities recorded for this plot yet.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="muted">Select or create a plot to view activity details.</p>
          )}
        </section>

        {/* Right Column: Alerts & Agronomic Checks */}
        <section className="card">
          <div className="row-between">
            <h2>Open Alerts ({alerts.length})</h2>
            <button onClick={handleScanInactivity}>Scan Inactivity</button>
          </div>
          <div className="alert-list">
            {alerts.map((al) => (
              <div key={al.id} className="alert-card">
                <div className="alert-top">
                  <strong>{al.plot_name}</strong>
                  <span className="badge warn">{al.severity}</span>
                </div>
                <p>{al.message}</p>
                <button onClick={() => handleResolveAlert(al.id)}>Resolve</button>
              </div>
            ))}
            {alerts.length === 0 && (
              <p className="muted">All clear — no open agronomic or weather alerts.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
