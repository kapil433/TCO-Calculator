"""
TCO API — reference data + calculate endpoint.
"""

import os
from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel, Field

from app.data.states import (
    STATE_CODES, STATE_NAMES, STATE_TAX_TABLE,
    get_tax, get_tax_rate_pct, get_cess_breakdown,
)
from app.data.fuel_prices import FUEL_PRICES, get_fuel_prices_live, get_fuel_price_status
from app.data.car_db import get_brands, get_models, get_model_info
from app.services.tco_service import calc_vehicle
from app.util.constants import IDV_D, TP, PA_COVER, INS_GST, NCB, get_od_rate, MAINT

router = APIRouter(prefix="/tco", tags=["tco"])


# ─── Reference data ─────────────────────────────────────────────────────

@router.get("/states")
def list_states(response: Response):
    """List state codes and names for dropdown."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    return [
        {"code": c, "name": STATE_NAMES.get(c, c)}
        for c in STATE_CODES
    ]


@router.get("/states/{state_code}")
def state_info(state_code: str):
    """State metadata and tax note."""
    s = STATE_TAX_TABLE.get(state_code.upper())
    if not s:
        raise HTTPException(404, "State not found")
    return {"code": state_code.upper(), "name": s["name"], "note": s.get("note", "")}


@router.get("/fuel-prices")
def fuel_prices_all(response: Response):
    """All state fuel prices (Jan 2026 baseline)."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    return FUEL_PRICES


@router.get("/fuel-prices/live/meta")
def fuel_prices_live_meta():
    """Full status: source, last_updated, age_hours, is_stale, next_refresh_hint."""
    return get_fuel_price_status()


@router.get("/fuel-prices/{state_code}")
def fuel_prices_state(state_code: str):
    """Fuel prices for one state. Uses scraped data from mypetrolprice.com when available."""
    code = state_code.upper()
    prices, _ = get_fuel_prices_live()
    return prices.get(code, prices.get("MH", {}))


@router.post("/fuel-prices/refresh")
def fuel_prices_refresh(x_refresh_key: str | None = Header(None)):
    """Manually trigger a fuel price scrape. Requires X-Refresh-Key header."""
    expected = os.environ.get("REFRESH_KEY", "")
    if not expected or x_refresh_key != expected:
        raise HTTPException(403, "Forbidden — invalid or missing X-Refresh-Key")
    try:
        from scripts.scrape_fuel_prices import run_scrape
        result = run_scrape(force=True)
        return result
    except Exception as e:
        raise HTTPException(500, f"Scrape failed: {e}")


@router.get("/tax")
def tax_preview(state: str, fuel: str, ex: float):
    """Preview life tax (₹) for state + fuel + ex-showroom. Returns amount, rate %, and note."""
    code = state.upper()
    tax_amt = get_tax(code, fuel, ex)
    rate_pct = get_tax_rate_pct(code, fuel, ex)
    table = STATE_TAX_TABLE.get(code, {})
    note = table.get("note", "")
    return {"tax": tax_amt, "rate_pct": rate_pct, "state_note": note}


@router.get("/cess")
def cess_breakdown(state: str, fuel: str, ex: float):
    """Cess breakdown for states that levy cess (AP, KA, RJ, UK, GA)."""
    result = get_cess_breakdown(state.upper(), fuel, ex)
    if result is None:
        return {"hasCess": False}
    return result


@router.get("/insurance-preview")
def insurance_preview(
    ex: float,
    eng: str = "mid",
    fuel: str = "petrol",
    num_years: int = 5,
    ncb_mode: str = "max",
):
    """Year-wise insurance premium breakdown using IRDAI formula."""
    if ex <= 0:
        raise HTTPException(400, "ex-showroom must be > 0")
    num_years = min(max(1, num_years), 15)
    tp_base = TP.get(eng, TP["mid"])
    if fuel == "ev":
        tp_base = round(tp_base * 0.85)

    year_wise = []
    total = 0
    for yr in range(num_years):
        dep = IDV_D[min(yr, len(IDV_D) - 1)]
        idv = ex * (1 - dep)
        ncb_rate = 0.20 if ncb_mode == "avg" and (yr % 3) == 2 else NCB[min(yr, len(NCB) - 1)]
        od_rate = get_od_rate(idv)
        od_premium = round(idv * od_rate)
        ncb_discount = round(od_premium * ncb_rate)
        od_after_ncb = od_premium - ncb_discount
        tp_premium = tp_base
        pa = PA_COVER
        subtotal = od_after_ncb + tp_premium + pa
        gst = round(subtotal * INS_GST)
        total_premium = subtotal + gst
        year_wise.append({
            "year": yr + 1,
            "idv": round(idv),
            "depPct": round(dep * 100, 1),
            "odRate": od_rate,
            "odPremium": od_premium,
            "ncbPct": round(ncb_rate * 100, 1),
            "ncbDiscount": ncb_discount,
            "odAfterNcb": od_after_ncb,
            "tpPremium": tp_premium,
            "paCover": pa,
            "gst": gst,
            "totalPremium": round(total_premium),
        })
        total += round(total_premium)

    formula = (
        f"IDV = Ex-showroom × (1 − IRDAI dep%). "
        f"OD = IDV × OD rate. "
        f"NCB applied on OD. "
        f"TP = ₹{tp_base} ({eng}). "
        f"PA = ₹{PA_COVER}. "
        f"GST = 18%."
    )

    return {
        "yearWise": year_wise,
        "totalNYears": total,
        "formula": formula,
        "engineClass": eng,
        "fuelType": fuel,
    }


