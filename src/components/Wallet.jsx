import React, { useState } from 'react'

function Wallet() {
  const [credential, setCredential] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [profileIndex, setProfileIndex] = useState(0)

  const handleIssueCredential = async () => {
    setLoading(true)
    setError(null)
    setCredential(null)

    try {
      const response = await fetch(`http://localhost:3000/issue?profile=${profileIndex}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setCredential(data)
    } catch (err) {
      setError(err.message || 'Failed to issue credential')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>VC Identity Wallet</h1>
      
      <div style={styles.controls}>
        <label style={styles.label}>
          Profile Index:
          <input
            type="number"
            value={profileIndex}
            onChange={(e) => setProfileIndex(parseInt(e.target.value) || 0)}
            min="0"
            style={styles.input}
          />
        </label>
        
        <button
          onClick={handleIssueCredential}
          disabled={loading}
          style={{
            ...styles.button,
            ...(loading ? styles.buttonDisabled : {}),
          }}
        >
          {loading ? 'Issuing...' : 'Issue Credential'}
        </button>
      </div>

      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {credential && (
        <div style={styles.credentialContainer}>
          <h2 style={styles.sectionTitle}>Issued Credential</h2>
          
          <div style={styles.profileSection}>
            <h3 style={styles.subtitle}>Profile</h3>
            <div style={styles.profileInfo}>
              <p><strong>Name:</strong> {credential.profile.name}</p>
              <p><strong>Date of Birth:</strong> {credential.profile.dob}</p>
              <p><strong>Credit Score:</strong> {credential.profile.creditScore}</p>
            </div>
          </div>

          <div style={styles.credentialSection}>
            <h3 style={styles.subtitle}>Verifiable Credential</h3>
            <pre style={styles.json}>
              {JSON.stringify(credential.credential, null, 2)}
            </pre>
          </div>
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
    marginBottom: '2rem',
    color: '#333',
    textAlign: 'center',
  },
  controls: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '2rem',
    flexWrap: 'wrap',
  },
  label: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    fontSize: '1rem',
    fontWeight: '500',
  },
  input: {
    padding: '0.5rem',
    fontSize: '1rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: '80px',
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
  credentialContainer: {
    marginTop: '2rem',
    padding: '1.5rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #dee2e6',
  },
  sectionTitle: {
    fontSize: '1.5rem',
    marginBottom: '1rem',
    color: '#333',
  },
  subtitle: {
    fontSize: '1.2rem',
    marginBottom: '0.75rem',
    color: '#555',
  },
  profileSection: {
    marginBottom: '2rem',
    padding: '1rem',
    backgroundColor: 'white',
    borderRadius: '6px',
    border: '1px solid #dee2e6',
  },
  profileInfo: {
    lineHeight: '1.8',
  },
  credentialSection: {
    padding: '1rem',
    backgroundColor: 'white',
    borderRadius: '6px',
    border: '1px solid #dee2e6',
  },
  json: {
    backgroundColor: '#f8f9fa',
    padding: '1rem',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '0.875rem',
    lineHeight: '1.5',
    border: '1px solid #dee2e6',
    maxHeight: '600px',
  },
}

export default Wallet

