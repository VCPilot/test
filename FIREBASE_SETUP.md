# Firebase Configuration Guide

This guide will help you configure Firebase Firestore so that credentials can be saved.

## Step 1: Get Your Firebase Config

1. Open your Firebase Console:
   https://console.firebase.google.com/project/vc-identity-pilot-4b7b9

2. Click the **gear icon** ⚙️ in the top left, then click **"Project settings"**

3. Scroll down to the **"Your apps"** section

4. If you don't see a web app yet, click **"Add app"** and select the **Web** icon `</>`

5. Give your app a name (e.g., "VC Identity Pilot") and register it

6. You'll see a code snippet that looks like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX",
     authDomain: "vc-identity-pilot-4b7b9.firebaseapp.com",
     projectId: "vc-identity-pilot-4b7b9",
     storageBucket: "vc-identity-pilot-4b7b9.appspot.com",
     messagingSenderId: "123456789012",
     appId: "1:123456789012:web:abcdef123456"
   };
   ```

7. **Copy these values** - you'll need them in the next step

## Step 2: Enable Firestore

1. In the Firebase Console, go to **"Firestore Database"** in the left sidebar

2. Click **"Create database"**

3. Choose **"Start in test mode"** (we can add security rules later)

4. Select a **location** for your database (choose the closest to you)

5. Click **"Enable"**

## Step 3: Create Environment File

1. In your project root directory, create a file named `.env.local`

2. Add your Firebase config values with this format:
   ```bash
   VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX
   VITE_FIREBASE_AUTH_DOMAIN=vc-identity-pilot-4b7b9.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=vc-identity-pilot-4b7b9
   VITE_FIREBASE_STORAGE_BUCKET=vc-identity-pilot-4b7b9.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
   VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
   ```

3. Replace the values with your actual values from Step 1

4. **Important**: `.env.local` is already in `.gitignore`, so your API keys won't be committed to GitHub

## Step 4: Restart Your Server

After creating `.env.local`:

1. Stop your current server (Ctrl+C in the terminal where `npm run client` is running)

2. Restart it:
   ```bash
   npm run client
   ```

3. Refresh your browser at http://localhost:3001

4. Try issuing a credential again

## Step 5: Verify It's Working

1. Click "Issue Credential"

2. You should see: **"✓ Credential saved to Firestore successfully!"**

3. In the Firebase Console, go to **Firestore Database**

4. You should see a new collection called `credentials` with your saved credential

## Optional: Update Firestore Security Rules

Once everything is working, you should update your Firestore security rules:

1. In Firebase Console → Firestore Database → **"Rules"** tab

2. Replace the test rules with:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /credentials/{credentialId} {
         // Allow anyone to read and write (adjust as needed)
         allow read, write: if true;
       }
     }
   }
   ```

3. Click **"Publish"**

## Troubleshooting

**Problem**: Still seeing "Saving credential to Firestore..." forever

**Solution**: 
- Check your browser's Developer Console (F12 → Console tab)
- Look for any error messages
- Verify your `.env.local` file has all 6 values

**Problem**: "Firebase: Error (auth/invalid-api-key)"

**Solution**: 
- Double-check you copied the correct `apiKey` value from Firebase Console
- Make sure there are no extra spaces in `.env.local`

**Problem**: Can't find Firebase config in console

**Solution**: 
- Make sure you registered a Web app (not iOS/Android)
- Go to Project Settings → Your apps section

---

**Need help?** Check the browser console for error messages - they usually tell you exactly what's wrong!

