'use client';

import { useRouter } from 'next/navigation';
import { useSession } from '@/lib/auth-client';
import { authClient } from '@/lib/auth-client';
import { clearJWTCache } from '@/lib/api';
import { useEffect } from 'react';

export default function TodoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  // Redirect if no session
  useEffect(() => {
    if (!isPending && !session) {
      router.push('/auth/sign-in');
    }
  }, [session, isPending, router]);

  const handleSignOut = async () => {
    await authClient.signOut();
    clearJWTCache(); // Clear cached JWT
    router.push('/auth/sign-in');
  };

  if (isPending) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!session) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <main>{children}</main>
    </div>
  );
}