"""
State tax and fuel data — all 36 states & UTs.
Tax functions return ABSOLUTE rupee amount (not rate).
All rates INCLUDE cess/surcharge baked in (matching legacy calculator).
Keys: p=petrol, d=diesel, c=cng, e=ev
"""

STATE_CODES = [
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DN", "DL", "GA", "GJ", "HR", "HP",
    "JK", "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OD",
    "PY", "PB", "RJ", "SK", "TN", "TS", "TR", "UP", "UK", "WB",
]

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


def get_tax(state_code: str, fuel: str, ex_showroom: float) -> int:
    """
    Return life tax in rupees for state/fuel/ex-showroom.
    fuel: petrol | diesel | cng | ev | strong_hybrid
    """
    x = ex_showroom
    key = "p" if fuel == "strong_hybrid" else fuel[0] if fuel != "ev" else "e"
    table = STATE_TAX_TABLE.get(state_code) or STATE_TAX_TABLE["MH"]
    fn = table.get(key) or table["p"]
    raw = fn(x)
    return int(round(raw))


# ══════════════════════════════════════════════════════════════════
# STATE_TAX_TABLE — Ported 1:1 from legacy/index.html STATE_TAX
# All functions return ABSOLUTE ₹ tax amount.
# Rates INCLUDE cess/surcharge where applicable (AP, KA, RJ).
# ══════════════════════════════════════════════════════════════════

def _ga_pd(x):
    b = (0.09 if x < 6e5 else 0.11 if x < 1e6 else 0.12) * x
    return b + 20000 if x > 1e6 else b