@router.get("/maintenance-schedule")
def maintenance_schedule(fuel: str = "petrol"):
    """Return the default year-wise maintenance cost array for a fuel type."""
    fuel_key = fuel if fuel in MAINT else "petrol"
    return {"fuel": fuel_key, "schedule": MAINT[fuel_key]}


@router.get("/brands")
def brands(response: Response):
    """Car brands for dropdown."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    return get_brands()


@router.get("/brands/{brand}/models")
def models(brand: str):
    """Models for a brand."""
    return get_models(brand)


@router.get("/brands/{brand}/models/{model_name}/info")
def model_info(brand: str, model_name: str):
    """Model info (resale, eng)."""
    info = get_model_info(brand, model_name)
    if not info:
        raise HTTPException(404, "Model not found")
    return info


# ─── Calculate ───────────────────────────────────────────────────────────

class VehicleInput(BaseModel):
    v: int = Field(1, ge=1, le=3)
    state: str
    fuel: str = Field(..., pattern="^(petrol|diesel|cng|ev|strong_hybrid)$")
    ex: float = Field(..., gt=0, description="Ex-showroom price ₹")
    num_years: int = Field(5, ge=1, le=15)
    acc: float = Field(0, ge=0)
    tax_override: float | None = Field(None, ge=0)
    rto: float = Field(2700, ge=0)
    charger: float = Field(0, ge=0)
    cash: bool = True
    dp: float = Field(0, ge=0)
    tenure: int = Field(60, ge=0, le=96)
    ir: float = Field(8.5, ge=0, le=25)
    mileage: float = Field(18, gt=0)
    fuel_price: float = Field(100, ge=0)
    ann_km: float = Field(15000, gt=0)
    eng: str = Field("mid", pattern="^(small|mid|large)$")
    ins_override_yr1: float | None = Field(None, ge=0)
    tyre_cycle_yrs: int = Field(3, ge=1, le=10)
    tyre_set_cost: float = Field(0, ge=0)
    svc_yr1: float | None = None
    addon_total: float = Field(0, ge=0)
    battery_kwh: float = Field(0, ge=0)
    include_battery: bool = False
    fuel_escal_pct: float = Field(5, ge=0, le=20)
    ncb_mode: str = Field("max", pattern="^(max|avg)$")
    make: str | None = None
    model: str | None = None


class CalculateRequest(BaseModel):
    vehicles: list[VehicleInput]
    num_years_global: int | None = Field(None, ge=1, le=15)


@router.post("/calculate")
def calculate(req: CalculateRequest):
    """
    Compute TCO for 1–3 vehicles. Returns same shape as original single-page app.
    """
    if not req.vehicles:
        raise HTTPException(400, "At least one vehicle required")
    if len(req.vehicles) > 3:
        raise HTTPException(400, "Max 3 vehicles")
    num_years = req.num_years_global or (req.vehicles[0].num_years if req.vehicles else 5)
    results = []
    for vi in req.vehicles:
        r = calc_vehicle(
            vi.v,
            vi.state,
            vi.fuel,
            vi.ex,
            req.num_years_global or vi.num_years,
            acc=vi.acc,
            tax_override=vi.tax_override,
            rto=vi.rto,
            charger=vi.charger,
            cash=vi.cash,
            dp=vi.dp,
            tenure=vi.tenure,
            ir=vi.ir,
            mileage=vi.mileage,
            fuel_price=vi.fuel_price,
            ann_km=vi.ann_km,
            eng=vi.eng,
            ins_override_yr1=vi.ins_override_yr1,
            tyre_cycle_yrs=vi.tyre_cycle_yrs,
            tyre_set_cost=vi.tyre_set_cost,
            svc_yr1=vi.svc_yr1,
            addon_total=vi.addon_total,
            battery_kwh=vi.battery_kwh,
            include_battery=vi.include_battery,
            fuel_escal_pct=vi.fuel_escal_pct,
            ncb_mode=vi.ncb_mode,
            make=vi.make,
            model=vi.model,
        )
        if not r:
            raise HTTPException(400, f"Calculation failed for vehicle {vi.v}")
        results.append(r)
    return {"results": results, "numYears": num_years}
