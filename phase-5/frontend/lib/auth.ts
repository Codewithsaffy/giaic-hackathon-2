import { betterAuth } from 'better-auth';
import { jwt } from 'better-auth/plugins';
import { nextCookies } from 'better-auth/next-js';
import { Pool } from 'pg';

if (!process.env.DATABASE_URL) {
  console.warn('DATABASE_URL is not set in environment variables');
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  },
  connectionTimeoutMillis: 15000,
  idleTimeoutMillis: 30000,
  max: 10,
  keepAlive: true,
});

const secret = process.env.BETTER_AUTH_SECRET;

const getBetterAuthURL = () => {
  if (process.env.BETTER_AUTH_URL) return process.env.BETTER_AUTH_URL;
  if (process.env.NEXT_PUBLIC_BASE_URL) return process.env.NEXT_PUBLIC_BASE_URL;
  return 'http://localhost:3000';
};

const betterAuthUrl = getBetterAuthURL();

// Internal URL for Service-to-Service communication (e.g., SSR)
const internalApiUrl = process.env.INTERNAL_API_URL || 'http://todo-backend:8000';
// Public URL for Browser communication
const publicApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const resolvedApiUrl = (typeof window === 'undefined') ? internalApiUrl : publicApiUrl;

export const auth = betterAuth({
  database: pool,
  secret: secret,
  baseURL: betterAuthUrl,
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: [betterAuthUrl, 'http://localhost:3000', 'http://127.0.0.1:3000'],
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET,
      algorithm: 'HS256',
      expirationTime: '7d',
      jwt: {
        issuer: betterAuthUrl,
        audience: resolvedApiUrl
      }
    }),
    nextCookies()
  ]
});
