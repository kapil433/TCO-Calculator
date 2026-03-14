import { useState } from 'react'
import { trackWizardStep } from '../analytics'

const STEP_LABELS = [
  'State & Period',
  'Vehicle',
  'Tax & On-Road',
  'Financing',
  'Insurance',
  'Running Cost',
  'Maintenance',
]

export default function WizardLayout({ children, onCalculate, loading }) {
  const [step, setStep] = useState(0)
  const totalSteps = STEP_LABELS.length

  const steps = Array.isArray(children) ? children : [children]

  return (
    <div className="wizard">
      <div className="wizard-indicator">
        {STEP_LABELS.map((label, i) => (
          <button
            key={i}
            type="button"
            className={`wizard-dot${i === step ? ' active' : ''}${i < step ? ' done' : ''}`}
            onClick={() => setStep(i)}
            title={label}
          >
            <span className="wizard-dot-num">{i < step ? '✓' : i + 1}</span>
            <span className="wizard-dot-label">{label}</span>
          </button>
        ))}
      </div>

      <div className="wizard-body">
        {steps[step] || null}
      </div>

      <div className="wizard-nav">
        <button
          type="button"
          className="btn-secondary"
          disabled={step === 0}
          onClick={() => setStep(step - 1)}
          style={{ visibility: step === 0 ? 'hidden' : 'visible', padding: '10px 16px', minHeight: 44 }}
        >
          Back
        </button>

        <span style={{ fontSize: 12, color: 'var(--t3)', whiteSpace: 'nowrap' }}>
          {step + 1} / {totalSteps}
        </span>

        {step < totalSteps - 1 ? (
          <button
            type="button"
            className="btn-primary"
            style={{ width: 'auto', padding: '12px 32px', minHeight: 44 }}
            onClick={() => { const next = step + 1; setStep(next); trackWizardStep(next, STEP_LABELS[next]) }}
          >
            Next
          </button>
        ) : (
          <button
            type="button"
            className="btn-primary"
            style={{ width: 'auto', padding: '12px 24px', minHeight: 44 }}
            onClick={onCalculate}
            disabled={loading}
          >
            {loading ? 'Calculating...' : 'Calculate TCO'}
          </button>
        )}
      </div>
    </div>
  )
}
