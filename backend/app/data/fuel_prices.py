"""
State-wise fuel prices (₹/L or ₹/kWh).

Priority: live scraped data (fuel_prices_live.json) > static baseline below.
The scraper runs weekly via background scheduler or manual: python scripts/scrape_fuel_prices.py
"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

_DATA_DIR = Path(__file__).resolve().parent
_LIVE_FILE = _DATA_DIR / "fuel_prices_live.json"
_MAX_AGE = timedelta(days=7)

FUEL_PRICES = {
    "AN": {"petrol": 96, "diesel": 88, "cng": 74, "ev": 4.0},
    "AP": {"petrol": 108, "diesel": 95, "cng": 80, "ev": 3.8},
    "AR": {"petrol": 92, "diesel": 86, "cng": 72, "ev": 4.0},
    "AS": {"petrol": 97, "diesel": 88, "cng": 75, "ev": 4.0},
    "BR": {"petrol": 107, "diesel": 94, "cng": 78, "ev": 4.2},
    "CH": {"petrol": 95, "diesel": 88, "cng": 74, "ev": 3.5},
    "CG": {"petrol": 103, "diesel": 91, "cng": 77, "ev": 4.0},
    "DN": {"petrol": 95, "diesel": 89, "cng": 73, "ev": 3.5},
    "DL": {"petrol": 95, "diesel": 88, "cng": 76, "ev": 3.0},
    "GA": {"petrol": 96, "diesel": 88, "cng": 74, "ev": 3.8},
    "GJ": {"petrol": 96, "diesel": 92, "cng": 74, "ev": 3.5},
    "HR": {"petrol": 97, "diesel": 90, "cng": 75, "ev": 3.5},
    "HP": {"petrol": 95, "diesel": 88, "cng": 73, "ev": 3.5},
    "JK": {"petrol": 96, "diesel": 90, "cng": 74, "ev": 3.8},
    "JH": {"petrol": 104, "diesel": 91, "cng": 77, "ev": 4.0},
    "KA": {"petrol": 102, "diesel": 88, "cng": 75, "ev": 4.0},
    "KL": {"petrol": 108, "diesel": 97, "cng": 81, "ev": 4.0},
    "LA": {"petrol": 96, "diesel": 90, "cng": 74, "ev": 3.8},
    "LD": {"petrol": 92, "diesel": 86, "cng": 72, "ev": 4.0},
    "MP": {"petrol": 108, "diesel": 94, "cng": 78, "ev": 4.0},
    "MH": {"petrol": 106, "diesel": 93, "cng": 79, "ev": 3.5},
    "MN": {"petrol": 98, "diesel": 89, "cng": 76, "ev": 4.0},
    "ML": {"petrol": 98, "diesel": 89, "cng": 76, "ev": 4.0},
    "MZ": {"petrol": 98, "diesel": 89, "cng": 76, "ev": 4.0},
    "NL": {"petrol": 98, "diesel": 89, "cng": 76, "ev": 4.0},
    "OD": {"petrol": 103, "diesel": 90, "cng": 77, "ev": 4.0},
    "PY": {"petrol": 97, "diesel": 90, "cng": 75, "ev": 3.8},
    "PB": {"petrol": 97, "diesel": 90, "cng": 76, "ev": 3.8},
    "RJ": {"petrol": 108, "diesel": 93, "cng": 76, "ev": 4.0},
    "SK": {"petrol": 92, "diesel": 86, "cng": 72, "ev": 4.0},
    "TN": {"petrol": 102, "diesel": 92, "cng": 77, "ev": 4.2},
    "TS": {"petrol": 108, "diesel": 95, "cng": 80, "ev": 3.8},
    "TR": {"petrol": 98, "diesel": 89, "cng": 76, "ev": 4.0},
    "UP": {"petrol": 97, "diesel": 90, "cng": 75, "ev": 3.8},
    "UK": {"petrol": 96, "diesel": 89, "cng": 74, "ev": 3.8},
    "WB": {"petrol": 106, "diesel": 93, "cng": 78, "ev": 3.8},
}


def _read_live_file():
    """Read and parse the live JSON file. Returns (data_dict, error_str|None)."""
    if not _LIVE_FILE.exists():
        return None, "file_missing"
    try:
        with open(_LIVE_FILE, encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def get_fuel_prices_live():
    """Return (prices_by_state, last_updated_iso) from scraped JSON if present."""
    data, err = _read_live_file()
    if data:
        return data.get("prices", FUEL_PRICES), data.get("last_updated")
    return FUEL_PRICES, None


def get_fuel_price_status() -> dict:
    """Full status for the /fuel-prices/live/meta endpoint."""
    data, err = _read_live_file()
    if not data:
        return {
            "source": "static",
            "last_updated": None,
            "age_hours": None,
            "is_stale": True,
            "next_refresh_hint": "Run scraper or start backend to auto-refresh",
        }
    ts = data.get("last_updated")
    if not ts:
        return {"source": "live", "last_updated": None, "age_hours": None, "is_stale": True}
    try:
        updated = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - updated
        age_h = round(age.total_seconds() / 3600, 1)
        stale = age > _MAX_AGE
        return {
            "source": "live",
            "last_updated": ts,
            "age_hours": age_h,
            "is_stale": stale,
            "next_refresh_hint": "Will auto-refresh when stale" if not stale else "Refresh pending",
        }
    except Exception:
        return {"source": "mypetrolprice.com", "last_updated": ts, "age_hours": None, "is_stale": True}
