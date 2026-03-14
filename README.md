# TCO Calculator — India 4-Wheeler PV

**Total Cost of Ownership** for passenger vehicles in India. Compare up to 3 vehicles (petrol, diesel, CNG, EV, strong hybrid) across 1–15 years with state-wise life tax, IRDAI insurance, and resale.

- **Backend:** Python (FastAPI), APIs for reference data + TCO calculation
- **Frontend:** React + Vite, consumes backend via REST
- **Local hosting:** Backend on port 8000, frontend on 5173 with proxy to API

## Repo structure

```
TCO-Calculator/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── main.py          # App entry, CORS, routes
│   │   ├── config.py        # Settings (env)
│   │   ├── api/v1/tco.py    # Controllers (HTTP → service)
│   │   ├── services/        # Business logic (TCO calc)
│   │   ├── data/            # States, fuel prices, car DB
│   │   └── util/            # Constants (IRDAI, etc.)
│   └── requirements.txt
├── frontend/                # React + Vite
│   ├── src/
│   │   ├── api/client.js    # API client (states, brands, calculate)
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js       # Dev proxy → backend
│   └── package.json
└── README.md
```

## Run locally

### 1. Backend (port 8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API root:** http://localhost:8000  
- **Swagger UI:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

- **App:** http://localhost:5173  
- Vite proxies `/api` to `http://localhost:8000`, so the app calls the backend with no CORS issues.

### 3. Build for deployment

```bash
cd frontend
npm run build
```

Serve the `dist/` folder (e.g. Nginx, Vercel, or same host as API). Set `VITE_API_URL` to your API base URL (e.g. `https://api.yourdomain.com`) when building for production.

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tco/states` | List states (code, name) |
| GET | `/api/v1/tco/fuel-prices/{state}` | Fuel prices for state |
| GET | `/api/v1/tco/brands` | Car brands |
| GET | `/api/v1/tco/brands/{brand}/models` | Models for brand |
| POST | `/api/v1/tco/calculate` | Compute TCO (1–3 vehicles) |

Request body for `POST /api/v1/tco/calculate`:

```json
{
  "vehicles": [
    {
      "v": 1,
      "state": "MH",
      "fuel": "petrol",
      "ex": 1000000,
      "num_years": 5,
      "cash": true,
      "mileage": 18,
      "fuel_price": 106,
      "ann_km": 15000,
      "eng": "mid"
    }
  ],
  "num_years_global": 5
}
```

See **Swagger** at `/docs` for full request/response schemas.

## Migrating from the single HTML version

The original [kapil433/TCO-Calculator](https://github.com/kapil433/TCO-Calculator) had one `index.html` with all logic and data inline. This revision:

1. **Backend** holds data (states, fuel, car DB) and TCO logic; exposes REST APIs.
2. **Frontend** is a React app that loads states/brands from the API and posts to `/calculate` to get results.
3. You can keep the original `index.html` in the repo as `legacy/` or replace it. The API response shape matches what the original JS used (`tco`, `bd`, `resalePerYear`, etc.) so you can port the full UI (charts, breakdown, fleet) to React step by step.

## Fuel prices (mypetrolprice.com)

To refresh state-wise fuel prices from [mypetrolprice.com](https://www.mypetrolprice.com/), run the scraper weekly (e.g. via Task Scheduler or cron):

```bash
cd backend
.venv\Scripts\activate
python scripts/scrape_fuel_prices.py
```

Output: `app/data/fuel_prices_live.json`. The API serves this file when present; otherwise it uses the built-in static prices. The frontend shows "Fuel prices: mypetrolprice.com · updated &lt;date&gt;" when live data is available.

## Optional: database

For now the backend uses in-memory data (Python dicts). To add SQLite/MySQL later:

- Add `app/repositories/` and DB connection in `config.py` (e.g. `DATABASE_URL` from env).
- Move `CAR_DB`, fuel prices, or state overrides into DB if you need admin-editable data. The calculation logic stays in `services/tco_service.py`.
