---
name: better-auth-expert
description: |
  This skill should be used when creating authentication configurations for Better Auth with Next.js 16 frontend and Python FastAPI backend using JWT tokens. It handles the complete setup including JWT plugin configuration, Next.js client setup, and Python JWT verification with shared secrets.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Better Auth Expert Skill

This skill provides expert guidance for setting up Better Auth with JWT tokens in a monorepo containing Next.js 16 frontend and Python FastAPI backend.

## Skill Purpose

This skill helps configure a complete authentication system using Better Auth with JWT tokens, ensuring secure communication between a Next.js 16 frontend and Python FastAPI backend using a shared secret for token verification.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, current auth setup (if any), environment variables, existing API routes |
| **Conversation** | User's specific requirements for auth flows, user models, custom fields, protected routes |
| **Skill References** | Domain patterns from `references/` (JWT configuration, Next.js integration, Python verification) |
| **User Guidelines** | Project-specific conventions, team standards, security requirements |

Ensure all required context is gathered before implementing.

## Configuration Requirements

- Frontend must use `betterAuth` with `plugins: [jwt()]`
- Backend must verify the JWT signature using the shared `BETTER_AUTH_SECRET`
- Do NOT use NextAuth or Auth.js; only Better Auth

## Implementation Steps

### 1. Configure Better Auth with JWT Plugin

Create the main auth configuration for the Next.js frontend:

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  database: {
    // Your database configuration
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  plugins: [
    jwt({
      algorithm: "HS256",
      expiresIn: "7d",
      issuer: process.env.BETTER_AUTH_ISSUER || "https://your-app.com",
      audience: [process.env.BETTER_AUTH_AUDIENCE || "https://your-app.com"],
    }),
  ],
});
```

### 2. Set up Next.js API Route Handler

Create the API route handler in `app/api/auth/route.ts`:

```typescript
import { auth } from "@/lib/auth";

// Use the built-in Next.js adapter
export const { GET, POST } = auth;
```

### 3. Create Better Auth Client Instance

Create a client instance in `lib/auth-client.ts`:

```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
  fetchOptions: {
    // Add any custom fetch options here
  },
});
```

### 4. Set up Server Component with Session (Recommended)

For server-side protected pages, use server-side session validation:

```typescript
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/sign-in");
  }

  return (
    <div>
      <h1>Welcome {session.user.name}</h1>
    </div>
  );
}
```

### Alternative: Client Component with Session

If you need client-side interactivity, use the client component:

```typescript
"use client";

import { authClient } from "@/lib/auth-client";
import { redirect } from "next/navigation";

const DashboardPage = () => {
  const { data, error, isPending } = authClient.useSession();

  if (isPending) {
    return <div>Loading...</div>;
  }
  if (!data || error) {
    redirect("/sign-in");
  }

  return (
    <div>
      <h1>Welcome {data.user.name}</h1>
    </div>
  );
};

export default DashboardPage;
```

### 5. Python JWT Verification Setup

Create a JWT verification module in your FastAPI backend. You can use either the manual verification approach or leverage Better Auth's built-in verification:

**Option A: Manual JWT Verification (using pyjwt)**

```python
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import os

# Initialize security scheme
security = HTTPBearer()

# Get secret from environment
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = "HS256"

def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token using the shared Better Auth secret
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"verify_aud": False, "verify_iss": False}  # Disable issuer/audience verification if needed
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials=Depends(security)) -> dict:
    """
    Get current user from JWT token in Authorization header
    """
    token = credentials.credentials
    return verify_jwt_token(token)

# Example usage in a FastAPI route:
from fastapi import FastAPI

app = FastAPI()

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}
```

**Option B: Using Better Auth's Built-in Verification (Recommended)**

For more robust verification that matches Better Auth's token format exactly, you can implement token validation using the same patterns Better Auth uses:

```python
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import os
import httpx

# Initialize security scheme
security = HTTPBearer()

# Get configuration from environment
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = "HS256"
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

async def verify_better_auth_token(token: str) -> dict:
    """
    Verify JWT token using Better Auth's JWKS endpoint for more secure validation
    """
    try:
        # Fetch JWKS from Better Auth endpoint
        async with httpx.AsyncClient() as client:
            jwks_response = await client.get(f"{BETTER_AUTH_URL}/api/auth/jwks")
            jwks = jwks_response.json()

        # Verify token using JWKS
        from jose import jwt, jwk
        from jose.utils import base64url_decode

        # Decode the token to get the header
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')

        # Find the key in JWKS
        key = None
        for k in jwks['keys']:
            if k['kid'] == kid:
                key = k
                break

        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate signing key"
            )

        # Convert the key and verify
        signing_key = jwk.construct(key, key['kty'])
        message, encoded_sig, header = jwt._load(token)
        decoded_sig = base64url_decode(encoded_sig)

        if not signing_key.verify(message, decoded_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature"
            )

        # If signature is valid, decode and return payload
        payload = jwt.decode(
            token,
            key,  # This should be the secret key for HS256
            algorithms=[JWT_ALGORITHM],
            issuer=BETTER_AUTH_URL,  # Verify issuer
            audience=BETTER_AUTH_URL  # Verify audience
        )

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials=Depends(security)) -> dict:
    """
    Get current user from Better Auth JWT token in Authorization header
    """
    token = credentials.credentials
    return await verify_better_auth_token(token)
```

### 6. Environment Variables

Create or update your `.env` files:

```bash
# Frontend (Next.js)
NEXT_PUBLIC_BASE_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000/api/auth
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_ISSUER=https://your-app.com
BETTER_AUTH_AUDIENCE=https://your-app.com

# Backend (FastAPI)
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

## Security Considerations

1. **Secret Management**: Store `BETTER_AUTH_SECRET` securely in environment variables
2. **Token Validation**: Always validate JWT tokens on the backend before processing requests
3. **HTTPS**: Use HTTPS in production to prevent token interception
4. **Token Expiration**: Configure appropriate token expiration times
5. **Algorithm**: Use HS256 or stronger algorithms for token signing

## Dependencies to Install

### Frontend (Next.js):
```bash
npm install better-auth @better-auth/next-js
# or
yarn add better-auth @better-auth/next-js
```

### Backend (FastAPI):
```bash
pip install pyjwt[crypto]
# or if using poetry
poetry add pyjwt[crypto]
```

## Common Issues and Solutions

1. **Token Verification Fails**: Ensure the `BETTER_AUTH_SECRET` is identical between frontend and backend
2. **CORS Issues**: Configure CORS properly to allow communication between frontend and backend
3. **Token Expiration**: Adjust `expiresIn` in the JWT plugin configuration as needed
4. **Issuer/Audience Mismatch**: Verify that issuer and audience values match between frontend and backend configurations

## Testing the Setup

1. Start your Next.js frontend
2. Start your FastAPI backend
3. Register/login a user through the frontend
4. Access protected routes on the backend using the JWT token from the frontend session