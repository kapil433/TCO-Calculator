import { useState, useEffect, useCallback } from 'react'
import WizardLayout from './components/WizardLayout'
import ResultsPage from './components/ResultsPage'
import { trackCalculate, trackCompareMode } from './analytics'
import {
  StepStateYears,
  StepVehicle,
  StepTaxCess,
  StepFinance,
  StepInsurance,
  StepRunning,
  StepMaintenance,
} from './components/VehicleForm'
import {
  getStates,
  getBrands,
  getModels,
  getFuelPricesLiveMeta,
  calculateTco,
} from './api/client'

const defaultVehicle = () => ({
  fuel: 'petrol',
  ex: 0,
  acc: 0,
  tax_override: null,
  rto: 2700,
  charger: 0,
  cash: true,
  dp: 0,
  tenure: 60,
  ir: 8.5,
  mileage: 18,
  fuel_price: 100,
  ann_km: 15000,
  eng: 'mid',
  ins_override_yr1: null,
  tyre_cycle_yrs: 3,
  tyre_set_cost: 0,
  addons: {},
  battery_kwh: 32,
  include_battery: false,
  home_charge_pct: 70,
  home_rate: 4,
  pub_rate: 15,
  fuel_escal_pct: 5,
  ncb_mode: 'max',
  make: '',
  model: '',
  svc_yr1: null,
})

function buildAddonTotal(v, numYears) {
  const addons = v.addons || {}
  let total = 0
  if (addons.zeroDep) total += (v.ex || 0) * 0.025 * 0.8 * 0.2 * Math.min(numYears, 5) * 1.18
  if (addons.engineProtect) total += 1200 * numYears * 1.18
  if (addons.rsa) total += 599 * numYears * 1.18
  if (addons.returnToInvoice) total += (v.ex || 0) * 0.025 * 0.8 * 0.1 * Math.min(numYears, 3) * 1.18
  return Math.round(total)
}

function buildVehiclePayload(v, stateCode, numYears) {
  const isEV = v.fuel === 'ev'
  let fuelPrice = Number(v.fuel_price) || 100
  if (isEV && (v.home_charge_pct != null || v.home_rate != null || v.pub_rate != null)) {
    const home = (Number(v.home_charge_pct) || 70) / 100
    fuelPrice = home * (Number(v.home_rate) || 4) + (1 - home) * (Number(v.pub_rate) || 15)
  }
  return {
    v: 1,
    state: stateCode,
    fuel: v.fuel || 'petrol',
    ex: Number(v.ex) || 0,
    num_years: numYears,
    acc: Number(v.acc) || 0,
    tax_override: v.tax_override > 0 ? v.tax_override : null,
    rto: Number(v.rto) || 2700,
    charger: isEV ? (Number(v.charger) || 0) : 0,
    cash: !!v.cash,
    dp: Number(v.dp) || 0,
    tenure: Number(v.tenure) || 60,
    ir: Number(v.ir) || 8.5,
    mileage: Number(v.mileage) || (isEV ? 5.5 : 18),
    fuel_price: fuelPrice,
    ann_km: Number(v.ann_km) || 15000,
    eng: v.eng || 'mid',
    ins_override_yr1: v.ins_override_yr1 > 0 ? v.ins_override_yr1 : null,
    tyre_cycle_yrs: Number(v.tyre_cycle_yrs) || 3,
    tyre_set_cost: Number(v.tyre_set_cost) || 0,
    svc_yr1: v.svc_yr1 != null && Number(v.svc_yr1) > 0 ? Number(v.svc_yr1) : null,
    addon_total: buildAddonTotal(v, numYears),
    battery_kwh: Number(v.battery_kwh) || 0,
    include_battery: !!v.include_battery,
    fuel_escal_pct: Number(v.fuel_escal_pct) || 5,
    ncb_mode: v.ncb_mode || 'max',
    make: v.make || null,
    model: v.model || null,
  }
}

