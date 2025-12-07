# Project 3: Bulking up our JWKS Server

**Name:** Gautam Aryal  
**Course:** CSCE 3550 - Foundations of Cybersecurity 
**Semester:** Fall 2025

## Project Overview

This project enhances a JSON Web Key Set (JWKS) server with advanced security features including AES encryption for private keys, user registration with secure password generation, authentication request logging, and rate limiting to prevent abuse.

## Features Implemented

### 1. AES Encryption of Private Keys

- Private RSA keys are encrypted using AES-256-GCM before storing in the database
- Encryption key is securely loaded from the `NOT_MY_KEY` environment variable
- IV (Initialization Vector) is embedded directly in the encrypted blob
- Keys are automatically encrypted on save and decrypted on retrieval

### 2. User Registration

- **Endpoint:** `POST /register`
- Automatically generates secure passwords using UUIDv4
- Passwords are hashed with Argon2 (industry-standard secure hashing algorithm)
- User information stored in SQLite database
- Returns the generated password to the user upon successful registration

**Example Request:**

```json
{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Example Response:**

```json
{
  "password": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Authentication Request Logging

- All authentication requests are logged to `auth_logs` database table
- Captures: Request IP address, timestamp, and user ID (if provided)
- Only successful authentication attempts are logged
- Enables security auditing and monitoring

### 4. Rate Limiting

- **Endpoint:** `POST /auth` is rate-limited to 10 requests per second
- Returns HTTP 429 (Too Many Requests) when limit is exceeded
- Prevents DoS attacks and brute-force attempts
- Implemented using Flask-Limiter with in-memory storage

## Technology Stack

- Python 3.11+
- Flask 3.0.3
- SQLite3
- cryptography (AES-GCM, RSA key generation)
- argon2-cffi (password hashing)
- PyJWT (RS256 token signing)
- Flask-Limiter
- pytest and pytest-cov

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation Steps

**Clone the repository:**

```bash
git clone <repository-url>
cd jwks-server
```
**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Set the encryption key environment variable:**

Windows (PowerShell):

```powershell
$env:NOT_MY_KEY = "your-secret-encryption-key-here"
```

Linux/Mac:

```bash
export NOT_MY_KEY="your-secret-encryption-key-here"
```

**Run the server:**

```bash
python -m app.server
```

Server will start on `http://0.0.0.0:8080`.

## API Endpoints

### GET `/.well-known/jwks.json`

Returns the JSON Web Key Set containing all valid (non-expired) public keys.

**Response:**

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "1",
      "n": "base64url-encoded-modulus",
      "e": "AQAB"
    }
  ]
}
```

### POST `/register`

Register a new user and receive a generated password.

**Request Body:**

```json
{
  "username": "testuser",
  "email": "test@example.com"
}
```

**Response (201 Created):**

```json
{
  "password": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### POST `/auth`

Authenticate and receive a signed JWT token.

**Query Parameters:**

- `expired` (optional): Set to `"true"` to request a token signed with an expired key

**Example Response:**

```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ..."
}
```

**429 Response (Rate Limited):**

Returned when more than 10 requests per second are made.

## Database Schema

### keys Table

```sql
CREATE TABLE keys(
    kid INTEGER PRIMARY KEY AUTOINCREMENT,
    key BLOB NOT NULL,
    exp INTEGER NOT NULL,
    iv BLOB NOT NULL
);
```

### users Table

```sql
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### auth_logs Table

```sql
CREATE TABLE auth_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_ip TEXT NOT NULL,
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## Project Structure

```
jwks-server/
├── app/
│   ├── __init__.py
│   ├── auth_logger.py
│   ├── database.py
│   ├── encryption.py
│   ├── jwks_utils.py
│   ├── key_store.py
│   ├── server.py
│   └── user_store.py
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── README.md
├── requirements.txt
└── totally_not_my_privateKeys.db
```

## Security Features

### Encryption Details

- **Algorithm:** AES-256-GCM
- **Key Size:** 256 bits (32 bytes)
- **Nonce Size:** 96 bits (12 bytes)
- **Mode:** Authenticated encryption

### Password Security

- Password generation uses UUIDv4
- Argon2id password hashing
  - Time cost: 2
  - Memory cost: 64 MB
  - Parallelism: 4
  - Salt: 16 bytes
  - Hash length: 32 bytes

### Rate Limiting

- Token bucket algorithm
- Limit: 10 requests per second
- Storage: in-memory
- Exceeds limit returns HTTP 429

## Testing

Run the full test suite with coverage:

```bash
pytest tests/ -v --cov=app
```

**Tests include:**

- Database creation and seeding
- JWT token signing and validation
- JWKS endpoint validation
- User registration
- Authentication logging
- Rate limiting
- SQL injection protection

## Running the Gradebot

Windows:

```powershell
.\gradebot.exe project3
```

## Key Implementation Notes

- `NOT_MY_KEY` must be set before running the server
- On startup, the server creates required tables and seeds two RSA keys
- One key is expired; one is valid for one hour
- Sensitive information is never committed to the repository

## Dependencies

See `requirements.txt` for the full list:

- Flask
- cryptography
- PyJWT
- argon2-cffi
- Flask-Limiter
- pytest
- pytest-cov

## References

- RFC 7517 - JSON Web Key (JWK)
- RFC 7519 - JSON Web Token (JWT)
- RFC 6585 - HTTP 429 Status Code
- NIST SP 800-38D - AES-GCM
- Argon2 Password Hashing Specification

## Author

Gautam Aryal  
CSCE 3550 - Foundations of Cybersecurity 
University of North Texas  
Fall 2025


