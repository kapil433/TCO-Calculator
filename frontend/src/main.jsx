import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { initGA } from './analytics'

initGA()

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null } }
  static getDerivedStateFromError(error) { return { hasError: true, error } }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ maxWidth: 600, margin: '80px auto', padding: 32, textAlign: 'center', fontFamily: 'system-ui' }}>
          <h1 style={{ fontSize: 22, marginBottom: 12 }}>Something went wrong</h1>
          <p style={{ color: '#666', marginBottom: 16 }}>The calculator encountered an unexpected error.</p>
          <p style={{ fontSize: 12, color: '#999', marginBottom: 20 }}>{String(this.state.error)}</p>
          <button onClick={() => window.location.reload()} style={{ padding: '10px 24px', fontSize: 14, cursor: 'pointer', borderRadius: 6, border: '1px solid #ccc', background: '#f8f9fa' }}>
            Reload App
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
