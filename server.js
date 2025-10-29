const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();

// Configure CORS
const corsOptions = {
  origin: [
    'http://localhost:3000',
    'https://vc-identity-pilot.web.app',
    'https://vc-identity-pilot.firebaseapp.com',
    process.env.FIREBASE_DOMAIN
  ].filter(Boolean),
  credentials: true,
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));
app.use(express.json());

// Generate a local issuer DID
const generateIssuerDID = () => {
  // Use a static DID for demo purposes (no key generation needed)
  return `did:web:issuer.local`;
};

const issuerDid = generateIssuerDID();

// Issue credential handler (works for both GET and POST)
const handleIssue = async (req, res) => {
  try {
    // Load synthetic profiles
    const profilesPath = path.join(__dirname, 'synthetic_profiles.json');
    const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf8'));
    
    if (!profiles || profiles.length === 0) {
      return res.status(400).json({ error: 'No profiles found' });
    }

    // Get the profile index (supports both 'profile' and 'index' query params)
    const profileIndex = parseInt(req.query.profile) || parseInt(req.query.index) || 0;
    const profile = profiles[profileIndex];
    
    if (!profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Create the credential
    const credential = {
      '@context': [
        'https://www.w3.org/2018/credentials/v1',
        'https://www.w3.org/2018/credentials/examples/v1',
      ],
      type: ['VerifiableCredential', 'IdentityCredential'],
      issuer: issuerDid,
      issuanceDate: new Date().toISOString(),
      credentialSubject: {
        id: `did:example:${profile.name.toLowerCase().replace(/\s/g, '')}`,
        name: profile.name,
        dateOfBirth: profile.dob,
        creditScore: profile.creditScore,
      },
      credentialSchema: {
        id: 'https://example.org/credential-schema/v1',
        type: 'JsonSchemaValidator2018',
      },
    };

    // Create a simple JWT-like proof (for demonstration)
    const proof = {
      type: 'Ed25519Signature2020',
      created: new Date().toISOString(),
      verificationMethod: `${issuerDid}#key-1`,
      proofValue: crypto.randomBytes(32).toString('base64'),
    };

    const verifiableCredential = {
      ...credential,
      proof
    };

    res.json({
      profile,
      credential: verifiableCredential,
    });
  } catch (error) {
    console.error('Error issuing credential:', error);
    res.status(500).json({ error: error.message });
  }
};

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'VC Identity Pilot API',
    version: '1.0.0',
    endpoints: {
      '/issue': 'Issue a Verifiable Credential (GET/POST) - Query params: profile or index (default: 0)',
      '/health': 'Health check endpoint'
    },
    wallet: 'Open http://localhost:3001 for the Wallet UI'
  });
});

// Support both GET and POST for /issue endpoint
app.get('/issue', handleIssue);
app.post('/issue', handleIssue);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    issuer: issuerDid 
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`VC Identity Pilot server running on http://localhost:${PORT}`);
  console.log(`Available endpoints:`);
  console.log(`  GET/POST /issue?profile=0 - Issue a Verifiable Credential`);
  console.log(`  GET  /health - Health check`);
});

module.exports = app;
