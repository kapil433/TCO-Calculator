"""
TCO calculation service — one vehicle.
Mirrors the original JS calcVehicle logic.
"""

from app.data.states import get_tax
from app.data.car_db import get_resale_array
from app.util.constants import (
    IDV_D,
    TP,
    PA_COVER,
    INS_GST,
    NCB,
    get_od_rate,
    MAINT,
)


def calc_emi(principal: float, rate_pa: float, months: int) -> tuple[float, float]:
    """Return (emi, total_interest)."""
    if not principal or not months:
        return 0.0, 0.0
    r = rate_pa / 100 / 12
    if r <= 0:
        return principal / months, 0.0
    emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return emi, emi * months - principal


def calc_vehicle(
    v: int,
    state: str,
    fuel: str,
    ex: float,
    num_years: int,
    *,
    acc: float = 0,
    tax_override: float | None = None,
    rto: float = 2700,
    charger: float = 0,
    cash: bool = True,
    dp: float = 0,
    tenure: int = 60,
    ir: float = 8.5,
    mileage: float = 18,
    fuel_price: float = 100,
    ann_km: float = 15000,
    eng: str = "mid",
    ins_override_yr1: float | None = None,
    tyre_cycle_yrs: int = 3,
    tyre_set_cost: float = 0,
    svc_yr1: float | None = None,
    addon_total: float = 0,
    battery_kwh: float = 0,
    include_battery: bool = False,
    fuel_escal_pct: float = 5,
    ncb_mode: str = "max",
    make: str | None = None,
    model: str | None = None,
) -> dict:
    """
    Compute TCO for one vehicle. Returns dict compatible with frontend (tco, bd, resalePerYear, etc.).
    """
    num_years = min(max(1, int(num_years)), 15)
    if ex <= 0:
        return {}

    tax_amt = tax_override if tax_override is not None and tax_override > 0 else get_tax(state, fuel, ex)
    on_road = ex + tax_amt + rto + acc + (charger if fuel == "ev" else 0)

    loan_amt = max(0, on_road - dp) if not cash else 0
    tenure = tenure if not cash and tenure else 0
    ir = ir if not cash else 0
    emi, total_int = (calc_emi(loan_amt, ir, tenure) if loan_amt and tenure else (0.0, 0.0))

    # Fuel cost over num_years with escalation
    escal = fuel_escal_pct / 100
    fuel_cost_n = 0
    for yr in range(1, num_years + 1):
        fuel_cost_n += (ann_km / mileage) * fuel_price * ((1 + escal) ** (yr - 1))
    fuel_cost_n = round(fuel_cost_n)

    # Insurance (IRDAI + NCB)
    ins_total = 0
    ins_arr = []
    tp_base = TP.get(eng, TP["mid"])
    if fuel == "ev":
        tp_base = round(tp_base * 0.85)
    for yr in range(num_years):
        idv = ex * (1 - IDV_D[min(yr, len(IDV_D) - 1)])
        ncb_rate = 0.20 if ncb_mode == "avg" and (yr % 3) == 2 else NCB[min(yr, len(NCB) - 1)]
        od = idv * get_od_rate(idv) * (1 - ncb_rate)
        ins_yr = (od + tp_base + PA_COVER) * (1 + INS_GST)
        if yr == 0 and ins_override_yr1 is not None and ins_override_yr1 > 0:
            ins_yr = ins_override_yr1
        ins_yr = round(ins_yr)
        ins_arr.append(ins_yr)
        ins_total += ins_yr
    ins_total += round(addon_total)

    # Maintenance — optionally scale from user's yr1 override
    maint_list = list(MAINT.get(fuel, MAINT["petrol"]))
    if svc_yr1 is not None and svc_yr1 > 0 and maint_list[0] > 0:
        scale = svc_yr1 / maint_list[0]
        maint_list = [round(m * scale) for m in maint_list]
    maint_total = sum(maint_list[i] for i in range(min(num_years, len(maint_list))))

    # Tyres
    tyre_n = 0
    for yr in range(1, num_years + 1):
        if tyre_cycle_yrs and yr % tyre_cycle_yrs == 0:
            tyre_n += tyre_set_cost

    # Battery provision (EV)
    batt_provision_n = 0
    batt_annual = 0
    if fuel == "ev" and include_battery and battery_kwh > 0:
        cost_per_kwh = 20000
        useful_years = 8
        cost_at_yr_n = battery_kwh * cost_per_kwh * (0.92 ** num_years)
        batt_annual = cost_at_yr_n / useful_years
        batt_provision_n = round(batt_annual * min(num_years, useful_years))

    # Resale (mileage-adjusted)
    resale_arr, resale_src, _ = get_resale_array(make, model, fuel, ann_km=ann_km)
    resale_pct_n = resale_arr[num_years - 1] if num_years <= len(resale_arr) else resale_arr[-1]
    residual_n = round(ex * resale_pct_n)
    resale_per_year = [round(ex * resale_arr[i]) for i in range(min(15, len(resale_arr)))]
    dep_loss = round(ex + tax_amt + rto + acc + (charger if fuel == "ev" else 0) - residual_n)

    tco = (
        on_road
        + (0 if cash else total_int)
        + fuel_cost_n
        + ins_total
        + maint_total
        + tyre_n
        + batt_provision_n
    )
    total_km = ann_km * num_years
    cpkm = tco / total_km if total_km else 0
    net_cost = tco - residual_n

    bd = {
        "On-Road Price": on_road,
        "Fuel / Energy": fuel_cost_n,
        f"Insurance ({num_years}yr)": ins_total,
        f"Maintenance ({num_years}yr)": maint_total,
        f"Tyres ({num_years}yr)": tyre_n,
    }
    if not cash:
        bd["Loan Interest"] = round(total_int)
    if addon_total > 0:
        bd[f"↳ Add-ons ({num_years}yr)"] = round(addon_total)
    if batt_provision_n > 0:
        bd[f"🔋 Battery Reserve ({num_years}yr)"] = batt_provision_n

    result = {
        "v": v,
        "state": state,
        "fuel": fuel,
        "ex": ex,
        "onRoad": on_road,
        "taxAmt": tax_amt,
        "cash": cash,
        "dp": dp if not cash else 0,
        "loanAmt": loan_amt if not cash else 0,
        "tenure": tenure if not cash else 0,
        "ir": ir if not cash else 0,
        "emi": round(emi) if not cash else 0,
        "totalInt": round(total_int) if not cash else 0,
        "numYears": num_years,
        "fuelCostN": fuel_cost_n,
        "insTotal": ins_total,
        "insArr": ins_arr,
        "addonTotal": round(addon_total),
        "maintTotal": maint_total,
        "maintArr": maint_list[:num_years],
        "tyreN": tyre_n,
        "battProvisionN": batt_provision_n,
        "battAnnual": round(batt_annual),
        "battKwh": battery_kwh,
        "residualN": residual_n,
        "resalePerYear": resale_per_year,
        "resalePctN": resale_pct_n,
        "depLoss": dep_loss,
        "netCost": net_cost,
        "tco": round(tco),
        "totalKm": total_km,
        "cpkm": round(cpkm, 2),
        "resaleSrc": resale_src,
        "make": make,
        "model": model,
        "bd": bd,
        "_annKm": ann_km,
        "_mil": mileage,
        "_fprice": fuel_price,
        "_fuelEscalPct": fuel_escal_pct,
        "_eng": eng,
        "_resaleArr": resale_arr,
        "_tyreCycleYrs": tyre_cycle_yrs,
        "_tyreSetCost": tyre_set_cost,
        "_includesBatt": include_battery,
        "_battAnnual": batt_annual,
        "_maintList": maint_list,
        "ncb_mode": ncb_mode,
    }

    result["yearByYear"] = build_yearly_profile(result)
    return result


