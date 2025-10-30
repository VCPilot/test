const functions = require('firebase-functions');
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();

// Configure CORS to allow all origins (or specify your domain)
const corsOptions = {
  origin: true, // Allow all origins for Functions
  credentials: true,
};

app.use(cors(corsOptions));
app.use(express.json());

// Generate a local issuer DID
const generateIssuerDID = () => {
  return `did:web:issuer.firebase`;
};

const issuerDid = generateIssuerDID();

// Issue credential handler (works for both GET and POST)
const handleIssue = async (req, res) => {
  try {
    // Load synthetic profiles from parent directory
    const profilesPath = path.join(__dirname, '../synthetic_profiles.json');
    const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf8'));
    
    if (!profiles || profiles.length === 0) {
      return res.status(400).json({ error: 'No profiles found' });
    }

    // Get the profile index
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

    // Create a simple proof
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
    deployed: true,
    endpoints: {
      '/issue': 'Issue a Verifiable Credential (GET/POST)',
      '/health': 'Health check endpoint'
    }
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

// Export the Express app as a Firebase Cloud Function
exports.api = functions.https.onRequest(app);

