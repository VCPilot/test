# API Deployment Guide

## Current Status

✅ **Frontend deployed**: https://vc-identity-pilot-4b7b9.web.app

⚠️ **API deployment**: Requires Firebase Blaze plan (upgrade needed)

## Two Options for API

### Option 1: Local API Server (Works Now)
Run the API locally on your machine:

1. Start the API server:
   ```bash
   npm start
   # or: node server.js
   ```

2. Visit https://vc-identity-pilot-4b7b9.web.app

3. The wallet will try to connect to the API at `/api` (which will fail because Functions aren't deployed)

4. You'll see a message saying "API not reachable" - this is expected

**Note**: The deployed wallet can't reach localhost from your browser. This option only works if you run the wallet locally at `http://localhost:3001`.

### Option 2: Deploy API to Firebase Functions (Requires Upgrade)

To enable the API on the deployed site:

1. **Upgrade to Blaze plan**:
   - Visit: https://console.firebase.google.com/project/vc-identity-pilot-4b7b9/usage/details
   - Click "Upgrade" to Blaze (pay-as-you-go)
   - Note: Free tier includes 2 million function invocations/month

2. **Deploy Functions**:
   ```bash
   npx firebase deploy --only functions
   ```

3. **The API will be available at**: 
   - https://vc-identity-pilot-4b7b9.web.app/api/issue
   - https://vc-identity-pilot-4b7b9.web.app/api/health

4. Visit https://vc-identity-pilot-4b7b9.web.app and click "Issue Credential"

## File Structure

```
VC Identity Pilot/
├── functions/
│   ├── index.js          # Express API as Firebase Function
│   └── package.json      # Functions dependencies
├── src/
│   └── components/
│       └── Wallet.jsx    # Detects local vs deployed, uses appropriate API URL
├── server.js             # Local Express server
└── firebase.json         # Configured with functions and hosting rewrites
```

## How It Works

The Wallet component automatically detects whether it's running:
- **Locally** (`localhost:3001`): Calls `http://localhost:3000`
- **Deployed** (Firebase Hosting): Calls `window.location.origin + '/api'`

The `/api` path is rewritten by Firebase Hosting to invoke the `api` Cloud Function.

## Testing Locally

1. **Terminal 1**: Start the local API
   ```bash
   npm start
   ```

2. **Terminal 2**: Start the local frontend
   ```bash
   npm run client
   ```

3. Visit: http://localhost:3001

## Alternative: Deploy API to Railway/Render

If you prefer not to upgrade Firebase, you can deploy the API separately:

1. Sign up for Railway (https://railway.app) or Render (https://render.com)

2. Connect your GitHub repo

3. Deploy `server.js` as a web service

4. Update the Wallet component to use your deployment URL:
   ```javascript
   const API_URL = isLocal ? 'http://localhost:3000' : 'https://your-api-url.railway.app'
   ```

5. Redeploy the frontend

## Support

For questions or issues, check the Firebase Console:
https://console.firebase.google.com/project/vc-identity-pilot-4b7b9/overview

