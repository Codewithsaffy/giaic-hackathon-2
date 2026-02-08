import { createAuthClient } from 'better-auth/react';
import { jwtClient } from 'better-auth/client/plugins';

const getBaseURL = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
};

export const authClient = createAuthClient({
  baseURL: getBaseURL(),
  plugins: [
    jwtClient() // Adds authClient.token() method for JWT retrieval
  ]
});

export const { signIn, signOut, useSession, signUp } = authClient;
