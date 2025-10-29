# VC Identity Pilot

A Node.js Express API with a React front-end for issuing Verifiable Credentials (W3C format).

## Features

- Issues W3C Verifiable Credentials from synthetic profiles
- Express REST API backend
- React Wallet front-end with credential card display
- Firestore integration for saving credentials
- CORS support for cross-origin requests

## Prerequisites

- Node.js v22.21.0 or higher
- npm
- Firebase project (for Firestore integration)

## Installation

1. Install dependencies:
```bash
npm install
```

## Firebase Setup

1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Firestore Database in your Firebase project
3. Create a `.env` file in the project root with your Firebase configuration:
```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```
4. Get these values from: Firebase Console → Project Settings → General → Your apps
5. Update `src/firebase.js` with your Firebase configuration or use environment variables

## Usage

### Start the Backend Server

In one terminal, start the Express API server:

```bash
npm start
# or for development with auto-reload
npm run dev
```

The server will start on `http://localhost:3000`

### Start the React Front-end (Wallet)

In another terminal, start the React development server:

```bash
npm run client
```

The Wallet will be available at `http://localhost:3001`

The Wallet includes:
- A button to "Issue Credential"
- Profile index selector
- **Credential Card Display**: Shows name, date of birth, and credit score in a formatted card
- **Firestore Integration**: Automatically saves credential JSON to Firestore when issued
- Collapsible JSON view for full credential details

### Issue a Verifiable Credential

Issue a credential for the first profile (index 0):
```bash
curl -X POST http://localhost:3000/issue
```

Issue a credential for a specific profile (e.g., index 1):
```bash
curl -X POST "http://localhost:3000/issue?index=1"
```

### Health Check

Check if the server is running:
```bash
curl http://localhost:3000/health
```

## API Endpoints

- `GET /issue` or `POST /issue` - Issue a Verifiable Credential
  - Query parameters: 
    - `profile` or `index` (optional, default: 0) - Profile index from synthetic_profiles.json
  
- `GET /health` - Health check endpoint

## Verifiable Credential Format

The issued credentials follow the W3C Verifiable Credentials standard with:
- Context: `https://www.w3.org/2018/credentials/v1`
- Type: `VerifiableCredential`, `IdentityCredential`
- Credential Subject: Contains profile data (name, dob, creditScore)
- Proof: JWT format

## Files

- `server.js` - Main Express server
- `synthetic_profiles.json` - Synthetic profile data
- `package.json` - Dependencies and scripts

## License

MIT