def _amortize_interest(loan_amt: float, emi: float, tenure: int) -> list[float]:
    """Distribute loan interest across years using proper amortization schedule.
    Uses bisection to find the monthly rate, then tracks month-by-month balance."""
    if loan_amt <= 0 or emi <= 0 or tenure <= 0:
        return []
    lo, hi = 0.0, 0.05
    monthly_rate = 0.007
    for _ in range(50):
        mid = (lo + hi) / 2
        emi_test = loan_amt * mid * (1 + mid) ** tenure / ((1 + mid) ** tenure - 1)
        if emi_test < emi:
            lo = mid
        else:
            hi = mid
        monthly_rate = mid

    balance = loan_amt
    yr_int = 0.0
    result = []
    for m in range(1, tenure + 1):
        int_m = balance * monthly_rate
        yr_int += int_m
        balance = max(0, balance + int_m - emi)
        if m % 12 == 0 or m == tenure:
            result.append(round(yr_int))
            yr_int = 0.0
    return result


def build_yearly_profile(r: dict) -> list[dict]:
    """
    Build year-by-year cost/depreciation/resale profile (always 15 years).
    Mirrors the legacy buildYearlyProfile: amortized loan interest, recalculated
    insurance from IDV/NCB/OD for all years, growth-ratio maintenance, fuel escalation.
    """
    PROFILE_YEARS = 15
    ex = r["ex"]
    on_road = r["onRoad"]
    num_years = r["numYears"]
    fuel = r.get("fuel", "petrol")
    ann_km = r.get("_annKm", 15000)
    mileage = r.get("_mil", 18)
    fuel_price = r.get("_fprice", 100)
    escal_rate = r.get("_fuelEscalPct", 5) / 100
    tyre_cycle = r.get("_tyreCycleYrs", 3)
    tyre_cost = r.get("_tyreSetCost", 0)
    resale_arr = r.get("_resaleArr", [])
    batt_annual = r.get("_battAnnual", 0)
    includes_batt = r.get("_includesBatt", False)
    cash = r.get("cash", True)
    addon_total = r.get("addonTotal", 0)
    eng = r.get("_eng", "mid")
    ncb_mode = r.get("ncb_mode", "max")
    ins_arr_override = r.get("insArr", [])

    # --- Loan interest amortization (front-loaded per year) ---
    amort_int_by_yr = []
    if not cash:
        loan_amt = r.get("loanAmt", 0)
        emi_val = r.get("emi", 0)
        tenure_months = r.get("tenure", 0)
        amort_int_by_yr = _amortize_interest(loan_amt, emi_val, tenure_months)

    # --- Maintenance schedule (growth-ratio, with fuel-specific escalation beyond array) ---
    maint_base_list = list(MAINT.get(fuel, MAINT["petrol"]))
    svc_base = r.get("_maintList", maint_base_list)[0] if r.get("_maintList") else maint_base_list[0]
    maint_by_yr = []
    for i in range(PROFILE_YEARS):
        if i == 0:
            maint_by_yr.append(round(svc_base))
        elif i < len(maint_base_list):
            grow = maint_base_list[i] / maint_base_list[i - 1] if maint_base_list[i - 1] > 0 else 1
            maint_by_yr.append(round(maint_by_yr[i - 1] * grow))
        else:
            esc = 1.08 if fuel == "ev" else 1.18 if fuel == "diesel" else 1.15
            maint_by_yr.append(round(maint_by_yr[i - 1] * esc))

    # --- Insurance: recalculate from scratch for all 15 years ---
    tp_base = TP.get(eng, TP["mid"])
    if fuel == "ev":
        tp_base = round(tp_base * 0.85)

    # --- Fuel base cost ---
    fuel_ann_base = (ann_km / mileage) * fuel_price if mileage > 0 else 0

    profile = []
    cum_cost = on_road

    for yr in range(1, PROFILE_YEARS + 1):
        # Insurance — recalculated per year using IRDAI formula
        idv = ex * (1 - IDV_D[min(yr - 1, len(IDV_D) - 1)])
        if ncb_mode == "avg":
            ncb_rate = 0.20 if ((yr - 1) % 3) == 2 else 0
        else:
            ncb_rate = NCB[min(yr - 1, len(NCB) - 1)]
        od = idv * get_od_rate(idv) * (1 - ncb_rate)
        ins_yr = round((od + tp_base + PA_COVER) * (1 + INS_GST))
        if yr == 1 and ins_arr_override and ins_arr_override[0]:
            ins_yr = ins_arr_override[0]

        maint_yr = maint_by_yr[yr - 1] if yr - 1 < len(maint_by_yr) else maint_by_yr[-1]
        tyre_yr = tyre_cost if tyre_cycle and yr % tyre_cycle == 0 else 0
        batt_yr = round(batt_annual) if includes_batt else 0
        fuel_ann = round(fuel_ann_base * ((1 + escal_rate) ** (yr - 1)))

        addon_yr = round(addon_total / num_years) if yr <= num_years else 0
        loan_int_yr = amort_int_by_yr[yr - 1] if yr - 1 < len(amort_int_by_yr) else 0

        year_cost = fuel_ann + ins_yr + addon_yr + maint_yr + tyre_yr + batt_yr + loan_int_yr
        cum_cost += year_cost

        resale_pct = resale_arr[yr - 1] if yr - 1 < len(resale_arr) else (resale_arr[-1] if resale_arr else 0.5)
        resale_val = round(ex * resale_pct)
        net_cost = cum_cost - resale_val
        total_km = ann_km * yr
        cpkm = round(cum_cost / total_km, 2) if total_km > 0 else 0

        profile.append({
            "yr": yr,
            "yearCost": round(year_cost),
            "cumCost": round(cum_cost),
            "resaleVal": resale_val,
            "resalePct": round(resale_pct * 100, 1),
            "netCost": round(net_cost),
            "cpkm": cpkm,
            "insYr": ins_yr,
            "addonYr": addon_yr,
            "maintYr": maint_yr,
            "tyreYr": tyre_yr,
            "battYr": batt_yr,
            "fuelAnn": fuel_ann,
            "loanIntYr": loan_int_yr,
        })

    return profile
