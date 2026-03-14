import { useState, useRef, useMemo, Fragment } from 'react'
import { jsPDF } from 'jspdf'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, PointElement, LineElement,
  ArcElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { Bar, Line, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale, BarElement, PointElement, LineElement,
  ArcElement, Title, Tooltip, Legend, Filler,
)

const TABS = ['Summary', 'Cost Analysis', 'Resale & Depreciation', 'Year-by-Year', 'Smart Insights']
const VCOLORS = ['#d4a017', '#1971c2', '#2f9e44']
const VCOLORS_L = ['rgba(212,160,23,0.18)', 'rgba(25,113,194,0.18)', 'rgba(47,158,68,0.18)']
const CAT_COLORS = ['#d4a017', '#1971c2', '#2f9e44', '#e8590c', '#9c36b5', '#c92a2a', '#0ca678']

function fmt(n) {
  if (n == null || isNaN(n)) return '₹0'
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`
  return `₹${Math.round(n).toLocaleString('en-IN')}`
}
function fmtN(n) { return n == null || isNaN(n) ? '0' : Math.round(n).toLocaleString('en-IN') }
function pct(part, total) { return total > 0 ? ((part / total) * 100).toFixed(1) : '0.0' }
function vLabel(r, i) {
  const p = [`V${i + 1}`]
  if (r.make) p.push(r.make)
  if (r.model) p.push(r.model)
  p.push(`(${r.fuel})`)
  return p.join(' ')
}

function getCats(results, numYears) {
  const cats = [
    { key: 'onRoad', label: 'On-Road Price', get: (r) => r.onRoad },
    { key: 'fuel', label: 'Fuel / Energy', get: (r) => r.fuelCostN },
    { key: 'ins', label: `Insurance (${numYears}yr)`, get: (r) => r.insTotal },
    { key: 'maint', label: `Maintenance (${numYears}yr)`, get: (r) => r.maintTotal },
    { key: 'tyres', label: `Tyres (${numYears}yr)`, get: (r) => r.tyreN },
  ]
  if (results.some((r) => !r.cash)) cats.push({ key: 'int', label: 'Loan Interest', get: (r) => r.totalInt || 0 })
  if (results.some((r) => r.addonTotal > 0)) cats.push({ key: 'addon', label: 'Add-ons', get: (r) => r.addonTotal || 0 })
  if (results.some((r) => r.battProvisionN > 0)) cats.push({ key: 'batt', label: 'Battery Reserve', get: (r) => r.battProvisionN || 0 })
  return cats
}

function getBadges(results) {
  if (results.length < 2) return []
  const badges = []
  const minTco = Math.min(...results.map((r) => r.tco))
  const bestResale = Math.max(...results.map((r) => r.residualN))
  const lowestFuel = Math.min(...results.map((r) => r.fuelCostN))
  const lowestRun = Math.min(...results.map((r) => r.fuelCostN + r.maintTotal))
  results.forEach((r, i) => {
    const b = []
    if (r.tco === minTco) b.push('Lowest TCO')
    if (r.residualN === bestResale) b.push('Best Resale')
    if (r.fuelCostN === lowestFuel) b.push('Lowest Fuel')
    if ((r.fuelCostN + r.maintTotal) === lowestRun) b.push('Lowest Running')
    badges.push(b)
  })
  return badges
}

/* ═══════ TAB 1: Summary ═══════ */
function SummaryTab({ results, numYears, summaryRef }) {
  const badges = getBadges(results)
  const cats = getCats(results, numYears)
  const multi = results.length > 1

  const compBarData = multi ? {
    labels: results.map((r, i) => vLabel(r, i)),
    datasets: cats.map((cat, ci) => ({
      label: cat.label,
      data: results.map((r) => cat.get(r)),
      backgroundColor: CAT_COLORS[ci % CAT_COLORS.length],
      borderRadius: 3,
    })),
  } : null

  const anyFinanced = results.some((r) => !r.cash)

  return (
    <div ref={summaryRef}>
      {multi && badges.some((b) => b.length > 0) && (
        <div className="summary-grid" style={{ gridTemplateColumns: `repeat(${Math.min(results.length, 3)}, 1fr)`, marginBottom: 8 }}>
          {results.map((r, i) => (
            <div key={i} style={{ display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'center', minHeight: 24 }}>
              {(badges[i] || []).map((b) => <span key={b} className="badge">{b}</span>)}
            </div>
          ))}
        </div>
      )}
      <div className="summary-grid" style={{ gridTemplateColumns: `repeat(${Math.min(results.length, 3)}, 1fr)`, alignItems: 'stretch' }}>
        {results.map((r, i) => (
          <div key={i} className="summary-card" style={{ borderTopColor: VCOLORS[i], display: 'flex', flexDirection: 'column' }}>
            <div className="summary-card-title" style={{ color: VCOLORS[i] }}>{vLabel(r, i)}</div>
            <p className="summary-tco">{fmt(r.tco)}</p>
            <p className="summary-sub">{numYears} years · {r.totalKm?.toLocaleString('en-IN')} km</p>
            <div className="summary-metrics" style={{ flex: 1 }}>
              <div className="sm-row"><span>Cost / km</span><span className="sm-val">₹{r.cpkm}</span></div>
              <div className="sm-row"><span>Net cost / km</span><span className="sm-val">₹{r.totalKm ? (r.netCost / r.totalKm).toFixed(2) : 0}</span></div>
              <div className="sm-row"><span>On-road</span><span>{fmt(r.onRoad)}</span></div>
              <div className="sm-row"><span>Resale @ yr {numYears}</span><span style={{ color: 'var(--green)' }}>{fmt(r.residualN)}</span></div>
              <div className="sm-row"><span>Net cost</span><span className="sm-val">{fmt(r.netCost)}</span></div>
              {anyFinanced && (
                <div className="sm-row"><span>EMI / month</span><span>{!r.cash ? fmt(r.emi) : '—'}</span></div>
              )}
            </div>
          </div>
        ))}
      </div>
      {compBarData && (
        <div className="chart-container" style={{ maxWidth: 800, margin: '24px auto 0' }}>
          <Bar data={compBarData} options={{
            responsive: true, plugins: { title: { display: true, text: 'TCO Composition Comparison' }, legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
            scales: { x: { stacked: true }, y: { stacked: true, ticks: { callback: (v) => fmt(v) } } },
          }} />
        </div>
      )}
    </div>
  )
}

/* ═══════ TAB 2: Cost Analysis ═══════ */
function CostAnalysisTab({ results, numYears }) {
  const cats = getCats(results, numYears)
  const multi = results.length > 1

  const analysisQuotes = results.map((r, i) => {
    const topCat = cats.slice().sort((a, b) => b.get(r) - a.get(r))[0]
    const topPct = pct(topCat.get(r), r.tco)
    return `${vLabel(r, i)}: ${topCat.label} is the largest expense at ${topPct}% of total TCO (${fmt(topCat.get(r))}).`
  })

  return (
    <div>
      <div className={multi ? 'cost-grid' : ''} style={multi ? { gridTemplateColumns: `repeat(${results.length}, 1fr)` } : {}}>
        {results.map((r, i) => {
          const data = {
            labels: cats.map((c) => c.label.replace(/ \(\d+yr\)/, '')),
            datasets: [{
              data: cats.map((c) => c.get(r)),
              backgroundColor: CAT_COLORS.slice(0, cats.length),
              borderWidth: 0,
            }],
          }
          return (
            <div key={i} className="chart-container" style={{ textAlign: 'center' }}>
              <h4 style={{ fontSize: 13, fontWeight: 600, color: VCOLORS[i], marginBottom: 8 }}>{vLabel(r, i)}</h4>
              <div style={{ maxWidth: 260, margin: '0 auto' }}>
                <Doughnut data={data} options={{
                  responsive: true, cutout: '55%',
                  plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }, tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${fmt(ctx.raw)} (${pct(ctx.raw, r.tco)}%)` } } },
                }} />
              </div>
              <p style={{ fontFamily: 'var(--mono)', fontSize: 18, fontWeight: 700, marginTop: 10, color: VCOLORS[i] }}>{fmt(r.tco)}</p>
            </div>
          )
        })}
      </div>

      <div style={{ overflowX: 'auto', marginTop: 24 }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>Category</th>
              {results.map((r, i) => (
                <th key={i} colSpan={2} style={{ textAlign: 'right', color: VCOLORS[i] }}>{vLabel(r, i)}</th>
              ))}
            </tr>
            <tr>
              <th></th>
              {results.map((_, i) => (
                <Fragment key={`h${i}`}><th style={{ textAlign: 'right', fontSize: 10, color: 'var(--t3)' }}>Amount</th><th style={{ textAlign: 'right', fontSize: 10, color: 'var(--t3)' }}>%</th></Fragment>
              ))}
            </tr>
          </thead>
          <tbody>
            {cats.map((cat) => (
              <tr key={cat.key}>
                <td>{cat.label}</td>
                {results.map((r, i) => (
                  <Fragment key={i}><td className="mono-r">{fmt(cat.get(r))}</td><td className="mono-r hint-r">{pct(cat.get(r), r.tco)}%</td></Fragment>
                ))}
              </tr>
            ))}
            <tr className="total-row">
              <td>Total TCO</td>
              {results.map((r, i) => (
                <Fragment key={i}><td className="mono-r" style={{ color: VCOLORS[i] }}>{fmt(r.tco)}</td><td className="mono-r">100%</td></Fragment>
              ))}
            </tr>
            <tr className="green-row">
              <td>Resale value</td>
              {results.map((r, i) => (
                <Fragment key={i}><td className="mono-r" style={{ color: 'var(--green)' }}>{fmt(r.residualN)}</td><td className="mono-r hint-r">{pct(r.residualN, r.tco)}%</td></Fragment>
              ))}
            </tr>
            <tr className="total-row">
              <td>Net Cost (TCO − Resale)</td>
              {results.map((r, i) => (
                <Fragment key={i}><td className="mono-r">{fmt(r.netCost)}</td><td className="mono-r"></td></Fragment>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {multi && (
        <div className="chart-container" style={{ maxWidth: 700, margin: '24px auto 0' }}>
          <Bar data={{
            labels: cats.map((c) => c.label.replace(/ \(\d+yr\)/, '')),
            datasets: results.map((r, i) => ({
              label: vLabel(r, i), data: cats.map((c) => c.get(r)), backgroundColor: VCOLORS[i], borderRadius: 3,
            })),
          }} options={{
            responsive: true, indexAxis: 'y',
            plugins: { title: { display: true, text: 'Category-wise Comparison' }, legend: { position: 'top' } },
            scales: { x: { ticks: { callback: (v) => fmt(v) } } },
          }} />
        </div>
      )}

      <div className="insight-box" style={{ marginTop: 20 }}>
        <strong>Analysis</strong>
        {analysisQuotes.map((q, i) => <p key={i} style={{ marginTop: 4, fontSize: 13 }}>{q}</p>)}
      </div>
    </div>
  )
}

/* ═══════ TAB 3: Resale & Depreciation ═══════ */
function ResaleDepTab({ results, numYears }) {
  const allYears = Array.from({ length: 15 }, (_, i) => i + 1)

  const depCurveData = {
    labels: allYears.map((y) => `Yr ${y}`),
    datasets: results.flatMap((r, i) => [
      {
        label: `${vLabel(r, i)} — Resale Value`,
        data: (r.resalePerYear || []).slice(0, 15),
        borderColor: VCOLORS[i], backgroundColor: VCOLORS_L[i],
        tension: 0.35, fill: true, pointRadius: 3,
      },
      {
        label: `${vLabel(r, i)} — Ex-showroom`,
        data: allYears.map(() => r.ex),
        borderColor: VCOLORS[i], borderDash: [6, 3],
        tension: 0, fill: false, pointRadius: 0,
      },
    ]),
  }

  const optimalSell = results.map((r) => {
    const yby = r.yearByYear || []
    if (yby.length < 3) return null
    let minAvg = Infinity
    let bestYear = null
    for (let y = 0; y < yby.length; y++) {
      const yr = y + 1
      const cumTotal = yby[y]?.cumCost || 0
      const resaleAtY = r.resalePerYear?.[y] || 0
      const netOwnership = cumTotal - resaleAtY
      const avgAnnual = netOwnership / yr
      if (avgAnnual < minAvg) {
        minAvg = avgAnnual
        bestYear = yr
      }
    }
    if (!bestYear || bestYear >= yby.length) return null
    return { year: bestYear, avgCost: Math.round(minAvg) }
  })

  return (
    <div>
      <div className="insight-box">
        <strong>How resale value is calculated</strong>
        {results.map((r, i) => (
          <p key={i} style={{ marginTop: 6, fontSize: 13 }}>
            <span style={{ color: VCOLORS[i], fontWeight: 600 }}>{vLabel(r, i)}:</span>{' '}
            Model/brand-specific depreciation data for years 1–5, extended using
            the {r.fuel.toUpperCase()} fuel-type curve for years 6–15 (IRDAI-aligned), adjusted for your annual km.
            At year {numYears}, resale is <strong>{fmt(r.residualN)}</strong> ({r.resalePctN != null ? `${(r.resalePctN * 100).toFixed(1)}%` : '—'} of ex-showroom).
          </p>
        ))}
      </div>

      <div className="chart-container" style={{ marginTop: 20 }}>
        <Line data={depCurveData} options={{
          responsive: true,
          plugins: { title: { display: true, text: 'Depreciation Curve — 15 Year Projection' }, legend: { position: 'bottom', labels: { boxWidth: 12 } },
            annotation: numYears <= 15 ? {} : undefined },
          scales: { y: { ticks: { callback: (v) => fmt(v) }, title: { display: true, text: 'Value (₹)' } } },
        }} />
        {numYears <= 15 && (
          <p className="hint" style={{ textAlign: 'center', marginTop: 4 }}>Your {numYears}-year ownership period highlighted. Curve shows 15-year projection.</p>
        )}
      </div>

      {optimalSell.some((o) => o) && (
        <div className="insight-box" style={{ marginTop: 16, background: 'rgba(47,158,68,0.08)' }}>
          <strong>Optimal Replacement Window</strong>
          <p style={{ fontSize: 13, marginTop: 4 }}>
            Based on <em>Equivalent Annual Cost (EAC)</em> analysis — the year where your
            average annual cost of ownership (on-road price + all running costs − resale value,
            divided by years held) reaches its <strong>minimum</strong>. Before this point,
            high early depreciation dominates; after it, rising maintenance and running costs
            push the average back up.
          </p>
          {results.map((r, i) => optimalSell[i] && (
            <p key={i} style={{ marginTop: 4, fontSize: 13 }}>
              <span style={{ color: VCOLORS[i], fontWeight: 600 }}>{vLabel(r, i)}:</span>{' '}
              Best to sell around <strong>year {optimalSell[i].year}</strong>{' '}
              (avg. annual cost: <strong>{fmt(optimalSell[i].avgCost)}</strong>/yr).
            </p>
          ))}
        </div>
      )}

      {results.map((r, ri) => (
        <div key={ri} style={{ marginTop: 24 }}>
          <h4 style={{ fontSize: 14, fontWeight: 600, color: VCOLORS[ri], marginBottom: 8 }}>{vLabel(r, ri)} — Year-by-Year Depreciation</h4>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ fontSize: 11 }}>
              <thead>
                <tr>
                  <th>Year</th><th className="r">Resale %</th><th className="r">Resale Value</th><th className="r">Annual Dep.</th><th className="r">Cumulative Cost</th><th className="r">Net Cost</th>
                </tr>
              </thead>
              <tbody>
                {(r.yearByYear || []).map((y, yi) => {
                  const prevResale = yi > 0 ? (r.resalePerYear?.[yi - 1] || 0) : r.ex
                  const annDep = prevResale - (r.resalePerYear?.[yi] || 0)
                  return (
                    <tr key={y.yr} style={y.yr === numYears ? { background: 'rgba(212,160,23,0.08)', fontWeight: 600 } : {}}>
                      <td>{y.yr}{y.yr === numYears ? ' ←' : ''}</td>
                      <td className="r">{y.resalePct}%</td>
                      <td className="r mono" style={{ color: 'var(--green)' }}>{fmt(y.resaleVal)}</td>
                      <td className="r mono" style={{ color: 'var(--red)' }}>{fmt(annDep)}</td>
                      <td className="r mono">{fmt(y.cumCost)}</td>
                      <td className="r mono" style={{ fontWeight: 600 }}>{fmt(y.netCost)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}

/* ═══════ TAB 4: Year-by-Year ═══════ */
function YearByYearTab({ results, numYears }) {
  const maxYears = Math.max(...results.map((r) => r.yearByYear?.length || 0))
  const yearLabels = Array.from({ length: maxYears }, (_, i) => `Yr ${i + 1}`)

  const stackedData = results.length === 1 ? {
    labels: yearLabels,
    datasets: [
      { label: 'Fuel', data: results[0].yearByYear?.map((y) => y.fuelAnn) || [], backgroundColor: CAT_COLORS[1] },
      { label: 'Insurance', data: results[0].yearByYear?.map((y) => y.insYr) || [], backgroundColor: CAT_COLORS[2] },
      { label: 'Maintenance', data: results[0].yearByYear?.map((y) => y.maintYr) || [], backgroundColor: CAT_COLORS[3] },
      { label: 'Tyres', data: results[0].yearByYear?.map((y) => y.tyreYr) || [], backgroundColor: CAT_COLORS[4] },
      { label: 'Battery', data: results[0].yearByYear?.map((y) => y.battYr) || [], backgroundColor: CAT_COLORS[5] },
    ].filter((d) => d.data.some((v) => v > 0)),
  } : null

  const cumData = {
    labels: yearLabels,
    datasets: results.map((r, i) => ({
      label: `${vLabel(r, i)} — Cumulative`,
      data: (r.yearByYear || []).map((y) => y.cumCost),
      borderColor: VCOLORS[i], backgroundColor: VCOLORS_L[i],
      tension: 0.3, fill: false,
    })),
  }

  return (
    <div>
      {results.map((r, ri) => (
        <div key={ri} style={{ marginBottom: 24 }}>
          <h4 style={{ fontSize: 14, fontWeight: 600, color: VCOLORS[ri], marginBottom: 8 }}>{vLabel(r, ri)}</h4>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ fontSize: 11 }}>
              <thead>
                <tr>
                  <th>Year</th><th className="r">Year Cost</th><th className="r">Cumulative</th>
                  <th className="r">Resale %</th><th className="r">Resale Val</th><th className="r">Net Cost</th>
                  <th className="r">₹/km</th><th className="r">Insurance</th><th className="r">Maint.</th><th className="r">Fuel</th>
                  <th className="r">Tyres</th><th className="r">Battery</th>
                </tr>
              </thead>
              <tbody>
                {(r.yearByYear || []).map((y) => (
                  <tr key={y.yr}>
                    <td>{y.yr}</td>
                    <td className="r mono">{fmt(y.yearCost)}</td><td className="r mono">{fmt(y.cumCost)}</td>
                    <td className="r">{y.resalePct}%</td><td className="r mono green">{fmt(y.resaleVal)}</td>
                    <td className="r mono bold">{fmt(y.netCost)}</td><td className="r">₹{y.cpkm}</td>
                    <td className="r mono">{fmt(y.insYr)}</td><td className="r mono">{fmt(y.maintYr)}</td>
                    <td className="r mono">{fmt(y.fuelAnn)}</td>
                    <td className="r mono">{y.tyreYr > 0 ? fmt(y.tyreYr) : '—'}</td>
                    <td className="r mono">{y.battYr > 0 ? fmt(y.battYr) : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      <div className="charts-row">
        {stackedData && (
          <div className="chart-container">
            <Bar data={stackedData} options={{
              responsive: true, plugins: { title: { display: true, text: 'Annual Cost Composition' }, legend: { position: 'bottom', labels: { boxWidth: 12 } } },
              scales: { x: { stacked: true }, y: { stacked: true, ticks: { callback: (v) => fmt(v) } } },
            }} />
          </div>
        )}
        <div className="chart-container">
          <Line data={cumData} options={{
            responsive: true, plugins: { title: { display: true, text: 'Cumulative Cost Over Time' }, legend: { position: 'bottom' } },
            scales: { y: { ticks: { callback: (v) => fmt(v) } } },
          }} />
        </div>
      </div>
    </div>
  )
}

/* ═══════ TAB 5: Smart Insights ═══════ */
function InsightsTab({ results, numYears }) {
  const multi = results.length > 1
  const cats = getCats(results, numYears)

  const gradeOf = (cpkm) => cpkm <= 5 ? 'A' : cpkm <= 8 ? 'B' : cpkm <= 12 ? 'C' : cpkm <= 18 ? 'D' : 'E'
  const gradeLabels = { A: 'Excellent', B: 'Good', C: 'Average', D: 'High', E: 'Very High' }

  const perVehicle = results.map((r, i) => {
    const label = vLabel(r, i)
    const g = gradeOf(r.cpkm)
    const fuelPct = parseFloat(pct(r.fuelCostN, r.tco))
    const maintPct = parseFloat(pct(r.maintTotal, r.tco))
    const lastYr = r.yearByYear?.[r.yearByYear.length - 1]
    const yr1 = r.yearByYear?.[0]
    const maintGrowth = lastYr?.maintYr > 0 && yr1?.maintYr > 0
      ? ((lastYr.maintYr / yr1.maintYr - 1) * 100).toFixed(0) : '0'
    return { label, r, i, g, fuelPct, maintPct, lastYr, yr1, maintGrowth: Number(maintGrowth) }
  })

  if (multi) {
    const sorted = [...results].sort((a, b) => a.netCost - b.netCost)
    const best = sorted[0]
    const worst = sorted[sorted.length - 1]
    const bi = results.indexOf(best)
    const wi = results.indexOf(worst)
    const saving = worst.netCost - best.netCost

    const bestVal = (arr, fn) => {
      const vals = arr.map(fn)
      const minI = vals.indexOf(Math.min(...vals))
      return minI
    }
    const worstVal = (arr, fn) => {
      const vals = arr.map(fn)
      const maxI = vals.indexOf(Math.max(...vals))
      return maxI
    }

    const cellStyle = (vi, bestI, worstI) => ({
      fontWeight: vi === bestI ? 700 : 400,
      color: vi === bestI ? 'var(--green)' : vi === worstI ? 'var(--red)' : undefined,
    })

    const bestTco = bestVal(results, (r) => r.tco)
    const worstTco = worstVal(results, (r) => r.tco)
    const bestNet = bestVal(results, (r) => r.netCost)
    const worstNet = worstVal(results, (r) => r.netCost)
    const bestCpkm = bestVal(results, (r) => r.cpkm)
    const worstCpkm = worstVal(results, (r) => r.cpkm)
    const bestResale = bestVal(results, (r) => -r.residualN)
    const worstResale = worstVal(results, (r) => -r.residualN)
    const bestFuelPct = bestVal(perVehicle, (v) => v.fuelPct)
    const worstFuelPct = worstVal(perVehicle, (v) => v.fuelPct)
    const bestMaintPct = bestVal(perVehicle, (v) => v.maintPct)
    const worstMaintPct = worstVal(perVehicle, (v) => v.maintPct)

    return (
      <div>
        <div className="insight-box" style={{ marginBottom: 16, background: 'rgba(47,158,68,0.08)' }}>
          <strong>🏆 Verdict</strong>
          <p style={{ fontSize: 13, marginTop: 4 }}>
            <strong style={{ color: VCOLORS[bi] }}>{vLabel(best, bi)}</strong> has the lowest net cost,
            saving <strong>{fmt(saving)}</strong> over {numYears} years compared
            to {vLabel(worst, wi)}.{best.residualN > worst.residualN ? ' It also holds its value better.' : ''}
          </p>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Metric</th>
                {results.map((r, i) => (
                  <th key={i} className="r" style={{ color: VCOLORS[i], minWidth: 120 }}>{vLabel(r, i)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Ownership Rating</strong></td>
                {perVehicle.map((v, i) => (
                  <td key={i} className="r">
                    <span className={`grade grade-${v.g}`} style={{ display: 'inline-flex', width: 24, height: 24, fontSize: 12 }}>{v.g}</span>
                    <span style={{ marginLeft: 6, fontSize: 11, color: 'var(--t2)' }}>{gradeLabels[v.g]}</span>
                  </td>
                ))}
              </tr>
              <tr>
                <td>Total TCO</td>
                {results.map((r, i) => <td key={i} className="mono-r r" style={cellStyle(i, bestTco, worstTco)}>{fmt(r.tco)}</td>)}
              </tr>
              <tr>
                <td>Net Cost (after resale)</td>
                {results.map((r, i) => <td key={i} className="mono-r r" style={cellStyle(i, bestNet, worstNet)}>{fmt(r.netCost)}</td>)}
              </tr>
              <tr>
                <td>Cost / km</td>
                {results.map((r, i) => <td key={i} className="mono-r r" style={cellStyle(i, bestCpkm, worstCpkm)}>₹{r.cpkm}</td>)}
              </tr>
              <tr>
                <td>Resale @ yr {numYears}</td>
                {results.map((r, i) => <td key={i} className="mono-r r" style={cellStyle(i, bestResale, worstResale)}>{fmt(r.residualN)}</td>)}
              </tr>
              <tr>
                <td>Fuel % of TCO</td>
                {perVehicle.map((v, i) => (
                  <td key={i} className="r" style={cellStyle(i, bestFuelPct, worstFuelPct)}>
                    {v.fuelPct}%{v.fuelPct > 40 ? <span style={{ fontSize: 10, color: 'var(--red)', marginLeft: 4 }}>High</span> : ''}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Maintenance % of TCO</td>
                {perVehicle.map((v, i) => (
                  <td key={i} className="r" style={cellStyle(i, bestMaintPct, worstMaintPct)}>
                    {v.maintPct}%{v.maintPct > 20 ? <span style={{ fontSize: 10, color: 'var(--red)', marginLeft: 4 }}>High</span> : ''}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Maint. Growth (yr 1→{numYears})</td>
                {perVehicle.map((v, i) => (
                  <td key={i} className="r">
                    {v.maintGrowth > 0 ? `+${v.maintGrowth}%` : '—'}
                    {v.maintGrowth > 100 && <span style={{ fontSize: 10, color: 'var(--red)', marginLeft: 4 }}>⚠</span>}
                  </td>
                ))}
              </tr>
              {results.some((r) => !r.cash) && (
                <Fragment>
                  <tr>
                    <td>Loan Interest</td>
                    {results.map((r, i) => <td key={i} className="mono-r r">{r.cash ? '—' : fmt(r.totalInt)}</td>)}
                  </tr>
                  <tr>
                    <td>Interest % of TCO</td>
                    {results.map((r, i) => <td key={i} className="r">{r.cash ? '—' : `${pct(r.totalInt, r.tco)}%`}</td>)}
                  </tr>
                  <tr>
                    <td>EMI / month</td>
                    {results.map((r, i) => <td key={i} className="mono-r r">{r.cash ? '—' : fmt(r.emi)}</td>)}
                  </tr>
                </Fragment>
              )}
              <tr>
                <td>On-road Price</td>
                {results.map((r, i) => <td key={i} className="mono-r r">{fmt(r.onRoad)}</td>)}
              </tr>
              <tr>
                <td>Depreciation Loss</td>
                {results.map((r, i) => <td key={i} className="mono-r r">{fmt(r.depLoss)}</td>)}
              </tr>
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: 20 }}>
          <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 10 }}>Detailed Notes</h4>
          <div className="insights-list">
            {perVehicle.map((v) => v.maintGrowth > 100 && (
              <div key={`mw-${v.i}`} className="insight-card" style={{ background: 'rgba(232,89,12,0.08)' }}>
                <div className="insight-card-header">
                  <span className="insight-icon">⚠️</span>
                  <span className="insight-title" style={{ color: VCOLORS[v.i] }}>{v.label} — Maintenance Escalation</span>
                </div>
                <p className="insight-text">
                  Maintenance grows {v.maintGrowth}% from year 1 ({fmt(v.yr1?.maintYr)}) to year {numYears} ({fmt(v.lastYr?.maintYr)}).
                  By year {numYears}, maintenance is {pct(v.lastYr?.maintYr, v.lastYr?.yearCost)}% of annual running cost. Consider extended warranty.
                </p>
              </div>
            ))}
            {perVehicle.map((v) => v.fuelPct > 40 && (
              <div key={`fp-${v.i}`} className="insight-card" style={{ background: 'rgba(25,113,194,0.06)' }}>
                <div className="insight-card-header">
                  <span className="insight-icon">⛽</span>
                  <span className="insight-title" style={{ color: VCOLORS[v.i] }}>{v.label} — Fuel Dependency</span>
                </div>
                <p className="insight-text">
                  Fuel accounts for {v.fuelPct}% of TCO — consider CNG or EV alternatives for significant savings.
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  /* ── Single vehicle mode: card-based insights ── */
  const v = perVehicle[0]
  const typeIcons = { rating: '📊', analysis: '📈', warning: '⚠️', finance: '💰' }
  const typeBg = { rating: 'var(--s1)', analysis: 'rgba(25,113,194,0.06)', warning: 'rgba(232,89,12,0.08)', finance: 'rgba(156,54,181,0.06)' }

  const items = []
  items.push({
    type: 'rating', title: `Ownership Cost Rating: ${v.g}`,
    text: `${v.label} has a cost of ₹${v.r.cpkm}/km — rated "${gradeLabels[v.g]}". Net cost after resale is ${fmt(v.r.netCost)} over ${numYears} years.`,
    grade: v.g,
  })
  items.push({
    type: 'analysis', title: 'Cost Composition',
    text: `Fuel accounts for ${v.fuelPct}% of TCO. Maintenance is ${v.maintPct}%.${v.maintPct > 20 ? ' Maintenance burden is significant — consider extended warranty.' : ''}${v.fuelPct > 40 ? ' High fuel dependency — CNG or EV could save substantially.' : ''}`,
  })
  if (v.maintGrowth > 100) {
    items.push({
      type: 'warning', title: 'Maintenance Escalation',
      text: `Maintenance grows ${v.maintGrowth}% from year 1 (${fmt(v.yr1?.maintYr)}) to year ${numYears} (${fmt(v.lastYr?.maintYr)}). By year ${numYears}, maintenance is ${pct(v.lastYr?.maintYr, v.lastYr?.yearCost)}% of annual running cost.`,
    })
  }
  if (!v.r.cash && v.r.totalInt > 0) {
    items.push({
      type: 'finance', title: 'Financing Impact',
      text: `Loan interest adds ${fmt(v.r.totalInt)} (${pct(v.r.totalInt, v.r.tco)}% of TCO). Monthly EMI: ${fmt(v.r.emi)}.`,
    })
  }

  return (
    <div className="insights-list">
      {items.map((ins, idx) => (
        <div key={idx} className="insight-card" style={{ background: typeBg[ins.type] || 'var(--s1)' }}>
          <div className="insight-card-header">
            <span className="insight-icon">{typeIcons[ins.type]}</span>
            <span className="insight-title">{ins.title}</span>
            {ins.grade && <span className={`grade grade-${ins.grade}`}>{ins.grade}</span>}
          </div>
          <p className="insight-text">{ins.text}</p>
        </div>
      ))}
    </div>
  )
}

/* ═══════ Per-tab image download button ═══════ */
function DownloadTabImage({ contentRef, tabName, numYears }) {
  const [saving, setSaving] = useState(false)

  const handleDownload = async () => {
    if (!contentRef?.current || saving) return
    setSaving(true)
    try {
      const canvas = await html2canvas(contentRef.current, {
        scale: 2, useCORS: true, backgroundColor: '#f8f9fa', logging: false,
      })
      canvas.toBlob((blob) => {
        if (!blob) return
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `TCO-${tabName.replace(/[^a-zA-Z0-9]/g, '')}-${numYears}yr.png`
        a.click()
        URL.revokeObjectURL(url)
      }, 'image/png')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ marginTop: 20, textAlign: 'center' }}>
      <button type="button" className="btn-secondary" onClick={handleDownload} disabled={saving} style={{ gap: 6, display: 'inline-flex', alignItems: 'center' }}>
        {saving ? 'Saving...' : `Download "${tabName}" as Image`}
      </button>
    </div>
  )
}

/* ═══════ PDF Export — captures actual UI with html2canvas ═══════ */
async function generatePDFFromUI(setActiveTab, contentRef, numYears, results, setExporting) {
  setExporting(true)
  const savedTab = document.querySelector('.results-tab.active')?.textContent || ''
  const doc = new jsPDF('p', 'mm', 'a4')
  const pw = doc.internal.pageSize.getWidth()
  const ph = doc.internal.pageSize.getHeight()
  const margin = 8
  const usableW = pw - 2 * margin
  const usableH = ph - 20
  let isFirst = true

  const captureTab = async (tabIndex) => {
    setActiveTab(tabIndex)
    await new Promise((r) => setTimeout(r, 600))

    const el = contentRef.current
    if (!el) return
    const canvas = await html2canvas(el, {
      scale: 2, useCORS: true, backgroundColor: '#f8f9fa',
      windowWidth: el.scrollWidth, logging: false,
    })
    const imgData = canvas.toDataURL('image/png')
    const imgW = usableW
    const imgH = (canvas.height / canvas.width) * imgW
    let yOff = 0

    while (yOff < imgH) {
      if (!isFirst) doc.addPage()
      isFirst = false

      if (yOff === 0) {
        doc.setFontSize(7); doc.setFont('helvetica', 'bold'); doc.setTextColor('#d4a017')
        doc.text(`TCO Report — ${numYears} Years — ${TABS[tabIndex]}`, margin, 6)
        doc.setFontSize(6); doc.setFont('helvetica', 'normal'); doc.setTextColor('#868e96')
        doc.text(new Date().toLocaleDateString('en-IN'), pw - margin, 6, { align: 'right' })
      }

      const headerGap = yOff === 0 ? 4 : 0
      const sliceH = Math.min(usableH - headerGap, imgH - yOff)
      const srcY = (yOff / imgH) * canvas.height
      const srcH = (sliceH / imgH) * canvas.height

      const sliceCanvas = document.createElement('canvas')
      sliceCanvas.width = canvas.width
      sliceCanvas.height = Math.round(srcH)
      const ctx = sliceCanvas.getContext('2d')
      ctx.drawImage(canvas, 0, Math.round(srcY), canvas.width, Math.round(srcH), 0, 0, canvas.width, Math.round(srcH))

      doc.addImage(sliceCanvas.toDataURL('image/png'), 'PNG', margin, margin + headerGap, imgW, sliceH)

      doc.setFontSize(6); doc.setFont('helvetica', 'normal'); doc.setTextColor('#868e96')
      doc.text('TCO Calculator India — IRDAI · State Tax · Resale', margin, ph - 4)
      yOff += sliceH
    }
  }

  try {
    for (let t = 0; t < TABS.length; t++) {
      await captureTab(t)
    }
    const pageCount = doc.internal.getNumberOfPages()
    for (let p = 1; p <= pageCount; p++) {
      doc.setPage(p)
      doc.setFontSize(6); doc.setFont('helvetica', 'normal'); doc.setTextColor('#adb5bd')
      doc.text(`Page ${p} / ${pageCount}`, pw - margin, ph - 4, { align: 'right' })
    }
    doc.save(`TCO-Report-${numYears}yr.pdf`)
  } finally {
    const idx = TABS.indexOf(savedTab)
    setActiveTab(idx >= 0 ? idx : 0)
    setExporting(false)
  }
}

/* ═══════ Excel Export — single comprehensive sheet ═══════ */
function generateExcel(results, numYears) {
  const wb = XLSX.utils.book_new()
  const cats = getCats(results, numYears)
  const rows = []
  const merges = []
  let r = 0

  const push = (cells) => { rows.push(cells); r++ }
  const blank = () => push([])

  push(['4-Wheeler PV TCO Calculator — India'])
  push([`${numYears}-Year Report · Generated ${new Date().toLocaleDateString('en-IN')}`])
  blank()

  // ── Section: Vehicle Summary ──
  push(['VEHICLE SUMMARY'])
  const sumHeaders = ['', ...results.map((_, i) => `Vehicle ${i + 1}`)]
  push(sumHeaders)
  const sumFields = [
    ['Make', (rv) => rv.make || '—'], ['Model', (rv) => rv.model || '—'], ['Fuel', (rv) => rv.fuel],
    ['Ex-showroom (₹)', (rv) => rv.ex], ['On-road (₹)', (rv) => rv.onRoad], ['Total TCO (₹)', (rv) => rv.tco],
    ['Cost/km (₹)', (rv) => rv.cpkm], ['Net Cost/km (₹)', (rv) => rv.totalKm ? parseFloat((rv.netCost / rv.totalKm).toFixed(2)) : 0],
    ['Resale Value (₹)', (rv) => rv.residualN], ['Net Cost (₹)', (rv) => rv.netCost],
    ['Total km', (rv) => rv.totalKm], ['EMI/month (₹)', (rv) => rv.emi || 0],
  ]
  sumFields.forEach(([label, fn]) => push([label, ...results.map(fn)]))
  blank()

  // ── Section: Cost Breakdown ──
  push(['COST BREAKDOWN'])
  const bdHead = ['Category']
  results.forEach((_, i) => { bdHead.push(`V${i + 1} Amount (₹)`); bdHead.push(`V${i + 1} % of TCO`) })
  push(bdHead)
  cats.forEach((cat) => {
    const row = [cat.label]
    results.forEach((rv) => { row.push(cat.get(rv)); row.push(parseFloat(pct(cat.get(rv), rv.tco))) })
    push(row)
  })
  const totRow = ['TOTAL TCO']; results.forEach((rv) => { totRow.push(rv.tco); totRow.push(100) }); push(totRow)
  const resRow = ['Resale Value']; results.forEach((rv) => { resRow.push(rv.residualN); resRow.push(parseFloat(pct(rv.residualN, rv.tco))) }); push(resRow)
  const netRow = ['Net Cost (TCO - Resale)']; results.forEach((rv) => { netRow.push(rv.netCost); netRow.push('') }); push(netRow)
  blank()

  // ── Section: Year-by-Year per vehicle ──
  results.forEach((rv, vi) => {
    push([`YEAR-BY-YEAR: V${vi + 1} ${rv.make || ''} ${rv.model || ''} (${rv.fuel})`])
    push(['Year', 'Year Cost', 'Cumulative', 'Resale %', 'Resale Value', 'Ann. Depreciation', 'Net Cost', '₹/km', 'Insurance', 'Maintenance', 'Fuel', 'Tyres', 'Battery'])
    ;(rv.yearByYear || []).forEach((y, yi) => {
      const prevResale = yi > 0 ? (rv.resalePerYear?.[yi - 1] || 0) : rv.ex
      push([y.yr, y.yearCost, y.cumCost, y.resalePct, y.resaleVal, prevResale - (rv.resalePerYear?.[yi] || 0), y.netCost, y.cpkm, y.insYr, y.maintYr, y.fuelAnn, y.tyreYr, y.battYr])
    })
    blank()
  })

  // ── Section: Resale Schedule (15yr) ──
  push(['RESALE SCHEDULE — 15 YEAR PROJECTION'])
  const rsHead = ['Year']; results.forEach((_, i) => { rsHead.push(`V${i + 1} Resale %`); rsHead.push(`V${i + 1} Resale (₹)`) })
  push(rsHead)
  for (let yi = 0; yi < 15; yi++) {
    const row = [yi + 1]
    results.forEach((rv) => {
      row.push(rv._resaleArr?.[yi] ? parseFloat((rv._resaleArr[yi] * 100).toFixed(1)) : '')
      row.push(rv.resalePerYear?.[yi] || '')
    })
    push(row)
  }
  blank()

  // ── Section: Assumptions ──
  push(['ASSUMPTIONS & INPUT PARAMETERS'])
  const aHead = ['Parameter', ...results.map((_, i) => `Vehicle ${i + 1}`)]
  push(aHead)
  const aFields = [
    ['State', (rv) => rv.state], ['Mileage', (rv) => rv._mil], ['Fuel Price (₹)', (rv) => rv._fprice],
    ['Annual km', (rv) => rv._annKm], ['Fuel Escalation %', (rv) => rv._fuelEscalPct || 5],
    ['Engine Class', (rv) => rv._eng], ['Tyre Cycle (yr)', (rv) => rv._tyreCycleYrs],
    ['Tyre Cost (₹)', (rv) => rv._tyreSetCost], ['Cash Purchase', (rv) => rv.cash ? 'Yes' : 'No'],
    ['Down Payment (₹)', (rv) => rv.dp || 0], ['Loan (₹)', (rv) => rv.loanAmt || 0],
    ['Tenure (months)', (rv) => rv.tenure || 0], ['Interest Rate %', (rv) => rv.ir || 0],
  ]
  aFields.forEach(([label, fn]) => push([label, ...results.map(fn)]))

  const ws = XLSX.utils.aoa_to_sheet(rows)

  const maxCols = Math.max(...rows.map((row) => row.length))
  ws['!cols'] = Array.from({ length: maxCols }, (_, i) => ({ wch: i === 0 ? 24 : 16 }))

  XLSX.utils.book_append_sheet(wb, ws, 'TCO Report')
  XLSX.writeFile(wb, `TCO-Report-${numYears}yr.xlsx`)
}

/* ═══════ Export Bar ═══════ */
function ExportBar({ results, numYears, setActiveTab, contentRef, setExporting, exporting }) {
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      <button type="button" className="btn-secondary" disabled={exporting} onClick={() => generatePDFFromUI(setActiveTab, contentRef, numYears, results, setExporting)}>
        {exporting ? 'Generating...' : 'PDF Report'}
      </button>
      <button type="button" className="btn-secondary" onClick={() => generateExcel(results, numYears)}>Excel</button>
    </div>
  )
}

/* ═══════ Main Results Page ═══════ */
export default function ResultsPage({ results, numYears, onBack }) {
  const [activeTab, setActiveTab] = useState(0)
  const [exporting, setExporting] = useState(false)
  const summaryRef = useRef(null)
  const contentRef = useRef(null)

  if (!results || !results.length) return null

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 clamp(10px, 3vw, 20px) 80px', position: 'relative' }}>
      {exporting && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(255,255,255,0.85)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12 }}>
          <div style={{ width: 40, height: 40, border: '3px solid var(--s2)', borderTopColor: 'var(--acc)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
          <p style={{ fontWeight: 600, color: 'var(--t2)' }}>Generating PDF — capturing all tabs...</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
        </div>
      )}

      <div className="results-header">
        <button type="button" className="btn-secondary" onClick={onBack} style={{ padding: '8px 16px' }}>← Back</button>
        <div className="results-tabs">
          {TABS.map((tab, i) => (
            <button key={tab} type="button" className={`results-tab${i === activeTab ? ' active' : ''}`} onClick={() => setActiveTab(i)}>{tab}</button>
          ))}
        </div>
        <ExportBar results={results} numYears={numYears} setActiveTab={setActiveTab} contentRef={contentRef} setExporting={setExporting} exporting={exporting} />
      </div>

      <div ref={contentRef} style={{ marginTop: 20 }}>
        {activeTab === 0 && <SummaryTab results={results} numYears={numYears} summaryRef={summaryRef} />}
        {activeTab === 1 && <CostAnalysisTab results={results} numYears={numYears} />}
        {activeTab === 2 && <ResaleDepTab results={results} numYears={numYears} />}
        {activeTab === 3 && <YearByYearTab results={results} numYears={numYears} />}
        {activeTab === 4 && <InsightsTab results={results} numYears={numYears} />}
      </div>
      <DownloadTabImage contentRef={contentRef} tabName={TABS[activeTab]} numYears={numYears} />
    </div>
  )
}
