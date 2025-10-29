import React, { useState } from 'react'
import { db } from '../firebase'
import { collection, addDoc, Timestamp } from 'firebase/firestore'

function Wallet() {
  const [credential, setCredential] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [profileIndex, setProfileIndex] = useState(0)

  const handleIssueCredential = async () => {
    setLoading(true)
    setError(null)
    setCredential(null)
    setSaveSuccess(false)

    try {
      // Call local backend directly
      const url = profileIndex > 0 
        ? `http://localhost:3000/issue?profile=${profileIndex}`
        : `http://localhost:3000/issue`
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setCredential(data)
      
      // Save credential to Firestore
      await saveToFirestore(data.credential)
    } catch (err) {
      setError(err.message || 'Failed to issue credential')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const saveToFirestore = async (credentialJson) => {
    try {
      setSaving(true)
      setSaveSuccess(false)
      
      await addDoc(collection(db, 'credentials'), {
        credential: credentialJson,
        issuedAt: Timestamp.now(),
        issuer: credentialJson.issuer,
        subjectId: credentialJson.credentialSubject?.id,
        createdAt: new Date().toISOString()
      })
      
      setSaveSuccess(true)
      console.log('Credential saved to Firestore')
    } catch (err) {
      console.error('Error saving to Firestore:', err)
      setError(`Failed to save to Firestore: ${err.message}`)
    } finally {
      setSaving(false)
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

      {saving && (
        <div style={styles.savingMessage}>
          Saving credential to Firestore...
        </div>
      )}

      {saveSuccess && (
        <div style={styles.successMessage}>
          ✓ Credential saved to Firestore successfully!
        </div>
      )}

      {credential && (
        <div style={styles.credentialContainer}>
          <h2 style={styles.sectionTitle}>Issued Credential</h2>
          
          {/* Credential Card */}
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h3 style={styles.cardTitle}>Identity Credential</h3>
              <div style={styles.cardBadge}>Verified</div>
            </div>
            
            <div style={styles.cardBody}>
              <div style={styles.cardField}>
                <div style={styles.cardLabel}>Name</div>
                <div style={styles.cardValue}>{credential.profile.name}</div>
              </div>
              
              <div style={styles.cardField}>
                <div style={styles.cardLabel}>Date of Birth</div>
                <div style={styles.cardValue}>{credential.profile.dob}</div>
              </div>
              
              <div style={styles.cardField}>
                <div style={styles.cardLabel}>Credit Score</div>
                <div style={styles.cardScore}>{credential.profile.creditScore}</div>
              </div>
            </div>
            
            <div style={styles.cardFooter}>
              <div style={styles.cardIssuer}>
                Issued by: {credential.credential.issuer}
              </div>
              <div style={styles.cardDate}>
                {new Date(credential.credential.issuanceDate).toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Credential JSON (collapsible) */}
          <details style={styles.details}>
            <summary style={styles.detailsSummary}>View Credential JSON</summary>
            <pre style={styles.json}>
              {JSON.stringify(credential.credential, null, 2)}
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
  savingMessage: {
    padding: '1rem',
    backgroundColor: '#e7f3ff',
    color: '#0066cc',
    borderRadius: '6px',
    marginBottom: '1rem',
    border: '1px solid #b3d9ff',
    textAlign: 'center',
  },
  successMessage: {
    padding: '1rem',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '6px',
    marginBottom: '1rem',
    border: '1px solid #c3e6cb',
    textAlign: 'center',
    fontWeight: '600',
  },
  credentialContainer: {
    marginTop: '2rem',
  },
  sectionTitle: {
    fontSize: '1.5rem',
    marginBottom: '1.5rem',
    color: '#333',
    textAlign: 'center',
  },
  // Card styles
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
    border: '1px solid #e5e7eb',
    overflow: 'hidden',
    marginBottom: '1.5rem',
    maxWidth: '600px',
    margin: '0 auto 1.5rem',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem',
    backgroundColor: '#f8f9fa',
    borderBottom: '2px solid #e5e7eb',
  },
  cardTitle: {
    fontSize: '1.25rem',
    fontWeight: '700',
    color: '#1f2937',
    margin: 0,
  },
  cardBadge: {
    padding: '0.25rem 0.75rem',
    backgroundColor: '#10b981',
    color: 'white',
    borderRadius: '20px',
    fontSize: '0.75rem',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  cardBody: {
    padding: '2rem',
  },
  cardField: {
    marginBottom: '1.5rem',
    paddingBottom: '1.5rem',
    borderBottom: '1px solid #f3f4f6',
  },
  cardLabel: {
    fontSize: '0.875rem',
    color: '#6b7280',
    fontWeight: '500',
    marginBottom: '0.5rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  cardValue: {
    fontSize: '1.25rem',
    color: '#111827',
    fontWeight: '600',
  },
  cardScore: {
    fontSize: '2rem',
    color: '#059669',
    fontWeight: '700',
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 1.5rem',
    backgroundColor: '#f9fafb',
    borderTop: '1px solid #e5e7eb',
    fontSize: '0.875rem',
    color: '#6b7280',
  },
  cardIssuer: {
    fontWeight: '500',
  },
  cardDate: {
    color: '#9ca3af',
  },
  details: {
    marginTop: '1rem',
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