export default function App() {
  const [view, setView] = useState('input')
  const [stateCode, setStateCode] = useState('MH')
  const [numYears, setNumYears] = useState(5)
  const [vehicleCount, setVehicleCount] = useState(1)
  const [vehicles, setVehicles] = useState([defaultVehicle(), defaultVehicle(), defaultVehicle()])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [states, setStates] = useState([])
  const [brands, setBrands] = useState([])
  const [modelsByBrand, setModelsByBrand] = useState({})
  const [fuelLiveMeta, setFuelLiveMeta] = useState({})

  useEffect(() => {
    getStates().then(setStates).catch(() => setStates([{ code: 'MH', name: 'Maharashtra' }]))
    getBrands().then(setBrands).catch(() => setBrands([]))
    getFuelPricesLiveMeta().then(setFuelLiveMeta).catch(() => {})
  }, [])

  const loadModels = useCallback((brand) => {
    if (modelsByBrand[brand]) return
    getModels(brand).then((list) => setModelsByBrand((prev) => ({ ...prev, [brand]: list }))).catch(() => {})
  }, [modelsByBrand])

  const setVehicle = (index, upd) => {
    setVehicles((prev) => {
      const next = [...prev]
      next[index] = typeof upd === 'function' ? upd(next[index]) : { ...next[index], ...upd }
      return next
    })
  }

  const handleCalculate = async () => {
    setError(null)
    setLoading(true)
    const count = vehicleCount
    const payloads = vehicles.slice(0, count).map((v, i) => ({
      ...buildVehiclePayload(v, stateCode, numYears),
      v: i + 1,
    }))
    const invalid = payloads.find((p) => !p.ex || p.ex <= 0)
    if (invalid) {
      setError('Enter ex-showroom price for all vehicles.')
      setLoading(false)
      return
    }
    try {
      const { results: res } = await calculateTco({
        vehicles: payloads,
        num_years_global: numYears,
      })
      trackCalculate(payloads, numYears)
      setResults(res)
      setView('results')
    } catch (e) {
      setError(e.message)
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  if (view === 'results' && results) {
    return (
      <div>
        <header style={{ padding: '12px 16px', borderBottom: '1px solid var(--bd)', background: 'var(--bg-card)' }}>
          <h1 style={{ fontSize: 'clamp(15px, 3.5vw, 18px)', fontWeight: 700 }}>TCO Results</h1>
        </header>
        <ResultsPage results={results} numYears={numYears} onBack={() => setView('input')} />
      </div>
    )
  }

  const activeVehicles = vehicles.slice(0, vehicleCount)
  const VCOLORS = ['#d4a017', '#1971c2', '#2f9e44']

  const makeSetState = (idx) => (upd) => setVehicle(idx, upd)

  const renderStepForVehicles = (StepComponent, extraProps = {}) => {
    if (vehicleCount === 1) {
      return <StepComponent v={vehicles[0]} setState={makeSetState(0)} {...extraProps} />
    }
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {activeVehicles.map((_, i) => (
          <div key={i} style={{ borderLeft: `3px solid ${VCOLORS[i]}`, paddingLeft: 12 }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: VCOLORS[i], marginBottom: 6 }}>Vehicle {i + 1}</p>
            <StepComponent v={vehicles[i]} setState={makeSetState(i)} {...extraProps} />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: 'clamp(12px, 3vw, 24px) clamp(10px, 3vw, 20px) 80px' }}>
      <header style={{ paddingBottom: 20, borderBottom: '1px solid var(--bd)', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
          <div style={{ minWidth: 0, flex: '1 1 200px' }}>
            <h1 style={{ fontSize: 'clamp(16px, 4vw, 22px)', fontWeight: 700, lineHeight: 1.3 }}>4-Wheeler PV TCO Calculator</h1>
            <p style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--t2)', marginTop: 4 }}>
              India · Total Cost of Ownership · State-wise tax · IRDAI · Resale
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
            {[1, 2, 3].map((n) => (
              <button
                key={n}
                type="button"
                className={vehicleCount === n ? 'btn-primary' : 'btn-secondary'}
                style={{ width: 'auto', padding: '8px 14px', fontSize: 12 }}
                onClick={() => { setVehicleCount(n); if (n > 1) trackCompareMode(n) }}
              >
                {n === 1 ? '1 Vehicle' : `Compare ${n}`}
              </button>
            ))}
          </div>
        </div>
        {fuelLiveMeta?.last_updated && (
          <p style={{ fontSize: 10, color: 'var(--t3)', marginTop: 8 }}>
            Fuel prices updated: {fuelLiveMeta.last_updated?.slice(0, 10)}
          </p>
        )}
      </header>

      <WizardLayout onCalculate={handleCalculate} loading={loading}>
        {/* Step 0: State & Years — always shared, single card */}
        <StepStateYears
          stateCode={stateCode}
          setStateCode={setStateCode}
          numYears={numYears}
          setNumYears={setNumYears}
          states={states}
        />
        {/* Step 1: Vehicle — per vehicle */}
        {renderStepForVehicles(StepVehicle, { brands, modelsByBrand, onLoadModels: loadModels })}
        {/* Step 2: Tax — per vehicle */}
        {renderStepForVehicles(StepTaxCess, { stateCode })}
        {/* Step 3: Finance — per vehicle */}
        {renderStepForVehicles(StepFinance)}
        {/* Step 4: Insurance — per vehicle */}
        {renderStepForVehicles(StepInsurance, { numYears })}
        {/* Step 5: Running — per vehicle */}
        {renderStepForVehicles(StepRunning, { stateCode })}
        {/* Step 6: Maintenance — per vehicle */}
        {renderStepForVehicles(StepMaintenance)}
      </WizardLayout>

      {error && (
        <div style={{ marginTop: 16, padding: 14, background: 'rgba(201,42,42,0.1)', border: '1px solid var(--red)', borderRadius: 8, color: 'var(--red)', fontSize: 13 }}>
          {error}
        </div>
      )}

      <footer className="app-footer">
        <div className="footer-inner">
          <p className="footer-brand">4-Wheeler PV TCO Calculator — India</p>
          <p className="footer-desc">
            Compare total cost of ownership for Petrol, Diesel, CNG, EV &amp; Hybrid vehicles.
            State-wise life tax, IRDAI insurance, model-specific depreciation &amp; resale.
          </p>
          <div className="footer-links">
            <a href="https://github.com/kapil433/TCO-Calculator" target="_blank" rel="noopener noreferrer">GitHub</a>
            <span className="footer-sep">·</span>
            <a href="https://kapil433.github.io/TCO-Calculator/" target="_blank" rel="noopener noreferrer">Live App</a>
          </div>
          <p className="footer-legal">
            &copy; {new Date().getFullYear()} Kapil Lodha. Open-source under MIT License.<br />
            Data sources: IRDAI, state RTO portals, industry depreciation benchmarks. Figures are estimates for educational use only — not financial advice.
          </p>
        </div>
      </footer>
    </div>
  )
}
