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
  }
});

const secret = process.env.BETTER_AUTH_SECRET;

export const auth = betterAuth({
  database: pool,
  secret: secret,
  baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000',
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: ['http://localhost:3000'],
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET, // Explicitly pass secret
      algorithm: 'HS256', // Force symmetric algorithm matching backend
      expirationTime: '7d',

      jwt: {
        issuer: 'http://localhost:3000',
        audience: 'http://127.0.0.1:8000'
      }
    }),
    nextCookies() // Must be last plugin
  ]
});
