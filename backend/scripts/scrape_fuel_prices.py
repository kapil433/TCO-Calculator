"""
Weekly scraper for fuel prices from mypetrolprice.com.

Can be run standalone:  python scripts/scrape_fuel_prices.py [--force]
Or called from the app's background scheduler.

Output: backend/app/data/fuel_prices_live.json
Source: https://www.mypetrolprice.com/
"""
import json
import re
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Install: pip install requests beautifulsoup4")
    raise

# mypetrolprice.com uses numeric state IDs in URLs
# URL pattern: https://www.mypetrolprice.com/{stateId}/Fuel-Prices-in-{State_Slug}
# This single "all fuel" page contains average prices for petrol, diesel, and CNG.
STATE_REGISTRY = {
    "AN": {"id": 1,  "slug": "Andaman_and_Nicobar_Islands", "name": "Andaman and Nicobar Islands"},
    "AP": {"id": 2,  "slug": "Andhra_Pradesh",              "name": "Andhra Pradesh"},
    "AR": {"id": 3,  "slug": "Arunachal_Pradesh",           "name": "Arunachal Pradesh"},
    "AS": {"id": 4,  "slug": "Assam",                       "name": "Assam"},
    "BR": {"id": 5,  "slug": "Bihar",                       "name": "Bihar"},
    "CH": {"id": 6,  "slug": "Chandigarh",                  "name": "Chandigarh"},
    "CG": {"id": 7,  "slug": "Chhattisgarh",                "name": "Chhattisgarh"},
    "DN": {"id": 8,  "slug": "Dadra_and_Nagar_Haveli",      "name": "Dadra and Nagar Haveli"},
    "DL": {"id": 10, "slug": "Delhi",                       "name": "Delhi"},
    "GA": {"id": 11, "slug": "Goa",                         "name": "Goa"},
    "GJ": {"id": 12, "slug": "Gujarat",                     "name": "Gujarat"},
    "HR": {"id": 13, "slug": "Haryana",                     "name": "Haryana"},
    "HP": {"id": 14, "slug": "Himachal_Pradesh",            "name": "Himachal Pradesh"},
    "JK": {"id": 15, "slug": "Jammu_and_Kashmir",           "name": "Jammu and Kashmir"},
    "JH": {"id": 16, "slug": "Jharkhand",                   "name": "Jharkhand"},
    "KA": {"id": 17, "slug": "Karnataka",                   "name": "Karnataka"},
    "KL": {"id": 18, "slug": "Kerala",                      "name": "Kerala"},
    "MP": {"id": 19, "slug": "Madhya_Pradesh",              "name": "Madhya Pradesh"},
    "MH": {"id": 20, "slug": "Maharashtra",                 "name": "Maharashtra"},
    "MN": {"id": 21, "slug": "Manipur",                     "name": "Manipur"},
    "ML": {"id": 22, "slug": "Meghalaya",                   "name": "Meghalaya"},
    "MZ": {"id": 23, "slug": "Mizoram",                     "name": "Mizoram"},
    "NL": {"id": 24, "slug": "Nagaland",                    "name": "Nagaland"},
    "OD": {"id": 25, "slug": "Odisha",                      "name": "Odisha"},
    "PY": {"id": 28, "slug": "Puducherry",                  "name": "Puducherry"},
    "PB": {"id": 29, "slug": "Punjab",                      "name": "Punjab"},
    "RJ": {"id": 30, "slug": "Rajasthan",                   "name": "Rajasthan"},
    "SK": {"id": 31, "slug": "Sikkim",                      "name": "Sikkim"},
    "TN": {"id": 33, "slug": "Tamil_Nadu",                  "name": "Tamil Nadu"},
    "TS": {"id": 34, "slug": "Telangana",                   "name": "Telangana"},
    "TR": {"id": 35, "slug": "Tripura",                     "name": "Tripura"},
    "UP": {"id": 36, "slug": "Uttar_Pradesh",               "name": "Uttar Pradesh"},
    "UK": {"id": 37, "slug": "Uttarakhand",                 "name": "Uttarakhand"},
    "WB": {"id": 38, "slug": "West_Bengal",                 "name": "West Bengal"},
}

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_FILE = BASE_DIR / "app" / "data" / "fuel_prices_live.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MAX_AGE = timedelta(days=7)
REQUEST_DELAY = 1.5  # seconds between requests to be polite


