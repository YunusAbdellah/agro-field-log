# AgroLog — Smart Field & Crop Activity Log (*Digitale Ackerschlagkartei*)

**AgroLog** is a full-stack AgriTech web application designed for farm plots (*Ackerschläge*), field activity tracking (*Maßnahmen*: sowing, fertilization, crop protection, irrigation, harvest, soil checks), seasonal input summaries, and automated agronomic/weather threshold alerts.

Built to bridge **agronomy domain workflows** with **modern software engineering** (Python, Django REST Framework, PostgreSQL, React, and Docker).

---

## Key Features

1. **Field Plot Management (*Schlagverwaltung*):** Create, inspect, and filter agricultural plots by crop type, season year, soil type, and search term.
2. **Activity Logging (*Ackerschlagkartei*):** Record field operations with dates, inputs (*NPK*, plant protection, irrigation), quantities, and units (`kg/ha`, `L/ha`, `mm`, `t/ha`).
3. **Automatic Agronomic & Weather Alert Engine:**
   - **High Input Rate Alert:** Flags when a single application exceeds a plot/rule threshold (e.g., `> 180 kg/ha` or `> 250 L/ha`).
   - **Field Inactivity Alert:** Flags plots with no recorded activity for more than `N` days during an active season.
   - **Weather / Dry-Spell / Rain Check:** Integrates Open-Meteo forecast data (with a deterministic fallback for offline/demo environments) to flag dry soil risk or upcoming rain windows before spraying/fertilizing.
4. **Season Summary & Alert Resolution:** Aggregated per-plot input totals by unit/activity type and one-click alert resolution.

---

## Tech Stack

- **Backend:** Python 3.12, Django 5, Django REST Framework (`DRF`), `django-cors-headers`
- **Database:** PostgreSQL 16 (with SQLite fallback option for lightweight local test runs)
- **Frontend:** React 18, Vite, CSS Grid/Flexbox dashboard UI
- **DevOps:** Docker, Docker Compose, automated Django `APITestCase` test suite, demo seed management command

---

## Quickstart with Docker Compose

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
2. Start PostgreSQL, Backend API, and Frontend:
   ```bash
   docker-compose up --build
   ```
3. Open the application:
   - **Frontend Dashboard:** `http://localhost:5173`
   - **Backend REST API:** `http://localhost:8000/api/`
   - **Django Admin:** `http://localhost:8000/admin/`

---

## Running Backend Tests

Inside the `backend/` directory (or inside the backend container):

```bash
python manage.py test
```

---

## Architecture Highlights & Interview Talking Points

- **Separation of Domain Logic:** Agronomic rule evaluation and weather retrieval live in `agro/services/alert_engine.py` and `agro/services/weather_service.py` rather than fat views or models, making rules easy to test and extend.
- **Resilient External Integration:** Weather lookups call Open-Meteo with a timeout and structured fallback so demos and automated tests never fail due to network flakiness.
- **Domain-Driven Data Modeling:** Models `FieldPlot`, `FieldActivity`, `AlertRule`, and `FieldAlert` cleanly represent multi-season crop logs and unit-aware input quantities.
