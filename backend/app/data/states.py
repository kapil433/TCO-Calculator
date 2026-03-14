"""
State tax and fuel data — all 36 states & UTs.
Tax functions return ABSOLUTE rupee amount (not rate).
Keys: p=petrol, d=diesel, c=cng, e=ev
"""

# State codes (dropdown order)
STATE_CODES = [
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DN", "DL", "GA", "GJ", "HR", "HP",
    "JK", "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OD",
    "PY", "PB", "RJ", "SK", "TN", "TS", "TR", "UP", "UK", "WB",
]

# State display names
STATE_NAMES = {
    "AN": "Andaman & Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CH": "Chandigarh",
    "CG": "Chhattisgarh",
    "DN": "Dadra & Nagar Haveli and Daman & Diu",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu & Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PY": "Puducherry",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal",
}


def _pct(x, rate):
    """Return x * rate (absolute rupees)."""
    return round(x * rate)


def get_tax(state_code: str, fuel: str, ex_showroom: float) -> int:
    """
    Return life tax in rupees for state/fuel/ex-showroom.
    fuel: petrol | diesel | cng | ev | strong_hybrid (strong_hybrid uses petrol rate).
    """
    x = ex_showroom
    key = "p" if fuel == "strong_hybrid" else fuel[0] if fuel != "ev" else "e"
    table = STATE_TAX_TABLE.get(state_code) or STATE_TAX_TABLE["MH"]
    fn = table.get(key) or table["p"]
    raw = fn(x)
    return int(round(raw)) if raw > 1 else int(round(x * raw))


# Each state: { "name", "note", "p", "d", "c", "e" } — values are callables (x) -> tax amount
def _dl_p(x): return x * 0.10 if x >= 6e5 else x * 0.07 if x >= 1e6 else x * 0.04
def _ga_p(x): return (x * 0.12 + 20000) if x > 1e6 else (x * 0.11 if x >= 6e5 else x * 0.09)
def _uk_p(x): return (x * 0.10 if x >= 1e6 else x * 0.09 if x >= 5e5 else x * 0.08) + 1500
def _uk_d(x): return (x * 0.10 if x >= 1e6 else x * 0.09 if x >= 5e5 else x * 0.08) + 3000

