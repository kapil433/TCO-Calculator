import { useEffect, useState, useMemo } from 'react'
import Card from './Card'
import { getFuelPrices, getTax, getCessBreakdown, getInsurancePreview, getMaintenanceSchedule, getModelInfo } from '../api/client'

const FUEL_OPTIONS = [
  { value: 'petrol', label: 'Petrol' },
  { value: 'diesel', label: 'Diesel' },
  { value: 'cng', label: 'CNG' },
  { value: 'ev', label: 'Electric (EV)' },
  { value: 'strong_hybrid', label: 'Strong Hybrid' },
]

const INSURANCE_ADDONS = [
  { key: 'zeroDep', label: 'Zero Depreciation (~20% of OD)', rate: 0.2, maxYr: 5 },
  { key: 'engineProtect', label: 'Engine & Gearbox Protect (~₹1,200/yr)', flat: 1200 },
  { key: 'rsa', label: 'Roadside Assistance (~₹599/yr)', flat: 599 },
  { key: 'returnToInvoice', label: 'Return to Invoice (~10% OD, yr 1–3)', rate: 0.1, maxYr: 3 },
]

function formatRs(n) {
  if (n == null || isNaN(n)) return '₹0'
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`
  return `₹${Math.round(n).toLocaleString('en-IN')}`
}

const numVal = (v) => (v === '' || v == null ? '' : v)
const numSet = (raw) => (raw === '' ? '' : Number(raw))

/* ─── Step 1: State & ownership period ─── */
export function StepStateYears({ stateCode, setStateCode, numYears, setNumYears, states }) {
  return (
    <Card title="State & ownership period">
      <div className="flex-2">
        <div>
          <label>Registration state</label>
          <select value={stateCode} onChange={(e) => setStateCode(e.target.value)}>
            {states.map((s) => (
              <option key={s.code} value={s.code}>{s.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Ownership period (years)</label>
          <select value={numYears} onChange={(e) => setNumYears(Number(e.target.value))}>
            {Array.from({ length: 15 }, (_, i) => i + 1).map((y) => (
              <option key={y} value={y}>{y} year{y > 1 ? 's' : ''}</option>
            ))}
          </select>
        </div>
      </div>
    </Card>
  )
}

/* ─── Step 2: Make / model / fuel / price ─── */
export function StepVehicle({ v, setState, brands, modelsByBrand, onLoadModels }) {
  useEffect(() => {
    if (v.make && !modelsByBrand[v.make]) onLoadModels(v.make)
  }, [v.make])

  useEffect(() => {
    if (v.make && v.model) {
      getModelInfo(v.make, v.model).then((info) => {
        if (info?.eng) setState({ eng: info.eng })
      }).catch(() => {})
    }
  }, [v.make, v.model])

  return (
    <Card title="Make, model & fuel">
      <div className="flex-3" style={{ gap: 12 }}>
        <div>
          <label>Maker / Brand</label>
          <select value={v.make || ''} onChange={(e) => setState({ make: e.target.value, model: '' })}>
            <option value="">— Select —</option>
            {brands.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>
        <div>
          <label>Model</label>
          <select value={v.model || ''} onChange={(e) => setState({ model: e.target.value })} disabled={!v.make}>
            <option value="">— Select —</option>
            {(modelsByBrand[v.make] || []).map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <div>
          <label>Fuel type</label>
          <select value={v.fuel || 'petrol'} onChange={(e) => {
            const f = e.target.value
            const mileageDefaults = { petrol: 18, diesel: 22, cng: 20, ev: 5.5, strong_hybrid: 19 }
            const tyreDefaults = { petrol: 20000, diesel: 22000, cng: 18000, ev: 24000, strong_hybrid: 22000 }
            const tyreCycleDefaults = { petrol: 3, diesel: 3, cng: 3, ev: 4, strong_hybrid: 3 }
            const escalDefaults = { petrol: 5, diesel: 5, cng: 3, ev: 3, strong_hybrid: 5 }
            setState({
              fuel: f,
              mileage: mileageDefaults[f] || 18,
              tyre_set_cost: tyreDefaults[f] || 20000,
              tyre_cycle_yrs: tyreCycleDefaults[f] || 3,
              fuel_escal_pct: escalDefaults[f] || 5,
            })
          }}>
            {FUEL_OPTIONS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
        </div>
      </div>
      <div className="flex-2" style={{ marginTop: 12 }}>
        <div>
          <label>Ex-showroom price (₹)</label>
          <input
            type="number"
            value={numVal(v.ex)}
            onChange={(e) => setState({ ex: numSet(e.target.value) })}
            min={100000} step={50000} placeholder="e.g. 1000000"
          />
        </div>
        <div>
          <label>Accessories / extras (₹)</label>
          <input type="number" value={numVal(v.acc)} onChange={(e) => setState({ acc: numSet(e.target.value) })} min={0} placeholder="0" />
        </div>
      </div>
    </Card>
  )
}

/* ─── Step 3: Life tax + cess + on-road ─── */
export function StepTaxCess({ v, setState, stateCode }) {
  const [taxData, setTaxData] = useState({ tax: 0, rate_pct: 0, state_note: '' })
  const [cessData, setCessData] = useState(null)
  const isEV = v.fuel === 'ev'

  useEffect(() => {
    if (stateCode && v.fuel && v.ex > 0) {
      getTax(stateCode, v.fuel, v.ex).then(setTaxData).catch(() => {})
      getCessBreakdown(stateCode, v.fuel, v.ex).then(setCessData).catch(() => setCessData(null))
    } else {
      setTaxData({ tax: 0, rate_pct: 0, state_note: '' })
      setCessData(null)
    }
  }, [stateCode, v.fuel, v.ex])

  const baseTax = taxData.tax || 0
  const taxAmt = v.tax_override != null && v.tax_override > 0 ? v.tax_override : baseTax
  const onRoad = (Number(v.ex) || 0) + taxAmt + (Number(v.rto) || 2700) + (Number(v.acc) || 0) + (isEV ? (Number(v.charger) || 0) : 0)

  return (
    <Card title="Life tax, cess & on-road price">
      <p className="hint">Auto-calculated from state + fuel + ex-showroom. Override if you have exact RTO quote.</p>
      {taxData.state_note && <p className="hint" style={{ marginTop: 4, fontStyle: 'italic' }}>{taxData.state_note}</p>}

      <div className="flex-2" style={{ marginTop: 10 }}>
        <div>
          <label>Life tax / road tax (₹)</label>
          <input
            type="number"
            value={v.tax_override ?? taxAmt}
            onChange={(e) => setState({ tax_override: e.target.value === '' ? null : Number(e.target.value) })}
            min={0}
          />
          {taxData.rate_pct > 0 && (
            <span className="hint">Effective rate: {taxData.rate_pct}% of ex-showroom</span>
          )}
        </div>
        <div>
          <label>RTO + FASTag + smart card (₹)</label>
          <input type="number" value={numVal(v.rto)} onChange={(e) => setState({ rto: numSet(e.target.value) })} min={0} placeholder="2700" />
        </div>
      </div>

      {cessData?.hasCess && (
        <div style={{ marginTop: 14, padding: 12, background: 'var(--s1)', borderRadius: 8, fontSize: 12 }}>
          <strong style={{ color: 'var(--acc)' }}>{cessData.cessName}</strong>
          {cessData.cessRate > 0 ? (
            <span style={{ marginLeft: 6, color: 'var(--t2)' }}>· <strong>{cessData.cessRate}%</strong> {cessData.basis}</span>
          ) : (
            <span style={{ marginLeft: 6, color: 'var(--t2)' }}>· {cessData.basis}</span>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 8 }}>
            <span>Base life tax <span style={{ color: 'var(--t2)' }}>({cessData.baseTaxRatePct}%)</span> = <strong>{formatRs(cessData.baseTaxAmt)}</strong></span>
            {cessData.cessRate > 0 ? (
              <span>{cessData.cessName} <span style={{ color: 'var(--t2)' }}>({cessData.cessRate}%)</span> = <strong style={{ color: 'var(--acc)' }}>{formatRs(cessData.cessAmt)}</strong></span>
            ) : (
              <span>{cessData.cessName} = <strong style={{ color: 'var(--acc)' }}>{cessData.cessAmt > 0 ? formatRs(cessData.cessAmt) : 'Nil'}</strong></span>
            )}
            <span>Total life tax at RTO = <strong style={{ color: 'var(--green)' }}>{formatRs(cessData.totalTaxAmt)}</strong></span>
            <span className="hint">Effective: {cessData.effective} · Source: {cessData.source}</span>
          </div>
        </div>
      )}

      {isEV && (
        <div style={{ marginTop: 12 }}>
          <label>Home charger installation (₹)</label>
          <input type="number" value={numVal(v.charger)} onChange={(e) => setState({ charger: numSet(e.target.value) })} min={0} placeholder="0" />
        </div>
      )}

      <p style={{ marginTop: 14, fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 600, color: 'var(--green)' }}>
        On-road price: {formatRs(onRoad)}
      </p>
    </Card>
  )
}

/* ─── Step 4: Financing ─── */
export function StepFinance({ v, setState }) {
  const principal = Math.max(0, (Number(v.ex) || 0) - (Number(v.dp) || 0))
  const tenure = Number(v.tenure) || 60
  const rate = Number(v.ir) || 8.5

  const emiInfo = useMemo(() => {
    if (v.cash || principal <= 0 || tenure <= 0) return null
    const r = rate / 100 / 12
    if (r <= 0) return { emi: principal / tenure, totalRepay: principal, interest: 0 }
    const emi = principal * r * Math.pow(1 + r, tenure) / (Math.pow(1 + r, tenure) - 1)
    const totalRepay = emi * tenure
    return { emi, totalRepay, interest: totalRepay - principal }
  }, [v.cash, principal, tenure, rate])

  return (
    <Card title="Financing">
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <button type="button" className={v.cash ? 'btn-primary' : 'btn-secondary'} style={{ flex: 1, padding: 10 }} onClick={() => setState({ cash: true })}>Full cash</button>
        <button type="button" className={!v.cash ? 'btn-primary' : 'btn-secondary'} style={{ flex: 1, padding: 10 }} onClick={() => setState({ cash: false })}>Loan / EMI</button>
      </div>
      {!v.cash && (
        <>
          <div className="flex-3" style={{ gap: 12 }}>
            <div>
              <label>Down payment (₹)</label>
              <input type="number" value={numVal(v.dp)} onChange={(e) => setState({ dp: numSet(e.target.value) })} min={0} placeholder="0" />
            </div>
            <div>
              <label>Loan tenure (months)</label>
              <input type="number" value={numVal(v.tenure)} onChange={(e) => setState({ tenure: numSet(e.target.value) })} min={12} max={96} placeholder="60" />
              <span className="hint">e.g. 60 = 5 yr, 84 = 7 yr</span>
            </div>
            <div>
              <label>Interest rate (% p.a.)</label>
              <input type="number" value={numVal(v.ir)} onChange={(e) => setState({ ir: numSet(e.target.value) })} min={0} max={25} step={0.1} placeholder="8.5" />
            </div>
          </div>
          {emiInfo && (
            <div className="emi-bar">
              <div className="emi-bar-item emi-highlight">
                <span className="emi-label">EMI / month</span>
                <span className="emi-value">{formatRs(emiInfo.emi)}</span>
              </div>
              <span className="emi-sep">·</span>
              <div className="emi-bar-item">
                <span className="emi-label">Loan</span>
                <span className="emi-value">{formatRs(principal)}</span>
              </div>
              <span className="emi-sep">·</span>
              <div className="emi-bar-item">
                <span className="emi-label">Interest total</span>
                <span className="emi-value" style={{ color: 'var(--red)' }}>{formatRs(emiInfo.interest)}</span>
              </div>
              <span className="emi-sep">·</span>
              <div className="emi-bar-item">
                <span className="emi-label">Total repayment</span>
                <span className="emi-value">{formatRs(emiInfo.totalRepay)}</span>
              </div>
            </div>
          )}
        </>
      )}
    </Card>
  )
}

/* ─── Step 5: Insurance ─── */
export function StepInsurance({ v, setState, numYears }) {
  const [preview, setPreview] = useState(null)

  useEffect(() => {
    if (v.ex > 0) {
      getInsurancePreview(v.ex, v.eng || 'mid', v.fuel || 'petrol', numYears, v.ncb_mode || 'max')
        .then(setPreview)
        .catch(() => setPreview(null))
    } else {
      setPreview(null)
    }
  }, [v.ex, v.eng, v.fuel, numYears, v.ncb_mode])

  return (
    <Card title="Insurance">
      <p className="hint">IRDAI formula: IDV × OD rate + TP + PA. Select engine size for TP slab.</p>
      <div className="flex-2" style={{ marginTop: 10 }}>
        <div>
          <label>Engine / motor size</label>
          <select value={v.eng || 'mid'} onChange={(e) => setState({ eng: e.target.value })}>
            <option value="small">{'Small (<1000 cc)'}</option>
            <option value="mid">Mid (1000–1500 cc)</option>
            <option value="large">{'Large (>1500 cc / SUV)'}</option>
          </select>
        </div>
        <div>
          <label>NCB (No Claim Bonus)</label>
          <select value={v.ncb_mode || 'max'} onChange={(e) => setState({ ncb_mode: e.target.value })}>
            <option value="max">Max NCB — zero claims</option>
            <option value="avg">Avg — 1 claim per 3 yr</option>
          </select>
        </div>
      </div>

      <div style={{ marginTop: 10 }}>
        <label>Year 1 premium override (₹) — optional</label>
        <input
          type="number"
          value={v.ins_override_yr1 ?? ''}
          onChange={(e) => setState({ ins_override_yr1: e.target.value ? Number(e.target.value) : null })}
          min={0} placeholder="Your insurer quote"
        />
      </div>

      {preview?.yearWise && (
        <div style={{ marginTop: 14 }}>
          <p className="hint" style={{ marginBottom: 6, fontStyle: 'italic' }}>{preview.formula}</p>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
              <thead>
                <tr style={{ background: 'var(--s1)', textAlign: 'left' }}>
                  <th style={{ padding: '6px 8px' }}>Yr</th>
                  <th style={{ padding: '6px 8px' }}>IDV</th>
                  <th style={{ padding: '6px 8px' }}>OD</th>
                  <th style={{ padding: '6px 8px' }}>NCB%</th>
                  <th style={{ padding: '6px 8px' }}>TP</th>
                  <th style={{ padding: '6px 8px' }}>GST</th>
                  <th style={{ padding: '6px 8px', fontWeight: 700 }}>Total</th>
                </tr>
              </thead>
              <tbody>
                {preview.yearWise.map((y) => (
                  <tr key={y.year} style={{ borderBottom: '1px solid var(--s2)' }}>
                    <td style={{ padding: '5px 8px' }}>{y.year}</td>
                    <td style={{ padding: '5px 8px' }}>{formatRs(y.idv)}</td>
                    <td style={{ padding: '5px 8px' }}>{formatRs(y.odAfterNcb)}</td>
                    <td style={{ padding: '5px 8px' }}>{y.ncbPct}%</td>
                    <td style={{ padding: '5px 8px' }}>{formatRs(y.tpPremium)}</td>
                    <td style={{ padding: '5px 8px' }}>{formatRs(y.gst)}</td>
                    <td style={{ padding: '5px 8px', fontWeight: 600 }}>{formatRs(y.totalPremium)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr style={{ background: 'var(--s1)', fontWeight: 700 }}>
                  <td colSpan={6} style={{ padding: '6px 8px' }}>Total ({numYears} yr)</td>
                  <td style={{ padding: '6px 8px' }}>{formatRs(preview.totalNYears)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}

      <div style={{ marginTop: 14 }}>
        <label style={{ marginBottom: 8 }}>Add-ons</label>
        {INSURANCE_ADDONS.map((a) => (
          <label key={a.key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, fontWeight: 400 }}>
            <input
              type="checkbox"
              checked={v.addons && v.addons[a.key]}
              onChange={(e) => setState({ addons: { ...(v.addons || {}), [a.key]: e.target.checked } })}
            />
            <span style={{ fontSize: 13 }}>{a.label}</span>
          </label>
        ))}
      </div>
    </Card>
  )
}

/* ─── Step 6: Running cost ─── */
export function StepRunning({ v, setState, stateCode }) {
  const isEV = v.fuel === 'ev'

  useEffect(() => {
    if (!stateCode || isEV) return
    getFuelPrices(stateCode).then((prices) => {
      const fuelKey = v.fuel === 'strong_hybrid' ? 'petrol' : v.fuel
      const price = prices[fuelKey]
      if (price != null && v.fuel_price !== price) setState({ fuel_price: price })
    }).catch(() => {})
  }, [stateCode, v.fuel])

  return (
    <Card title="Running cost">
      <p className="hint">Fuel price auto-filled from state average. Editable.</p>
      <div className="flex-2" style={{ marginTop: 10 }}>
        <div>
          <label>{isEV ? 'Range (km/kWh)' : v.fuel === 'cng' ? 'Mileage (km/kg)' : 'Mileage (km/L)'}</label>
          <input type="number" value={numVal(v.mileage)} onChange={(e) => setState({ mileage: numSet(e.target.value) })} min={0} step={isEV ? 0.1 : 1} placeholder={isEV ? '5.5' : '18'} />
        </div>
        <div>
          <label>{isEV ? 'Electricity (₹/kWh)' : v.fuel === 'cng' ? 'CNG (₹/kg)' : 'Fuel (₹/L)'}</label>
          <input type="number" value={numVal(v.fuel_price)} onChange={(e) => setState({ fuel_price: numSet(e.target.value) })} min={0} step={0.1} placeholder="100" />
        </div>
      </div>
      <div className="flex-2" style={{ marginTop: 12 }}>
        <div>
          <label>Annual km driven</label>
          <input type="number" value={numVal(v.ann_km)} onChange={(e) => setState({ ann_km: numSet(e.target.value) })} min={1000} step={1000} placeholder="15000" />
        </div>
        <div>
          <label>Fuel inflation (% per year)</label>
          <input type="number" value={numVal(v.fuel_escal_pct)} onChange={(e) => setState({ fuel_escal_pct: numSet(e.target.value) })} min={0} max={20} placeholder="5" />
        </div>
      </div>
      {isEV && (
        <div style={{ marginTop: 14, padding: 12, background: 'var(--s1)', borderRadius: 8 }}>
          <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--acc)', marginBottom: 8 }}>EV CHARGING MIX</label>
          <div className="flex-3" style={{ gap: 10 }}>
            <div>
              <label>Home charging %</label>
              <input type="number" value={numVal(v.home_charge_pct)} onChange={(e) => setState({ home_charge_pct: numSet(e.target.value) })} min={0} max={100} placeholder="70" />
            </div>
            <div>
              <label>Home rate (₹/kWh)</label>
              <input type="number" value={numVal(v.home_rate)} onChange={(e) => setState({ home_rate: numSet(e.target.value) })} min={0} step={0.5} placeholder="4" />
            </div>
            <div>
              <label>Public/DC rate (₹/kWh)</label>
              <input type="number" value={numVal(v.pub_rate)} onChange={(e) => setState({ pub_rate: numSet(e.target.value) })} min={0} step={0.5} placeholder="15" />
            </div>
          </div>
          <p className="hint" style={{ marginTop: 6 }}>
            Blended: ₹{((Number(v.home_charge_pct) || 70) / 100 * (Number(v.home_rate) || 4) + (1 - (Number(v.home_charge_pct) || 70) / 100) * (Number(v.pub_rate) || 15)).toFixed(1)}/kWh
          </p>
        </div>
      )}
    </Card>
  )
}

/* ─── Step 7: Maintenance + EV battery ─── */
export function StepMaintenance({ v, setState }) {
  const isEV = v.fuel === 'ev'
  const [schedule, setSchedule] = useState(null)

  useEffect(() => {
    const fuel = v.fuel || 'petrol'
    getMaintenanceSchedule(fuel).then(setSchedule).catch(() => setSchedule(null))
  }, [v.fuel])

  const hasOverride = v.svc_yr1 != null && v.svc_yr1 !== '' && Number(v.svc_yr1) > 0
  const overrideScale = hasOverride && schedule?.schedule?.[0]
    ? Number(v.svc_yr1) / schedule.schedule[0]
    : 1

  return (
    <Card title={isEV ? 'Maintenance & battery' : 'Maintenance'}>
      <div className="flex-2" style={{ gap: 12 }}>
        <div>
          <label>Year 1 service cost (₹)</label>
          <input type="number" value={v.svc_yr1 ?? ''} onChange={(e) => setState({ svc_yr1: e.target.value ? Number(e.target.value) : null })} min={0} placeholder={schedule?.schedule?.[0] ? `Default: ₹${schedule.schedule[0].toLocaleString('en-IN')}` : 'Auto from fuel type'} />
        </div>
        <div>
          <label>Tyre set replacement (₹)</label>
          <input type="number" value={numVal(v.tyre_set_cost)} onChange={(e) => setState({ tyre_set_cost: numSet(e.target.value) })} min={0} placeholder="0" />
        </div>
      </div>
      <div style={{ marginTop: 10 }}>
        <label>Tyre replacement interval (years)</label>
        <input type="number" value={numVal(v.tyre_cycle_yrs)} onChange={(e) => setState({ tyre_cycle_yrs: numSet(e.target.value) })} min={1} max={10} placeholder="3" />
      </div>

      {schedule?.schedule && (
        <div className="maint-preview">
          <p className="maint-preview-title">
            Estimated service schedule — {(v.fuel || 'petrol').toUpperCase()}
            {hasOverride && <span style={{ color: 'var(--acc)', marginLeft: 6 }}>(scaled {overrideScale.toFixed(2)}× from your input)</span>}
          </p>
          <div className="maint-preview-grid">
            {schedule.schedule.slice(0, 5).map((cost, i) => {
              const adjusted = hasOverride ? Math.round(cost * overrideScale) : cost
              return (
                <div key={i} className="maint-preview-item">
                  <span className="maint-yr">Yr {i + 1}</span>
                  <span className="maint-cost">{formatRs(adjusted)}</span>
                </div>
              )
            })}
          </div>
          <p className="hint" style={{ marginTop: 6 }}>
            Costs increase annually for wear & aging. Based on industry averages for {(v.fuel || 'petrol')} vehicles.
            {!hasOverride && ' Override Year 1 cost above to scale all years.'}
          </p>
        </div>
      )}

      {isEV && (
        <div style={{ marginTop: 16, padding: 12, background: 'var(--s1)', borderRadius: 8 }}>
          <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--acc)', marginBottom: 8 }}>BATTERY AMORTISATION</label>
          <div>
            <label>Include battery amortisation in TCO?</label>
            <select value={v.include_battery ? 'yes' : 'no'} onChange={(e) => setState({ include_battery: e.target.value === 'yes' })}>
              <option value="no">{'No — under warranty (recommended <5 yr)'}</option>
              <option value="yes">Yes — add annual reserve</option>
            </select>
          </div>
          {v.include_battery && (
            <div style={{ marginTop: 10 }}>
              <label>Battery capacity (kWh)</label>
              <input type="number" value={numVal(v.battery_kwh)} onChange={(e) => setState({ battery_kwh: numSet(e.target.value) })} min={0} placeholder="32" />
            </div>
          )}
        </div>
      )}
    </Card>
  )
}

export default function VehicleForm(props) {
  return null
}