STATE_TAX_TABLE = {
    "AN": {
        "name": STATE_NAMES["AN"],
        "note": "UT · Low flat rate · ~6% · EV exempt",
        "p": lambda x: x * 0.06, "d": lambda x: x * 0.06,
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "AP": {
        "name": STATE_NAMES["AP"],
        "note": "EV 100% exempt (till Jun 2026) · Petrol/Diesel 14.3–19.8% (incl. 10% Road Safety Cess)",
        "p": lambda x: x * (0.143 if x < 5e5 else 0.154 if x < 1e6 else 0.187 if x < 2e6 else 0.198),
        "d": lambda x: x * (0.143 if x < 5e5 else 0.154 if x < 1e6 else 0.187 if x < 2e6 else 0.198),
        "c": lambda x: x * (0.143 if x < 5e5 else 0.154 if x < 1e6 else 0.187 if x < 2e6 else 0.198),
        "e": lambda x: 0,
    },
    "AR": {
        "name": STATE_NAMES["AR"],
        "note": "Cheapest in India · Flat ~4% · EV exempt",
        "p": lambda x: x * 0.04, "d": lambda x: x * 0.04,
        "c": lambda x: x * 0.04, "e": lambda x: 0,
    },
    "AS": {
        "name": STATE_NAMES["AS"],
        "note": "Petrol 5-12% by price slab · EV ~3%",
        "p": lambda x: x * (0.05 if x < 4e5 else 0.06 if x < 6e5 else 0.07 if x < 12e5 else 0.075 if x < 15e5 else 0.09 if x < 2e6 else 0.12),
        "d": lambda x: x * (0.05 if x < 4e5 else 0.06 if x < 6e5 else 0.07 if x < 12e5 else 0.075 if x < 15e5 else 0.09 if x < 2e6 else 0.12),
        "c": lambda x: x * (0.05 if x < 4e5 else 0.06 if x < 6e5 else 0.07 if x < 12e5 else 0.075 if x < 15e5 else 0.09 if x < 2e6 else 0.12),
        "e": lambda x: x * 0.03,
    },
    "BR": {
        "name": STATE_NAMES["BR"],
        "note": "Petrol/Diesel 9-12% by slab · EV ~5%",
        "p": lambda x: x * (0.09 if x < 8e5 else 0.10 if x < 15e5 else 0.12),
        "d": lambda x: x * (0.09 if x < 8e5 else 0.10 if x < 15e5 else 0.12),
        "c": lambda x: x * (0.09 if x < 8e5 else 0.10 if x < 15e5 else 0.12),
        "e": lambda x: x * 0.05,
    },
    "CH": {
        "name": STATE_NAMES["CH"],
        "note": "EV & hybrid 0% (till Mar 2027) · Petrol 10-12% on pre-GST price",
        "p": lambda x: x * (0.10 if x < 15e5 else 0.12),
        "d": lambda x: x * (0.10 if x < 15e5 else 0.12),
        "c": lambda x: x * (0.10 if x < 15e5 else 0.12),
        "e": lambda x: 0,
    },
    "CG": {
        "name": STATE_NAMES["CG"],
        "note": "Petrol/Diesel 8-9% · EV ~3%",
        "p": lambda x: x * (0.08 if x < 5e5 else 0.09),
        "d": lambda x: x * (0.08 if x < 5e5 else 0.09),
        "c": lambda x: x * (0.08 if x < 5e5 else 0.09),
        "e": lambda x: x * 0.03,
    },
    "DN": {
        "name": STATE_NAMES["DN"],
        "note": "UT · Low 4-6% · EV exempt",
        "p": lambda x: x * 0.05, "d": lambda x: x * 0.06,
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "DL": {
        "name": STATE_NAMES["DL"],
        "note": "EV 0% fully exempt · Petrol 4-10% · Diesel 5-12.5%",
        "p": lambda x: x * (0.04 if x < 6e5 else 0.07 if x < 1e6 else 0.10),
        "d": lambda x: x * (0.05 if x < 6e5 else 0.0875 if x < 1e6 else 0.125),
        "c": lambda x: x * 0.04,
        "e": lambda x: 0,
    },
    "GA": {
        "name": STATE_NAMES["GA"],
        "note": "Petrol 9-12% · Infra cess ₹20K for cars >₹10L · EV ~3%",
        "p": _ga_pd, "d": _ga_pd,
        "c": lambda x: (0.09 if x < 6e5 else 0.11 if x < 1e6 else 0.12) * x,
        "e": lambda x: x * 0.03,
    },
    "GJ": {
        "name": STATE_NAMES["GJ"],
        "note": "Flat 6% on factory price · Company 12% · EV exempt",
        "p": lambda x: x * 0.06, "d": lambda x: x * 0.06,
        "c": lambda x: x * 0.06, "e": lambda x: 0,
    },
    "HR": {
        "name": STATE_NAMES["HR"],
        "note": "EV 0% (from Feb 2026) · Petrol 5-10% · CNG gets 20% rebate",
        "p": lambda x: x * (0.05 if x < 6e5 else 0.08 if x < 2e6 else 0.10),
        "d": lambda x: x * (0.065 if x < 6e5 else 0.09 if x < 2e6 else 0.11),
        "c": lambda x: x * (0.04 if x < 6e5 else 0.064 if x < 2e6 else 0.08),
        "e": lambda x: 0,
    },
    "HP": {
        "name": STATE_NAMES["HP"],
        "note": "Lowest state · ~6-7% by price slab · EV 0%",
        "p": lambda x: x * (0.06 if x < 15e5 else 0.07),
        "d": lambda x: x * (0.06 if x < 15e5 else 0.07),
        "c": lambda x: x * 0.05,
        "e": lambda x: 0,
    },
    "JK": {
        "name": STATE_NAMES["JK"],
        "note": "Flat 9% · EV ~4%",
        "p": lambda x: x * 0.09, "d": lambda x: x * 0.09,
        "c": lambda x: x * 0.07, "e": lambda x: x * 0.04,
    },
    "JH": {
        "name": STATE_NAMES["JH"],
        "note": "7-9% on pre-GST price · +3% for 2nd car · EV ~3%",
        "p": lambda x: x * (0.07 if x < 7e5 else 0.09),
        "d": lambda x: x * (0.07 if x < 7e5 else 0.09),
        "c": lambda x: x * (0.07 if x < 7e5 else 0.09),
        "e": lambda x: x * 0.03,
    },
    "KA": {
        "name": STATE_NAMES["KA"],
        "note": "HIGHEST IN INDIA · Petrol 14.4-20% incl. cess · EV ~0%",
        "p": lambda x: x * (0.1443 if x < 5e5 else 0.1554 if x < 1e6 else 0.1887 if x < 2e6 else 0.1998),
        "d": lambda x: x * (0.1554 if x < 5e5 else 0.1665 if x < 1e6 else 0.1998 if x < 2e6 else 0.2109),
        "c": lambda x: x * (0.1443 if x < 5e5 else 0.1554 if x < 1e6 else 0.1887 if x < 2e6 else 0.1998),
        "e": lambda x: 0,
    },
    "KL": {
        "name": STATE_NAMES["KL"],
        "note": "EV flat 5% · Petrol 10-22% by slab · High on luxury",
        "p": lambda x: x * (0.10 if x < 5e5 else 0.13 if x < 1e6 else 0.15 if x < 15e5 else 0.17 if x < 2e6 else 0.22),
        "d": lambda x: x * (0.10 if x < 5e5 else 0.13 if x < 1e6 else 0.15 if x < 15e5 else 0.17 if x < 2e6 else 0.22),
        "c": lambda x: x * (0.10 if x < 5e5 else 0.13 if x < 1e6 else 0.15 if x < 15e5 else 0.17 if x < 2e6 else 0.22),
        "e": lambda x: x * 0.05,
    },
    "LA": {
        "name": STATE_NAMES["LA"],
        "note": "UT · ~9% (J&K structure) · EV 0%",
        "p": lambda x: x * 0.09, "d": lambda x: x * 0.09,
        "c": lambda x: x * 0.07, "e": lambda x: 0,
    },
    "LD": {
        "name": STATE_NAMES["LD"],
        "note": "UT · Very low ~4% · EV exempt",
        "p": lambda x: x * 0.04, "d": lambda x: x * 0.04,
        "c": lambda x: x * 0.04, "e": lambda x: 0,
    },
    "MP": {
        "name": STATE_NAMES["MP"],
        "note": "EV 2% (Mar 2026) · Petrol 8-14% · Diesel 10-16%",
        "p": lambda x: x * (0.08 if x < 1e6 else 0.10 if x < 2e6 else 0.14),
        "d": lambda x: x * (0.10 if x < 1e6 else 0.12 if x < 2e6 else 0.16),
        "c": lambda x: x * (0.08 if x < 1e6 else 0.10 if x < 2e6 else 0.14),
        "e": lambda x: x * 0.02,
    },
    "MH": {
        "name": STATE_NAMES["MH"],
        "note": "EV 4% (till Jun 2026, then 1%) · Petrol 11-13%",
        "p": lambda x: x * (0.11 if x < 1e6 else 0.12 if x < 2e6 else 0.13),
        "d": lambda x: x * (0.13 if x < 1e6 else 0.14 if x < 2e6 else 0.15),
        "c": lambda x: x * 0.08,
        "e": lambda x: x * 0.04,
    },
    "MN": {
        "name": STATE_NAMES["MN"],
        "note": "NE state · Low ~5-6% · EV exempt",
        "p": lambda x: x * (0.05 if x < 1e6 else 0.06),
        "d": lambda x: x * (0.05 if x < 1e6 else 0.06),
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "ML": {
        "name": STATE_NAMES["ML"],
        "note": "NE state · Low ~5-7% · EV exempt",
        "p": lambda x: x * (0.05 if x < 1e6 else 0.07),
        "d": lambda x: x * (0.05 if x < 1e6 else 0.07),
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "MZ": {
        "name": STATE_NAMES["MZ"],
        "note": "NE state · Low ~5-6% · EV exempt",
        "p": lambda x: x * (0.05 if x < 1e6 else 0.06),
        "d": lambda x: x * (0.05 if x < 1e6 else 0.06),
        "c": lambda x: x * 0.04, "e": lambda x: 0,
    },
    "NL": {
        "name": STATE_NAMES["NL"],
        "note": "NE state · Low ~5% · EV exempt",
        "p": lambda x: x * 0.05, "d": lambda x: x * 0.05,
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "OD": {
        "name": STATE_NAMES["OD"],
        "note": "Petrol 6-10% · EV exempt",
        "p": lambda x: x * (0.06 if x < 5e5 else 0.08 if x < 1e6 else 0.10),
        "d": lambda x: x * (0.06 if x < 5e5 else 0.08 if x < 1e6 else 0.10),
        "c": lambda x: x * (0.06 if x < 5e5 else 0.08 if x < 1e6 else 0.10),
        "e": lambda x: 0,
    },
    "PY": {
        "name": STATE_NAMES["PY"],
        "note": "UT · Fixed-slab tax 6-7% · EV exempt · Very low",
        "p": lambda x: x * (0.06 if x < 1e6 else 0.07),
        "d": lambda x: x * (0.06 if x < 1e6 else 0.07),
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "PB": {
        "name": STATE_NAMES["PB"],
        "note": "EV & hybrid 100% exempt (till Dec 2026) · Petrol 10-12% on pre-GST",
        "p": lambda x: x * (0.10 if x < 15e5 else 0.12),
        "d": lambda x: x * (0.10 if x < 15e5 else 0.12),
        "c": lambda x: x * (0.10 if x < 15e5 else 0.12),
        "e": lambda x: 0,
    },
    "RJ": {
        "name": STATE_NAMES["RJ"],
        "note": "Petrol 10-13.5% incl. 12.5% surcharge · EV exempt (till Mar 2027)",
        "p": lambda x: x * (0.1012 if x < 8e5 else 0.1125 if x < 15e5 else 0.135),
        "d": lambda x: x * (0.1237 if x < 8e5 else 0.1350 if x < 15e5 else 0.1575),
        "c": lambda x: x * (0.0900 if x < 8e5 else 0.1012 if x < 15e5 else 0.1237),
        "e": lambda x: 0,
    },
    "SK": {
        "name": STATE_NAMES["SK"],
        "note": "NE state · Low ~4-5% · EV exempt",
        "p": lambda x: x * (0.04 if x < 1e6 else 0.05),
        "d": lambda x: x * (0.04 if x < 1e6 else 0.05),
        "c": lambda x: x * 0.04, "e": lambda x: 0,
    },
    "TN": {
        "name": STATE_NAMES["TN"],
        "note": "Hiked Nov 2023 · Petrol 12-20% · EV 0-2%",
        "p": lambda x: x * (0.12 if x < 5e5 else 0.13 if x < 1e6 else 0.18 if x < 2e6 else 0.20),
        "d": lambda x: x * (0.12 if x < 5e5 else 0.13 if x < 1e6 else 0.18 if x < 2e6 else 0.20),
        "c": lambda x: x * (0.12 if x < 5e5 else 0.13 if x < 1e6 else 0.18 if x < 2e6 else 0.20),
        "e": lambda x: x * (0 if x < 1e6 else 0.02),
    },
    "TS": {
        "name": STATE_NAMES["TS"],
        "note": "EV 100% exempt (till Jun 2026) · Petrol/Diesel 13-18%",
        "p": lambda x: x * (0.13 if x < 5e5 else 0.14 if x < 1e6 else 0.17 if x < 2e6 else 0.18),
        "d": lambda x: x * (0.13 if x < 5e5 else 0.14 if x < 1e6 else 0.17 if x < 2e6 else 0.18),
        "c": lambda x: x * (0.13 if x < 5e5 else 0.14 if x < 1e6 else 0.17 if x < 2e6 else 0.18),
        "e": lambda x: 0,
    },
    "TR": {
        "name": STATE_NAMES["TR"],
        "note": "NE state · Low ~5-6% · EV exempt",
        "p": lambda x: x * (0.05 if x < 1e6 else 0.06),
        "d": lambda x: x * (0.05 if x < 1e6 else 0.06),
        "c": lambda x: x * 0.05, "e": lambda x: 0,
    },
    "UP": {
        "name": STATE_NAMES["UP"],
        "note": "Petrol 9-11% · EV exempt till Oct 2026, then 5%",
        "p": lambda x: x * (0.09 if x < 1e6 else 0.11),
        "d": lambda x: x * (0.09 if x < 1e6 else 0.11),
        "c": lambda x: x * (0.09 if x < 1e6 else 0.11),
        "e": lambda x: 0,
    },
    "UK": {
        "name": STATE_NAMES["UK"],
        "note": "Petrol 8-10% + ₹1500 green tax · Diesel +₹3000 green tax · EV ~3%",
        "p": lambda x: (0.08 if x < 5e5 else 0.09 if x < 1e6 else 0.10) * x + 1500,
        "d": lambda x: (0.08 if x < 5e5 else 0.09 if x < 1e6 else 0.10) * x + 3000,
        "c": lambda x: (0.08 if x < 5e5 else 0.09 if x < 1e6 else 0.10) * x,
        "e": lambda x: x * 0.03,
    },
    "WB": {
        "name": STATE_NAMES["WB"],
        "note": "Petrol/Diesel 10% lifetime · CC-based min floors · EV ~3%",
        "p": lambda x: x * 0.10, "d": lambda x: x * 0.10,
        "c": lambda x: x * 0.10, "e": lambda x: x * 0.03,
    },
}


# ══════════════════════════════════════════════════════════════════
# CESS_INFO — Cess / surcharge breakdown for UI display.
# All STATE_TAX rates already INCLUDE cess (baked-in effective).
# This object drives the cess breakdown panel only.
# ══════════════════════════════════════════════════════════════════

CESS_INFO = {
    "AP": {
        "cessName": "Road Safety Cess",
        "cessRate": 10,
        "basis": "on computed life tax",
        "baseCalc": lambda x: 0.13 if x < 5e5 else 0.14 if x < 1e6 else 0.17 if x < 2e6 else 0.18,
        "effective": "Jan 2026",
        "source": "AP Cabinet Dec 2025 · Times of India",
    },
    "KA": {
        "cessName": "Road Tax Cess + Infra Cess",
        "cessRate": 11,
        "basis": "on computed road tax",
        "baseCalc": lambda x: 0.13 if x < 5e5 else 0.14 if x < 1e6 else 0.17 if x < 2e6 else 0.18,
        "effective": "2023",
        "source": "Karnataka Budget",
    },
    "RJ": {
        "cessName": "Road Tax Surcharge",
        "cessRate": 12.5,
        "basis": "on computed road tax",
        "baseCalc": lambda x: 0.09 if x < 8e5 else 0.1125 if x < 15e5 else 0.135,
        "effective": "2024",
        "source": "Rajasthan RTO",
    },
    "UK": {
        "cessName": "Green Tax (Flat)",
        "cessRate": 0,
        "basis": "flat per vehicle at RTO",
        "flatP": 1750,
        "flatD": 3500,
        "effective": "Mar 2026",
        "source": "Uttarakhand RTO",
    },
    "GA": {
        "cessName": "Infrastructure Cess (Flat)",
        "cessRate": 0,
        "basis": "₹20,000 flat for cars above ₹10L",
        "flatAbove": 20000,
        "priceThreshold": 1e6,
        "effective": "2025",
        "source": "Goa Budget",
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

    if info["cessRate"] > 0 and "baseCalc" in info:
        base_rate = info["baseCalc"](ex)
        base_tax_before_cess = round(ex * base_rate)
        cess_amt = round(base_tax_before_cess * info["cessRate"] / 100)
        base_rate_pct = round(base_rate * 100, 2)
        return {
            "hasCess": True,
            "cessName": info["cessName"],
            "cessRate": info["cessRate"],
            "cessRatePct": info["cessRate"],
            "basis": info["basis"],
            "baseTaxAmt": base_tax_before_cess,
            "baseTaxRatePct": base_rate_pct,
            "cessAmt": cess_amt,
            "totalTaxAmt": base_tax_before_cess + cess_amt,
            "effective": info["effective"],
            "source": info["source"],
        }

    if "flatP" in info or "flatD" in info:
        flat_amt = info.get("flatD", 0) if fuel == "diesel" else (0 if fuel == "ev" else info.get("flatP", 0))
        return {
            "hasCess": True,
            "cessName": info["cessName"],
            "cessRate": 0,
            "cessRatePct": 0,
            "basis": info["basis"],
            "cessType": "flat",
            "flatAmt": flat_amt,
            "baseTaxAmt": base_tax - flat_amt,
            "baseTaxRatePct": round((base_tax - flat_amt) / ex * 100, 2) if ex > 0 else 0,
            "cessAmt": flat_amt,
            "totalTaxAmt": base_tax,
            "effective": info["effective"],
            "source": info["source"],
        }

    if "flatAbove" in info:
        applies = ex > info.get("priceThreshold", 1e6)
        flat_amt = info["flatAbove"] if applies else 0
        return {
            "hasCess": True,
            "cessName": info["cessName"],
            "cessRate": 0,
            "cessRatePct": 0,
            "basis": info["basis"],
            "cessType": "flatAbove",
            "flatAmt": flat_amt,
            "applies": applies,
            "priceThreshold": info.get("priceThreshold", 1e6),
            "baseTaxAmt": base_tax - flat_amt,
            "baseTaxRatePct": round((base_tax - flat_amt) / ex * 100, 2) if ex > 0 else 0,
            "cessAmt": flat_amt,
            "totalTaxAmt": base_tax,
            "effective": info["effective"],
            "source": info["source"],
        }

    return None


def get_tax_rate_pct(state_code: str, fuel: str, ex: float) -> float:
    """Return effective tax rate as % of ex-showroom."""
    if ex <= 0:
        return 0
    return round(get_tax(state_code, fuel, ex) / ex * 100, 2)
