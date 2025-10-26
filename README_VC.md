# VC Identity Pilot

A Node.js Express application for issuing Verifiable Credentials (W3C format) using the Veramo library.

## Features

- Issues W3C Verifiable Credentials from synthetic profiles
- Uses Veramo library for credential issuance and signing
- Local signing key management
- Express REST API

## Prerequisites

- Node.js v22.21.0 or higher
- npm

## Installation

1. Install dependencies:
```bash
npm install
```

## Usage

### Start the server

```bash
npm start
# or for development with auto-reload
npm run dev
```

The server will start on `http://localhost:3000`

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

- `POST /issue` - Issue a Verifiable Credential
  - Query parameter: `index` (optional, default: 0) - Profile index from synthetic_profiles.json
  
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
