# VC Identity Pilot

A Node.js Express API with a React front-end for issuing Verifiable Credentials (W3C format).

## Features

- Issues W3C Verifiable Credentials from synthetic profiles
- Express REST API backend
- React Wallet front-end with credential display
- CORS support for cross-origin requests

## Prerequisites

- Node.js v22.21.0 or higher
- npm

## Installation

1. Install dependencies:
```bash
npm install
```

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
- Display of the returned credential in JSON format

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