STATE_TAX_TABLE = {
    "AN": {"name": STATE_NAMES["AN"], "note": "UT · Low flat ~6% · EV exempt", "p": lambda x: x * 0.06, "d": lambda x: x * 0.06, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "AP": {"name": STATE_NAMES["AP"], "note": "EV exempt · Petrol 14.3–19.8%", "p": lambda x: x * (0.198 if x >= 2e6 else 0.187 if x >= 1e6 else 0.154 if x >= 5e5 else 0.143), "d": lambda x: x * (0.198 if x >= 2e6 else 0.187 if x >= 1e6 else 0.154 if x >= 5e5 else 0.143), "c": lambda x: x * 0.143, "e": lambda x: 0},
    "AR": {"name": STATE_NAMES["AR"], "note": "Flat ~4% · EV exempt", "p": lambda x: x * 0.04, "d": lambda x: x * 0.04, "c": lambda x: x * 0.04, "e": lambda x: 0},
    "AS": {"name": STATE_NAMES["AS"], "note": "Petrol 5–12% · EV ~3%", "p": lambda x: x * (0.12 if x >= 2e6 else 0.09 if x >= 15e5 else 0.07 if x >= 12e5 else 0.06 if x >= 6e5 else 0.05), "d": lambda x: x * 0.12, "c": lambda x: x * 0.07, "e": lambda x: x * 0.03},
    "BR": {"name": STATE_NAMES["BR"], "note": "9–12% · EV ~5%", "p": lambda x: x * (0.12 if x >= 15e5 else 0.10 if x >= 8e5 else 0.09), "d": lambda x: x * 0.12, "c": lambda x: x * 0.10, "e": lambda x: x * 0.05},
    "CH": {"name": STATE_NAMES["CH"], "note": "EV 0% · Petrol 10–12%", "p": lambda x: x * (0.12 if x >= 15e5 else 0.10), "d": lambda x: x * 0.12, "c": lambda x: x * 0.10, "e": lambda x: 0},
    "CG": {"name": STATE_NAMES["CG"], "note": "8–9% · EV ~3%", "p": lambda x: x * (0.09 if x >= 5e5 else 0.08), "d": lambda x: x * 0.09, "c": lambda x: x * 0.08, "e": lambda x: x * 0.03},
    "DN": {"name": STATE_NAMES["DN"], "note": "UT · 4–6% · EV exempt", "p": lambda x: x * 0.05, "d": lambda x: x * 0.06, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "DL": {"name": STATE_NAMES["DL"], "note": "EV 0% · Petrol 4–10%", "p": _dl_p, "d": lambda x: x * (0.125 if x >= 1e6 else 0.0875 if x >= 6e5 else 0.05), "c": lambda x: x * 0.04, "e": lambda x: 0},
    "GA": {"name": STATE_NAMES["GA"], "note": "Infra cess ₹20K >₹10L · EV ~3%", "p": _ga_p, "d": _ga_p, "c": lambda x: x * (0.11 if x >= 1e6 else 0.09), "e": lambda x: x * 0.03},
    "GJ": {"name": STATE_NAMES["GJ"], "note": "Flat 6% · EV exempt", "p": lambda x: x * 0.06, "d": lambda x: x * 0.06, "c": lambda x: x * 0.06, "e": lambda x: 0},
    "HR": {"name": STATE_NAMES["HR"], "note": "EV 0% · Petrol 5–10%", "p": lambda x: x * (0.10 if x >= 2e6 else 0.08 if x >= 6e5 else 0.05), "d": lambda x: x * (0.11 if x >= 2e6 else 0.09), "c": lambda x: x * 0.08, "e": lambda x: 0},
    "HP": {"name": STATE_NAMES["HP"], "note": "~6–7% · EV 0%", "p": lambda x: x * (0.07 if x >= 15e5 else 0.06), "d": lambda x: x * 0.07, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "JK": {"name": STATE_NAMES["JK"], "note": "Flat 9% · EV ~4%", "p": lambda x: x * 0.09, "d": lambda x: x * 0.09, "c": lambda x: x * 0.07, "e": lambda x: x * 0.04},
    "JH": {"name": STATE_NAMES["JH"], "note": "7–9% · EV ~3%", "p": lambda x: x * (0.09 if x >= 7e5 else 0.07), "d": lambda x: x * 0.09, "c": lambda x: x * 0.07, "e": lambda x: x * 0.03},
    "KA": {"name": STATE_NAMES["KA"], "note": "HIGH · Petrol 14.4–20% · EV ~0%", "p": lambda x: x * (0.1998 if x >= 2e6 else 0.1887 if x >= 1e6 else 0.1554 if x >= 5e5 else 0.1443), "d": lambda x: x * (0.2109 if x >= 2e6 else 0.1998), "c": lambda x: x * 0.1554, "e": lambda x: 0},
    "KL": {"name": STATE_NAMES["KL"], "note": "10–22% · EV 5%", "p": lambda x: x * (0.22 if x >= 2e6 else 0.17 if x >= 15e5 else 0.15 if x >= 1e6 else 0.13 if x >= 5e5 else 0.10), "d": lambda x: x * 0.17, "c": lambda x: x * 0.13, "e": lambda x: x * 0.05},
    "LA": {"name": STATE_NAMES["LA"], "note": "~9% · EV 0%", "p": lambda x: x * 0.09, "d": lambda x: x * 0.09, "c": lambda x: x * 0.07, "e": lambda x: 0},
    "LD": {"name": STATE_NAMES["LD"], "note": "~4% · EV exempt", "p": lambda x: x * 0.04, "d": lambda x: x * 0.04, "c": lambda x: x * 0.04, "e": lambda x: 0},
    "MP": {"name": STATE_NAMES["MP"], "note": "EV 2% · Petrol 8–14%", "p": lambda x: x * (0.14 if x >= 2e6 else 0.10 if x >= 1e6 else 0.08), "d": lambda x: x * (0.16 if x >= 2e6 else 0.12), "c": lambda x: x * 0.10, "e": lambda x: x * 0.02},
    "MH": {"name": STATE_NAMES["MH"], "note": "EV 4% · Petrol 11–13%", "p": lambda x: x * (0.13 if x >= 2e6 else 0.12 if x >= 1e6 else 0.11), "d": lambda x: x * (0.15 if x >= 2e6 else 0.14 if x >= 1e6 else 0.13), "c": lambda x: x * 0.08, "e": lambda x: x * 0.04},
    "MN": {"name": STATE_NAMES["MN"], "note": "NE · Low ~5–6%", "p": lambda x: x * (0.06 if x >= 1e6 else 0.05), "d": lambda x: x * 0.06, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "ML": {"name": STATE_NAMES["ML"], "note": "NE · Low ~5–7%", "p": lambda x: x * (0.07 if x >= 1e6 else 0.05), "d": lambda x: x * 0.07, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "MZ": {"name": STATE_NAMES["MZ"], "note": "NE · Low ~5–6%", "p": lambda x: x * (0.06 if x >= 1e6 else 0.05), "d": lambda x: x * 0.06, "c": lambda x: x * 0.04, "e": lambda x: 0},
    "NL": {"name": STATE_NAMES["NL"], "note": "NE · ~5%", "p": lambda x: x * 0.05, "d": lambda x: x * 0.05, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "OD": {"name": STATE_NAMES["OD"], "note": "6–10% · EV exempt", "p": lambda x: x * (0.10 if x >= 1e6 else 0.08 if x >= 5e5 else 0.06), "d": lambda x: x * 0.10, "c": lambda x: x * 0.08, "e": lambda x: 0},
    "PY": {"name": STATE_NAMES["PY"], "note": "UT · 6–7% · EV exempt", "p": lambda x: x * (0.07 if x >= 1e6 else 0.06), "d": lambda x: x * 0.07, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "PB": {"name": STATE_NAMES["PB"], "note": "EV exempt · Petrol 10–12%", "p": lambda x: x * (0.12 if x >= 15e5 else 0.10), "d": lambda x: x * 0.12, "c": lambda x: x * 0.10, "e": lambda x: 0},
    "RJ": {"name": STATE_NAMES["RJ"], "note": "10–13.5% · EV exempt", "p": lambda x: x * (0.135 if x >= 15e5 else 0.1125 if x >= 8e5 else 0.1012), "d": lambda x: x * (0.1575 if x >= 15e5 else 0.135), "c": lambda x: x * 0.1125, "e": lambda x: 0},
    "SK": {"name": STATE_NAMES["SK"], "note": "NE · ~4–5%", "p": lambda x: x * (0.05 if x >= 1e6 else 0.04), "d": lambda x: x * 0.05, "c": lambda x: x * 0.04, "e": lambda x: 0},
    "TN": {"name": STATE_NAMES["TN"], "note": "Petrol 12–20% · EV 0–2%", "p": lambda x: x * (0.20 if x >= 2e6 else 0.18 if x >= 1e6 else 0.13 if x >= 5e5 else 0.12), "d": lambda x: x * 0.20, "c": lambda x: x * 0.13, "e": lambda x: x * (0.02 if x >= 1e6 else 0)},
    "TS": {"name": STATE_NAMES["TS"], "note": "EV exempt · Petrol 13–18%", "p": lambda x: x * (0.18 if x >= 2e6 else 0.17 if x >= 1e6 else 0.14 if x >= 5e5 else 0.13), "d": lambda x: x * 0.18, "c": lambda x: x * 0.14, "e": lambda x: 0},
    "TR": {"name": STATE_NAMES["TR"], "note": "NE · ~5–6%", "p": lambda x: x * (0.06 if x >= 1e6 else 0.05), "d": lambda x: x * 0.06, "c": lambda x: x * 0.05, "e": lambda x: 0},
    "UP": {"name": STATE_NAMES["UP"], "note": "9–11% · EV exempt", "p": lambda x: x * (0.11 if x >= 1e6 else 0.09), "d": lambda x: x * 0.11, "c": lambda x: x * 0.09, "e": lambda x: 0},
    "UK": {"name": STATE_NAMES["UK"], "note": "Green tax ₹1500/3000 · EV ~3%", "p": _uk_p, "d": _uk_d, "c": lambda x: (x * 0.10 if x >= 1e6 else x * 0.09), "e": lambda x: x * 0.03},
    "WB": {"name": STATE_NAMES["WB"], "note": "10% · EV ~3%", "p": lambda x: x * 0.10, "d": lambda x: x * 0.10, "c": lambda x: x * 0.10, "e": lambda x: x * 0.03},
}

# Cess info for states that levy cess on top of life tax (from original HTML cessInfo)
CESS_INFO = {
    "AP": {
        "cessName": "Road Development Cess",
        "cessRate": 0.01,
        "basis": "ex-showroom",
        "effective": "2020-04-01",
        "source": "AP Motor Vehicles Taxation Act",
    },
    "KA": {
        "cessName": "Infrastructure Cess",
        "cessRate": 0.0111,
        "basis": "ex-showroom",
        "effective": "2023-04-01",
        "source": "Karnataka Motor Vehicles Taxation Act, 2023 amendment",
    },
    "RJ": {
        "cessName": "Green Cess",
        "cessRate": 0.0225,
        "basis": "ex-showroom",
        "effective": "2022-04-01",
        "source": "Rajasthan Motor Vehicles Tax Rules, 2022 notification",
    },
    "UK": {
        "cessName": "Green Tax / Environment Cess",
        "cessRate": 0.0,
        "basis": "flat",
        "effective": "2021-04-01",
        "source": "Uttarakhand MVT Rules — ₹1500 petrol/CNG, ₹3000 diesel (included in base tax fn)",
    },
    "GA": {
        "cessName": "Infrastructure Cess",
        "cessRate": 0.0,
        "basis": "flat",
        "effective": "2022-01-01",
        "source": "Goa RTO — ₹20,000 on vehicles >₹10L (included in base tax fn)",
    },
}


def get_cess_breakdown(state_code: str, fuel: str, ex: float) -> dict | None:
    """Return cess breakdown for states that levy cess. None if no cess."""
    code = state_code.upper()
    if code not in CESS_INFO:
        return None
    info = CESS_INFO[code]
    if fuel == "ev" and code in ("KA", "RJ"):
        return None

    base_tax = get_tax(code, fuel, ex)
    if info["cessRate"] > 0:
        cess_amt = round(ex * info["cessRate"])
    else:
        cess_amt = 0

    base_rate_pct = round(base_tax / ex * 100, 2) if ex > 0 else 0
    total_tax = base_tax + cess_amt

    return {
        "hasCess": True,
        "cessName": info["cessName"],
        "cessRate": info["cessRate"],
        "cessRatePct": round(info["cessRate"] * 100, 2),
        "baseTaxAmt": base_tax,
        "baseTaxRatePct": base_rate_pct,
        "cessAmt": cess_amt,
        "totalTaxAmt": total_tax,
        "effective": info["effective"],
        "source": info["source"],
        "basis": info["basis"],
    }


def get_tax_rate_pct(state_code: str, fuel: str, ex: float) -> float:
    """Return effective tax rate as % of ex-showroom."""
    if ex <= 0:
        return 0
    return round(get_tax(state_code, fuel, ex) / ex * 100, 2)
