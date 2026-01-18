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
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return 'http://localhost:3000';
};

const betterAuthUrl = getBetterAuthURL();
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const auth = betterAuth({
  database: pool,
  secret: secret,
  baseURL: betterAuthUrl,
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: [betterAuthUrl],
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET,
      algorithm: 'HS256',
      expirationTime: '7d',
      jwt: {
        issuer: betterAuthUrl,
        audience: apiUrl
      }
    }),
    nextCookies()
  ]
});
