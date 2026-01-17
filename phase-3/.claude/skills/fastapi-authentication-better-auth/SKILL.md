---
name: better-auth-expert
description: Expert in Better Auth implementation with Next.js 16, FastAPI, and JWT authentication. Handles authentication patterns, JWT token management, and secure API integration.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Better Auth Expert

This skill should be used when implementing authentication with Better Auth, JWT tokens, Next.js 16, and FastAPI integration.

## Core Capabilities

### 1. Better Auth Configuration

#### Frontend Configuration
```typescript
import { betterAuth } from 'better-auth';
import { jwt } from 'better-auth/plugins';
import { nextCookies } from 'better-auth/next-js';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  },
  connectionTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
  max: 10
});

const secret = process.env.BETTER_AUTH_SECRET;

export const auth = betterAuth({
  database: pool,
  secret: secret,
  baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000',
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: [process.env.BETTER_AUTH_URL || 'http://localhost:3000'],
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET,
      algorithm: 'HS256',
      expirationTime: '7d',
      jwt: {
        issuer: process.env.BETTER_AUTH_URL || 'http://localhost:3000',
        audience: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
      }
    }),
    nextCookies()
  ]
});
```

#### Client Configuration
```typescript
import { createAuthClient } from 'better-auth/react';
import { jwtClient } from 'better-auth/client/plugins';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
  plugins: [
    jwtClient() // Adds authClient.token() method for JWT retrieval
  ]
});

export const { signIn, signOut, useSession, signUp } = authClient;
```

#### API Route Handler
```typescript
import { auth } from '@/lib/auth';
import { toNextJsHandler } from 'better-auth/next-js';

export const { GET, POST } = toNextJsHandler(auth);
```

### 2. JWT Token Management

#### Client-Side JWT Retrieval
```typescript
async function getJWTToken(): Promise<string> {
    const { data, error } = await authClient.token();

    if (error || !data?.token) {
        throw new Error('Failed to get JWT token: ' + (error?.message || 'No token returned'));
    }

    return data.token;
}
```

### 3. Backend JWT Verification

#### Python FastAPI Integration
```python
from typing import Optional
import jwt  # PyJWT
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session
from models import Session

# Initialize security scheme
security = HTTPBearer(auto_error=False)

# Configuration
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"
API_AUDIENCE = os.getenv("API_AUDIENCE", "http://127.0.0.1:8000")

# Initialize JWKS Client
jwks_client = PyJWKClient(JWKS_URL)

async def verify_token(token: str, db: AsyncSession) -> dict:
    """
    Verify token:
    1. Try JWKS (EdDSA) - Default for Better Auth
    2. Try Shared Secret (HS256) - Fallback
    3. Try Opaque Session Token - Fallback
    """

    # 1. Try JWKS Verification (EdDSA)
    try:
        # This automatically fetches keys and finds the right one by 'kid'
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "RS256"],
            audience=API_AUDIENCE,
            issuer=BETTER_AUTH_URL,
            # Allow some clock skew
            leeway=60
        )
        logger.info(f"Successfully verified JWT (JWKS) for user {payload.get('sub')}")
        return payload
    except Exception as e:
        logger.warning(f"JWKS verification failed: {e}")

    # 2. Try Shared Secret Verification (HS256)
    if JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                audience=API_AUDIENCE,
                issuer=BETTER_AUTH_URL
            )
            logger.info(f"Successfully verified JWT (HS256) for user {payload.get('sub')}")
            return payload
        except Exception as e:
            logger.warning(f"HS256 verification failed: {e}")

    # 3. Verify as Opaque Session Token in DB
    try:
        # Better Auth sends signed cookies (e.g., token.signature)
        # We need to strip the signature to match the DB record
        raw_token = token
        if "." in token:
             parts = token.split(".")
             if len(parts) == 2: # Typical signed cookie format: value.signature
                 raw_token = parts[0]

        statement = select(Session).where(Session.token == raw_token)
        result = await db.exec(statement)
        session = result.first()

        if session:
            now = datetime.now(timezone.utc)
            session_expiry = session.expiresAt.replace(tzinfo=timezone.utc) if session.expiresAt.tzinfo is None else session.expiresAt

            if session_expiry < now:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )

            return {
                "sub": session.userId,
                "type": "session",
                "exp": int(session.expiresAt.timestamp())
            }
    except Exception as e:
        logger.error(f"Database session lookup error: {str(e)}")

    # All failed
    logger.warning("Token verification completely failed")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPBearer] = Depends(security),
    db: AsyncSession = Depends(get_session)
) -> dict:
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing Authorization header"
        )

    return await verify_token(token, db)
```

### 4. API Authentication Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import uuid

from auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user info from JWT token.
    This endpoint verifies the JWT and returns user information.
    """
    # Extract user info from the token payload
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )

    return {
        "id": user_id,
        "email": current_user.get("email", ""),
        "name": current_user.get("name", ""),
        "created_at": current_user.get("iat")
    }
```

### 5. Client-Server API Integration

#### Frontend API Client with JWT
```typescript
async function apiClient<T>(
    endpoint: string | ((userId: string) => string),
    options: RequestInit = {}
): Promise<T> {
    const userId = await getUserId();
    const jwt = await getJWTToken();

    // Resolve endpoint
    const urlPath = typeof endpoint === 'function' ? endpoint(userId) : endpoint;

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwt}`,
        ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${urlPath}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({
            detail: 'Unknown error occurred'
        }));
        throw new Error(errorData.detail || `API Error: ${response.statusText}`);
    }

    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}
```

#### Server-Side API Client
```typescript
export async function apiClientServer<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Get the JWT token from cookies
  const cookieStore = await cookies();
  const token = cookieStore.get('better-auth.session_token')?.value;

  const config: RequestInit = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    cache: options.cache,
    next: options.next,
    ...(options.body && { body: JSON.stringify(options.body) })
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`API request failed: ${response.status} - ${errorData}`);
    }

    return response.json();
  } catch (error) {
    console.error(`API request error for ${url}:`, error);
    throw error;
  }
}
```

## Environment Configuration

### Frontend (.env)
```bash
NEXT_PUBLIC_BASE_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_URL=http://localhost:3000
API_AUDIENCE=http://127.0.0.1:8000
```

## Best Practices

1. **Secure Secret Storage**: Always use environment variables for secrets
2. **Token Verification Order**: JWKS first, then HS256, then database session lookup
3. **JWT Caching**: Cache tokens client-side to avoid repeated requests
4. **Error Handling**: Comprehensive error handling for all authentication flows
5. **Type Safety**: Use TypeScript interfaces for API responses
6. **Security Headers**: Always include proper security headers in API requests
7. **Token Expiration**: Handle token expiration gracefully with proper error messages
8. **Logging**: Implement proper logging for authentication events

## Troubleshooting

### Common Issues
- Token verification fails: Check that JWKS URL is accessible
- Invalid audience/issuer: Ensure API_AUDIENCE and BETTER_AUTH_URL match
- Database session lookup: Verify that session tables are properly configured
- CORS issues: Ensure trusted origins are properly configured