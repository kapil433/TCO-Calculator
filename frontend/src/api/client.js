/**
 * API client for TCO Calculator backend.
 * Base URL: from env VITE_API_URL or relative /api (proxied in dev).
 */
const BASE = import.meta.env.VITE_API_URL || ''

let _backendStatus = 'unknown'
export function getBackendStatus() { return _backendStatus }

async function fetchWithRetry(url, opts = {}, retries = 3, baseDelay = 1500) {
  for (let i = 0; i <= retries; i++) {
    try {
      const r = await fetch(url, opts)
      if (r.ok) { _backendStatus = 'up'; return r }
      if (r.status >= 500 && i < retries) {
        _backendStatus = 'waking'
        await new Promise((res) => setTimeout(res, baseDelay * Math.pow(2, i)))
        continue
      }
      return r
    } catch (err) {
      _backendStatus = i < retries ? 'waking' : 'down'
      if (i < retries) {
        await new Promise((res) => setTimeout(res, baseDelay * Math.pow(2, i)))
      } else {
        throw err
      }
    }
  }
}

export async function getStates() {
  const r = await fetchWithRetry(`${BASE}/api/v1/tco/states`)
  if (!r.ok) throw new Error('Failed to fetch states')
  return r.json()
}

export async function getFuelPrices(stateCode) {
  const r = await fetch(`${BASE}/api/v1/tco/fuel-prices/${stateCode || 'MH'}`)
  if (!r.ok) throw new Error('Failed to fetch fuel prices')
  return r.json()
}

export async function getFuelPricesLiveMeta() {
  const r = await fetch(`${BASE}/api/v1/tco/fuel-prices/live/meta`)
  if (!r.ok) return { last_updated: null, source: 'static' }
  return r.json()
}

export async function getTax(state, fuel, ex) {
  const r = await fetch(`${BASE}/api/v1/tco/tax?state=${encodeURIComponent(state)}&fuel=${encodeURIComponent(fuel)}&ex=${ex}`)
  if (!r.ok) return { tax: 0, rate_pct: 0, state_note: '' }
  return r.json()
}

export async function getCessBreakdown(state, fuel, ex) {
  const r = await fetch(`${BASE}/api/v1/tco/cess?state=${encodeURIComponent(state)}&fuel=${encodeURIComponent(fuel)}&ex=${ex}`)
  if (!r.ok) return { hasCess: false }
  return r.json()
}

export async function getInsurancePreview(ex, eng, fuel, numYears, ncbMode = 'max') {
  const params = new URLSearchParams({ ex, eng, fuel, num_years: numYears, ncb_mode: ncbMode })
  const r = await fetch(`${BASE}/api/v1/tco/insurance-preview?${params}`)
  if (!r.ok) return null
  return r.json()
}

export async function getMaintenanceSchedule(fuel = 'petrol') {
  const r = await fetch(`${BASE}/api/v1/tco/maintenance-schedule?fuel=${encodeURIComponent(fuel)}`)
  if (!r.ok) return { fuel, schedule: [] }
  return r.json()
}

export async function getBrands() {
  const r = await fetch(`${BASE}/api/v1/tco/brands`)
  if (!r.ok) throw new Error('Failed to fetch brands')
  return r.json()
}

export async function getModels(brand) {
  const r = await fetch(`${BASE}/api/v1/tco/brands/${encodeURIComponent(brand)}/models`)
  if (!r.ok) throw new Error('Failed to fetch models')
  return r.json()
}

export async function getModelInfo(brand, model) {
  const r = await fetch(`${BASE}/api/v1/tco/brands/${encodeURIComponent(brand)}/models/${encodeURIComponent(model)}/info`)
  if (!r.ok) return null
  return r.json()
}

export async function calculateTco(payload) {
  const r = await fetch(`${BASE}/api/v1/tco/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || r.statusText || 'Calculation failed')
  }
  return r.json()
}