def is_stale() -> bool:
    """Return True if live data doesn't exist or is older than MAX_AGE."""
    if not OUT_FILE.exists():
        return True
    try:
        with open(OUT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        ts = data.get("last_updated")
        if not ts:
            return True
        updated = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - updated
        return age > MAX_AGE
    except Exception:
        return True


def get_age_info() -> dict:
    """Return {exists, last_updated, age_hours, is_stale} for status reporting."""
    if not OUT_FILE.exists():
        return {"exists": False, "last_updated": None, "age_hours": None, "is_stale": True}
    try:
        with open(OUT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        ts = data.get("last_updated")
        if not ts:
            return {"exists": True, "last_updated": None, "age_hours": None, "is_stale": True}
        updated = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - updated
        return {
            "exists": True,
            "last_updated": ts,
            "age_hours": round(age.total_seconds() / 3600, 1),
            "is_stale": age > MAX_AGE,
        }
    except Exception:
        return {"exists": True, "last_updated": None, "age_hours": None, "is_stale": True}


def _extract_averages(html: str) -> dict:
    """
    Parse the "All Fuel" state page to extract average prices for each fuel type.
    The page has sections: Petrol, Diesel, AutoGas, CNG — each with Cheapest/Average/Costliest.
    A real section header is a fuel name immediately followed by "Cheapest" on the next line,
    distinguishing it from fuel names appearing as link text within other sections.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    fuels_we_want = {"Petrol", "Diesel", "CNG"}
    sections = {}  # fuel_name -> (start_index, end_index)

    for i in range(len(lines) - 1):
        if lines[i] in fuels_we_want and lines[i + 1] == "Cheapest":
            sections[lines[i].lower()] = i

    section_starts = sorted(sections.values())

    result = {}
    for fuel, start in sections.items():
        next_idx = len(lines)
        for s in section_starts:
            if s > start:
                next_idx = s
                break
        saw_average = False
        for j in range(start, next_idx):
            if lines[j] == "Average":
                saw_average = True
            elif saw_average and "₹" in lines[j]:
                m = re.search(r"₹\s*([\d.]+)", lines[j])
                if m:
                    result[fuel] = float(m.group(1))
                break

    return result


def scrape_state_all_fuels(code: str, info: dict, retries: int = 2) -> dict | None:
    """
    Scrape the combined "Fuel Prices in {State}" page with retry on transient errors.
    Returns {"petrol": X, "diesel": Y, "cng": Z, "ev": 4.0} or None on failure.
    """
    url = f"https://www.mypetrolprice.com/{info['id']}/Fuel-Prices-in-{info['slug']}"
    for attempt in range(1, retries + 2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            avgs = _extract_averages(r.text)
            if avgs.get("petrol") or avgs.get("diesel"):
                avgs["ev"] = 4.0
                if "cng" not in avgs:
                    avgs["cng"] = None
                return avgs
            return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt <= retries:
                wait = attempt * 3
                print(f"retry in {wait}s ({e})...", end=" ", flush=True)
                time.sleep(wait)
            else:
                print(f"  Error for {info['name']}: {e}")
                return None
        except Exception as e:
            print(f"  Error for {info['name']}: {e}")
            return None


def run_scrape(force: bool = False) -> dict:
    """
    Main scrape routine. Returns summary dict.
    Skips if data is fresh (< 7 days) unless force=True.
    """
    age = get_age_info()
    if not force and not age["is_stale"]:
        msg = f"Fuel prices are fresh ({age['age_hours']}h old, max {MAX_AGE.days * 24}h). Skipping."
        print(msg)
        return {"skipped": True, "reason": msg, **age}

    sys.path.insert(0, str(BASE_DIR))
    from app.data.fuel_prices import FUEL_PRICES

    print("Scraping fuel prices from mypetrolprice.com (all-fuel state pages)...")
    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "source": "mypetrolprice.com",
        "prices": {},
    }
    scraped = 0
    fallback = 0

    for code, info in STATE_REGISTRY.items():
        print(f"  {info['name']} ({code})...", end=" ", flush=True)
        row = scrape_state_all_fuels(code, info)
        if row and (row.get("petrol") or row.get("diesel")):
            data["prices"][code] = row
            scraped += 1
            print(f"petrol={row.get('petrol')} diesel={row.get('diesel')} cng={row.get('cng')}")
        else:
            data["prices"][code] = FUEL_PRICES.get(code, FUEL_PRICES.get("MH", {}))
            fallback += 1
            print("fallback (static)")
        time.sleep(REQUEST_DELAY)

    # Fill in any codes from static data that aren't on the site (e.g., LA, LD)
    for code in FUEL_PRICES:
        if code not in data["prices"]:
            data["prices"][code] = FUEL_PRICES[code]

    os.makedirs(OUT_FILE.parent, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    summary = {
        "skipped": False,
        "states_scraped": scraped,
        "states_fallback": fallback,
        "total": scraped + fallback,
        "last_updated": data["last_updated"],
        "file": str(OUT_FILE),
    }
    print(f"\nDone: {scraped} scraped, {fallback} fallback, saved to {OUT_FILE}")
    return summary


if __name__ == "__main__":
    force = "--force" in sys.argv
    run_scrape(force=force)
