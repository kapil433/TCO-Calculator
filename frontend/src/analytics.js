/**
 * Google Analytics 4 + custom event tracking for TCO Calculator.
 * GA script loads from index.html (G-FV2JJFMKN3). This module ensures gtag exists for custom events.
 */

const GA_ID = import.meta.env.VITE_GA_ID || 'G-FV2JJFMKN3'

export function initGA() {
  window.dataLayer = window.dataLayer || []
  if (!window.gtag) {
    window.gtag = function () { window.dataLayer.push(arguments) }
  }
  window.gtag('config', GA_ID, { send_page_view: true })
}

function send(eventName, params = {}) {
  if (window.gtag) {
    window.gtag('event', eventName, params)
  }
}

export function trackCalculate(vehicles, numYears) {
  const labels = vehicles.map((v) =>
    [v.make, v.model, v.fuel].filter(Boolean).join(' ')
  )
  send('calculate_tco', {
    vehicle_count: vehicles.length,
    num_years: numYears,
    vehicles: labels.join(' | '),
  })
}

export function trackCompareMode(count) {
  send('compare_mode', { vehicle_count: count })
}

export function trackExport(format) {
  send('export_report', { format })
}

export function trackTabView(tabName) {
  send('view_tab', { tab: tabName })
}

export function trackWizardStep(step, label) {
  send('wizard_step', { step, label })
}

export function trackStepField(field, value) {
  send('input_field', { field, value: String(value).slice(0, 50) })
}
