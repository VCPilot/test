# Verify Endpoint Documentation

## Overview

The `/verify` endpoint allows you to verify the structural validity and issuer authenticity of a Verifiable Credential.

## Endpoint

**POST** `/verify`

## Request

Send the credential JSON in the request body:

### Option 1: Direct credential
```json
{
  "@context": ["..."],
  "type": ["..."],
  "issuer": "...",
  "credentialSubject": {...},
  "proof": {...}
}
```

### Option 2: Wrapped credential
```json
{
  "credential": {
    "@context": ["..."],
    "type": ["..."],
    ...
  }
}
```

## Response

### Success (Verified)
```json
{
  "verified": true,
  "message": "Credential verified successfully",
  "checks": {
    "hasContext": true,
    "hasType": true,
    "hasIssuer": true,
    "hasIssuanceDate": true,
    "hasCredentialSubject": true,
    "hasProof": true,
    "correctIssuer": true
  },
  "issuer": "did:web:issuer.local",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Failed Verification
```json
{
  "verified": false,
  "message": "Credential verification failed",
  "checks": {
    "hasContext": true,
    "hasType": true,
    "hasIssuer": true,
    "hasIssuanceDate": true,
    "hasCredentialSubject": true,
    "hasProof": true,
    "correctIssuer": false  // Issuer doesn't match
  },
  "issuer": "did:example:someone-else",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Error
```json
{
  "verified": false,
  "error": "No credential provided"
}
```

## Verification Checks

The endpoint performs the following structural checks:

1. **hasContext**: Verifies `@context` is an array with at least one element
2. **hasType**: Verifies `type` is an array with at least one element
3. **hasIssuer**: Verifies `issuer` is a non-empty string
4. **hasIssuanceDate**: Verifies `issuanceDate` is a string
5. **hasCredentialSubject**: Verifies `credentialSubject` is an object
6. **hasProof**: Verifies `proof` is an object
7. **correctIssuer**: Verifies issuer matches the expected issuer DID (`did:web:issuer.local`)

**Note**: This is a demo implementation that performs structural validation and issuer checking. In production, you would verify the cryptographic proof using libraries like Veramo.

## Example Usage

### Using curl
```bash
# First, issue a credential
curl http://localhost:3000/issue > credential.json

# Then verify it
curl -X POST http://localhost:3000/verify \
  -H "Content-Type: application/json" \
  -d @credential.json
```

### Using JavaScript
```javascript
// Issue a credential
const issueResponse = await fetch('http://localhost:3000/issue');
const { credential } = await issueResponse.json();

// Verify the credential
const verifyResponse = await fetch('http://localhost:3000/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(credential)
});

const result = await verifyResponse.json();
console.log('Verified:', result.verified); // true or false
console.log('Checks:', result.checks); // detailed check results
```

## Testing

Start the server:
```bash
node server.js
```

Then test the endpoint:
```bash
# Get a credential
curl http://localhost:3000/issue?profile=0

# Verify it (replace CREDENTIAL with the actual credential JSON)
curl -X POST http://localhost:3000/verify \
  -H "Content-Type: application/json" \
  -d '{"credential": {...}}'
```

## Notes

- This endpoint only performs structural validation, not cryptographic proof verification
- For production use, integrate with Veramo or similar cryptographic libraries
- The issuer MUST match `did:web:issuer.local` for verification to pass
- All structural checks must pass for the credential to be considered verified

