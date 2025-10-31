import React, { useState } from 'react'

// Determine if we're running locally or deployed
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const API_URL = isLocal ? 'http://localhost:3000' : window.location.origin + '/api'

function Verify() {
  const [credentialJson, setCredentialJson] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleVerify = async () => {
    if (!credentialJson.trim()) {
      setError('Please paste a credential JSON')
      return
    }

    setLoading(true)
    setError(null)
    setVerificationResult(null)

    try {
      // Parse to make sure it's valid JSON
      const parsedCredential = JSON.parse(credentialJson)

      // Call verify endpoint
      const response = await fetch(`${API_URL}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedCredential),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setVerificationResult(result)
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON. Please check your credential format.')
      } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        setError('Cannot connect to API server. Is your local server running on port 3000?')
      } else {
        setError(err.message || 'Failed to verify credential')
      }
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Verify Credential</h1>

      {!isLocal && (
        <div style={styles.apiWarning}>
          <strong>💡 Demo Mode:</strong> This wallet is deployed on Firebase.
          <br />
          <strong>⚠️ To verify credentials:</strong> You need to run the local API server.
          <br />
          Clone the repo and run <code>npm start</code> in a terminal to start the API on <code>localhost:3000</code>
        </div>
      )}

      <div style={styles.inputSection}>
        <label style={styles.label}>
          Paste Credential JSON:
        </label>
        <textarea
          value={credentialJson}
          onChange={(e) => setCredentialJson(e.target.value)}
          placeholder='Paste your credential JSON here...'
          style={styles.textarea}
          rows={15}
        />
      </div>

      <button
        onClick={handleVerify}
        disabled={loading}
        style={{
          ...styles.button,
          ...(loading ? styles.buttonDisabled : {}),
        }}
      >
        {loading ? 'Verifying...' : 'Check Validity'}
      </button>

      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {verificationResult && (
        <div style={styles.resultSection}>
          <h2 style={styles.resultTitle}>Verification Result</h2>
          
          <div style={{
            ...styles.statusBadge,
            backgroundColor: verificationResult.verified ? '#10b981' : '#ef4444',
          }}>
            {verificationResult.verified ? '✓ Valid' : '✗ Invalid'}
          </div>

          <div style={styles.resultMessage}>
            {verificationResult.message || (verificationResult.verified ? 'Credential is valid' : 'Credential is invalid')}
          </div>

          {verificationResult.checks && (
            <details style={styles.details}>
              <summary style={styles.detailsSummary}>View Detailed Checks</summary>
              <div style={styles.checksGrid}>
                {Object.entries(verificationResult.checks).map(([key, value]) => (
                  <div key={key} style={styles.checkItem}>
                    <span style={styles.checkKey}>{key}:</span>
                    <span style={value ? styles.checkPass : styles.checkFail}>
                      {value ? '✓' : '✗'}
                    </span>
                  </div>
                ))}
              </div>
            </details>
          )}

          {verificationResult.issuer && (
            <div style={styles.issuerInfo}>
              <strong>Issuer:</strong> {verificationResult.issuer}
            </div>
          )}

          <details style={styles.details}>
            <summary style={styles.detailsSummary}>View Full Response</summary>
            <pre style={styles.json}>
              {JSON.stringify(verificationResult, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#333',
    textAlign: 'center',
  },
  apiWarning: {
    padding: '1rem 1.5rem',
    backgroundColor: '#fff4e6',
    color: '#856404',
    borderRadius: '6px',
    marginBottom: '2rem',
    border: '1px solid #ffe8cc',
    textAlign: 'center',
    fontSize: '0.95rem',
  },
  inputSection: {
    marginBottom: '1.5rem',
  },
  label: {
    display: 'block',
    fontSize: '1rem',
    fontWeight: '600',
    marginBottom: '0.5rem',
    color: '#333',
  },
  textarea: {
    width: '100%',
    padding: '1rem',
    fontSize: '0.95rem',
    fontFamily: 'monospace',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    resize: 'vertical',
    minHeight: '200px',
  },
  button: {
    padding: '0.75rem 2rem',
    fontSize: '1rem',
    fontWeight: '600',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    display: 'block',
    margin: '0 auto 2rem',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  error: {
    padding: '1rem',
    backgroundColor: '#fee',
    color: '#c33',
    borderRadius: '6px',
    marginBottom: '1rem',
    border: '1px solid #fcc',
  },
  resultSection: {
    marginTop: '2rem',
    padding: '2rem',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
    border: '1px solid #e5e7eb',
  },
  resultTitle: {
    fontSize: '1.5rem',
    marginBottom: '1.5rem',
    color: '#333',
    textAlign: 'center',
  },
  statusBadge: {
    padding: '1rem 2rem',
    borderRadius: '8px',
    fontSize: '1.5rem',
    fontWeight: '700',
    color: 'white',
    textAlign: 'center',
    marginBottom: '1rem',
  },
  resultMessage: {
    fontSize: '1.1rem',
    textAlign: 'center',
    color: '#333',
    marginBottom: '1.5rem',
  },
  checksGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '0.75rem',
    marginTop: '1rem',
  },
  checkItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0.5rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '4px',
  },
  checkKey: {
    fontSize: '0.9rem',
    color: '#666',
    fontFamily: 'monospace',
  },
  checkPass: {
    fontSize: '1.2rem',
    color: '#10b981',
  },
  checkFail: {
    fontSize: '1.2rem',
    color: '#ef4444',
  },
  issuerInfo: {
    padding: '1rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '6px',
    marginTop: '1rem',
    fontSize: '0.95rem',
    wordBreak: 'break-word',
  },
  details: {
    marginTop: '1.5rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #dee2e6',
    padding: '1rem',
  },
  detailsSummary: {
    cursor: 'pointer',
    fontWeight: '600',
    color: '#007bff',
    marginBottom: '0.5rem',
    userSelect: 'none',
  },
  json: {
    backgroundColor: 'white',
    padding: '1rem',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '0.875rem',
    lineHeight: '1.5',
    border: '1px solid #dee2e6',
    maxHeight: '400px',
  },
}

export default Verify

