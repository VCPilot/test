import { initializeApp } from 'firebase/app'
import { getFirestore } from 'firebase/firestore'

// Firebase configuration
// TODO: Replace with your Firebase project config
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "your-api-key",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "your-project.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "vc-identity-pilot",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "your-project.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "your-app-id"
}

// Initialize Firebase with error handling
let app = null
let db = null

try {
  app = initializeApp(firebaseConfig)
  db = getFirestore(app)
  console.log('Firebase initialized successfully')
} catch (error) {
  console.warn('Firebase initialization failed:', error)
  console.warn('App will continue without Firestore. Configure Firebase to enable saving credentials.')
}

export { db }
export default app

