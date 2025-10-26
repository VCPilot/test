const express = require('express');
const fs = require('fs');
const path = require('path');
const { createAgent, ICredentialIssuer, IDataStore } = require('@veramo/core');
const { CredentialIssuer } = require('@veramo/credential-ld');
const { DataStore, DataStoreORM } = require('@veramo/data-store');
const { KeyManager } = require('@veramo/key-manager');
const { KeyManagementSystem } = require('@veramo/kms-local');
const { EthrDIDProvider } = require('@veramo/did-provider-ethr');
const { DIDResolverPlugin } = require('@veramo/did-resolver');
const { getResolver } = require('ethr-did-resolver');
const { DIDComm } = require('@veramo/did-comm');
const Database = require('better-sqlite3');

const app = express();
app.use(express.json());

// Initialize Veramo agent
const dbPath = path.join(__dirname, 'veramo-db.sqlite');
const dbConnection = new Database(dbPath);

const agent = createAgent({
  plugins: [
    new KeyManager({
      store: new DataStore(dbConnection),
      kms: {
        local: new KeyManagementSystem(),
      },
    }),
    new DIDResolverPlugin({
      resolver: getResolver({
        networks: [
          {
            name: 'mainnet',
            rpcUrl: 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY', // Optional: for mainnet
          },
        ],
      }),
    }),
    new CredentialIssuer({
      credentialStore: new DataStore(dbConnection),
      keyStore: new DataStore(dbConnection),
      credentialManager: new DIDComm({
        store: new DataStore(dbConnection),
      }),
    }),
  ],
});

// Issue credential endpoint
app.post('/issue', async (req, res) => {
  try {
    // Load synthetic profiles
    const profilesPath = path.join(__dirname, 'synthetic_profiles.json');
    const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf8'));
    
    if (!profiles || profiles.length === 0) {
      return res.status(400).json({ error: 'No profiles found' });
    }

    // Get the first profile (or you can specify which one via query param)
    const profileIndex = req.query.index || 0;
    const profile = profiles[profileIndex];
    
    if (!profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Generate a DID for the issuer (if not exists)
    const issuerKeyId = 'issuer-key-1';
    let issuerDid;
    
    try {
      // Create a new key for the issuer
      const key = await agent.keyManagerCreate({
        kms: 'local',
        type: 'Secp256k1',
      });
      
      issuerDid = `did:ethr:${key.publicKeyHex.slice(-40)}`;
    } catch (error) {
      // Key might already exist
      const existingKeys = await agent.keyManagerGetKeyManagementSystems();
      issuerDid = `did:ethr:${existingKeys[0]}`;
    }

    // Create the credential
    const credential = {
      '@context': [
        'https://www.w3.org/2018/credentials/v1',
        'https://www.w3.org/2018/credentials/examples/v1',
      ],
      type: ['VerifiableCredential', 'IdentityCredential'],
      issuer: { id: issuerDid },
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

    // Sign the credential
    const verifiableCredential = await agent.createVerifiableCredential({
      credential,
      proofFormat: 'jwt',
    });

    res.json({
      profile,
      credential: verifiableCredential,
    });
  } catch (error) {
    console.error('Error issuing credential:', error);
    res.status(500).json({ error: error.message });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`VC Identity Pilot server running on http://localhost:${PORT}`);
  console.log(`Available endpoints:`);
  console.log(`  POST /issue - Issue a Verifiable Credential`);
  console.log(`  GET  /health - Health check`);
});

module.exports = app;
