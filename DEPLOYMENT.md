# Deployment Guide

## Deploy to Firebase Hosting

### Prerequisites
1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Firebase Hosting in your project

### Steps

1. **Login to Firebase** (in Cursor's terminal):
```bash
npx firebase-tools login
```
- When prompted about Gemini, type `Y` or `N` and press Enter
- A browser window will open - sign in with your Google account

2. **Initialize Firebase Hosting** (if needed):
```bash
npx firebase init hosting
```
Select options:
- Public directory: `dist`
- Configure as SPA: Yes
- Set up auto-deploy: No

3. **Deploy**:
```bash
npm run deploy
```

Or manually:
```bash
npm run build
npx firebase deploy
```

### After Deployment

Your app will be live at:
- `https://vc-identity-pilot.web.app`
- `https://vc-identity-pilot.firebaseapp.com`

### Testing the Deployed App

1. Start your local API server:
```bash
npm start
```

2. Visit your deployed URL in a browser

3. You should see the "Demo Mode" message indicating the wallet is deployed

4. Click "Issue Credential" - it will try to connect to your local API at `localhost:3000`

Note: For production use, you'll need to deploy your API server as well (to Cloud Functions, Heroku, Railway, etc.)

