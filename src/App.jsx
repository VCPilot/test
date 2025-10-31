import { useState, useEffect } from 'react'
import Wallet from './components/Wallet'
import Verify from './components/Verify'

function App() {
  const [currentPage, setCurrentPage] = useState('wallet')

  // Listen for navigation events from Wallet
  useEffect(() => {
    const handleNavigateToVerify = () => {
      setCurrentPage('verify')
    }
    
    window.addEventListener('navigateToVerify', handleNavigateToVerify)
    return () => window.removeEventListener('navigateToVerify', handleNavigateToVerify)
  }, [])

  return (
    <div className="App" style={{ minHeight: '100vh', padding: '20px' }}>
      {/* Navigation */}
      <nav style={styles.nav}>
        <button
          onClick={() => setCurrentPage('wallet')}
          style={{
            ...styles.navButton,
            ...(currentPage === 'wallet' ? styles.navButtonActive : {}),
          }}
        >
          Wallet
        </button>
        <button
          onClick={() => setCurrentPage('verify')}
          style={{
            ...styles.navButton,
            ...(currentPage === 'verify' ? styles.navButtonActive : {}),
          }}
        >
          Verify
        </button>
      </nav>

      {/* Page Content */}
      {currentPage === 'wallet' && <Wallet />}
      {currentPage === 'verify' && <Verify />}
    </div>
  )
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1rem',
    marginBottom: '2rem',
    paddingBottom: '1rem',
    borderBottom: '2px solid #e5e7eb',
  },
  navButton: {
    padding: '0.75rem 2rem',
    fontSize: '1rem',
    fontWeight: '600',
    backgroundColor: '#f8f9fa',
    color: '#333',
    border: '2px solid #e5e7eb',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  navButtonActive: {
    backgroundColor: '#007bff',
    color: 'white',
    borderColor: '#007bff',
  },
}

export default App

