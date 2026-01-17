# Better Auth Authentication Patterns

This document contains reference patterns and code snippets for implementing Better Auth with JWT tokens in a Next.js 16 and Python FastAPI environment.

## JWT Plugin Configuration

### Basic JWT Plugin Setup
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    jwt({
      algorithm: "HS256",
      expiresIn: "7d",
      issuer: "https://example.com",
      audience: ["https://api.example.com"],
    }),
  ],
});
```

### Advanced JWT Configuration with Custom Options
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
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

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET!,
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

### JWT Plugin with OIDC Provider Integration
```typescript
import { betterAuth } from "better-auth";
import { oidcProvider, jwt } from "better-auth/plugins";

export const auth = betterAuth({
  disabledPaths: [
    "/token",
  ],
  plugins: [
    jwt(), // Make sure to add the JWT plugin first
    oidcProvider({
      useJWTPlugin: true, // Enable JWT plugin integration
      loginPage: "/sign-in",
      // ... other options
    })
  ]
});
```

### JWT Plugin with Remote JWKS
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    jwt({
      jwks: {
        remoteUrl: "https://example.com/.well-known/jwks.json",
        keyPairConfig: {
          alg: 'ES256',
        },
      }
    })
  ]
});
```

### JWT Plugin with Custom Token Validation
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    jwt({
      algorithm: "HS256",
      expiresIn: "7d",
      issuer: process.env.BETTER_AUTH_ISSUER || "https://your-app.com",
      audience: [process.env.BETTER_AUTH_AUDIENCE || "https://your-app.com"],
      // Custom validation options
      validateToken: async (token) => {
        // Custom validation logic
        return true; // or false if validation fails
      }
    })
  ]
});
```

## Next.js 16 Client Setup

### API Route Handler Configuration
```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### Client Instance Creation
```typescript
import { createAuthClient } from "better-auth/react";
import { jwtClient } from 'better-auth/client/plugins';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
  plugins: [
    jwtClient() // Adds authClient.token() method for JWT retrieval
  ]
});

export const { signIn, signOut, useSession, signUp } = authClient;
```

### Protected Component with Session Hook
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

### Sign-in Component Example
```typescript
"use client";

import { authClient } from "@/lib/auth-client";

const SignInPage = () => {
  const { signIn } = authClient;

  const handleSignIn = async () => {
    await signIn.email({
      email: "user@example.com",
      password: "password",
      redirectTo: "/dashboard"
    });
  };

  return (
    <div>
      <button onClick={handleSignIn}>Sign In</button>
    </div>
  );
};

export default SignInPage;
```

## Python JWT Verification Logic

### Basic JWT Verification Function
```python
from typing import Optional
import jwt
import os
from fastapi import HTTPException, status

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
```

### FastAPI Dependency with HTTP Bearer
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict

security = HTTPBearer()

async def get_current_user(credentials=Depends(security)) -> Dict:
    """
    Get current user from JWT token in Authorization header
    """
    token = credentials.credentials
    return verify_jwt_token(token)
```

### Complete FastAPI Setup Example
```python
from datetime import datetime
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

### Advanced Python JWT Verification with JWKS (Recommended) - Updated Implementation
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

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

## Environment Configuration

### Frontend (Next.js) .env
```bash
NEXT_PUBLIC_BASE_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Backend (FastAPI) .env
```bash
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_URL=http://localhost:3000
API_AUDIENCE=http://127.0.0.1:8000
```

## Token Verification with Better Auth's Built-in Functions

### Using verifyAccessToken from better-auth/oauth2
```typescript
import { verifyAccessToken } from "better-auth/oauth2";

export const GET = async (req: Request) => {
  const authorization = req.headers?.get("authorization") ?? undefined;
  const accessToken = authorization?.startsWith("Bearer ")
    ? authorization.replace("Bearer ", "")
    : authorization;
  const payload = await verifyAccessToken(
    accessToken, {
      verifyOptions: {
        issuer: "https://auth.example.com",
        audience: "https://api.example.com",
      },
      scopes: ["read:post"],
    }
  );
  // Continue with protected resource logic
}
```

### Local JWKS Verification
```typescript
import { jwtVerify, createLocalJWKSet } from 'jose'

async function validateToken(token: string) {
  try {
    /**
     * This is the JWKS that you get from the /api/auth/
     * jwks endpoint
     */
    const storedJWKS = {
      keys: [{
        //...
      }]
    };
    const JWKS = createLocalJWKSet({
      keys: storedJWKS.data?.keys!,
    })
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: 'http://localhost:3000', // Should match your JWT issuer, which is the BASE_URL
      audience: 'http://localhost:3000', // Should match your JWT audience, which is the BASE_URL by default
    })
    return payload
  } catch (error) {
    console.error('Token validation failed:', error)
    throw error
  }
}

// Usage example
const token = 'your.jwt.token' // this is the token you get from the /api/auth/token endpoint
const payload = await validateToken(token)
```

### Remote JWKS Verification
```typescript
import { jwtVerify, createRemoteJWKSet } from 'jose'

async function validateToken(token: string) {
  try {
    const JWKS = createRemoteJWKSet(
      new URL('http://localhost:3000/api/auth/jwks')
    )
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: 'http://localhost:3000', // Should match your JWT issuer, which is the BASE_URL
      audience: 'http://localhost:3000', // Should match your JWT audience, which is the BASE_URL by default
    })
    return payload
  } catch (error) {
    console.error('Token validation failed:', error)
    throw error
  }
}

// Usage example
const token = 'your.jwt.token' // this is the token you get from the /api/auth/token endpoint
const payload = await validateToken(token)
```

## Best Practices

1. **Secure Secret Storage**: Never hardcode secrets in your source code
2. **Token Expiration**: Set appropriate expiration times based on your security requirements
3. **Algorithm Selection**: Use HS256 or stronger algorithms for token signing
4. **Error Handling**: Implement proper error handling for token verification failures
5. **Issuer/Audience Validation**: Consider validating issuer and audience claims in production
6. **HTTPS Requirement**: Always use HTTPS in production to prevent token interception
7. **JWKS Validation**: For production systems, use JWKS-based validation for better security
8. **Token Revocation**: Implement token blacklisting for enhanced security controls
9. **Rate Limiting**: Apply rate limiting to authentication endpoints to prevent abuse
10. **Logging**: Log authentication attempts for security monitoring while protecting sensitive data

## Security Considerations

- **Secret Rotation**: Plan for periodic rotation of JWT secrets
- **Token Size**: Keep tokens small to reduce network overhead
- **Algorithm Confusion**: Prevent algorithm confusion attacks by validating the 'alg' header
- **Clock Skew**: Account for minor clock differences between systems when validating exp/nbf claims
- **Access vs Identity Tokens**: Use separate tokens for access control vs identity verification