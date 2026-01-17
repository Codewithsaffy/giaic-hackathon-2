'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Home, LayoutGrid, Plus, LogOut, LogIn, UserPlus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { authClient } from '@/lib/auth-client';

export function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const { data: session, isPending } = authClient.useSession();

    const handleSignOut = async () => {
        await authClient.signOut({
            fetchOptions: {
                onSuccess: () => {
                    router.push('/auth/sign-in');
                },
            },
        });
    };

    const authenticatedItems = [
        { icon: LayoutGrid, label: 'Dashboard', href: '/todo' },
        { icon: Plus, label: 'Deploy', href: '/add-task' },
    ];

    const guestItems = [
        { icon: LogIn, label: 'Sign In', href: '/auth/sign-in' },
        { icon: UserPlus, label: 'Sign Up', href: '/auth/sign-up' },
    ];

    const items = [
        { icon: Home, label: 'Home', href: '/' },
        ...(session ? authenticatedItems : guestItems)
    ];

    if (isPending) return (
        <aside className="sidebar-container animate-pulse opacity-50">
            <div className="mb-10 w-12 h-12 bg-neutral-800 rounded-2xl"></div>
        </aside>
    );

    return (
        <aside className="sidebar-container">
            {/* App Logo (Desktop Only) */}
            <Link href="/" className="hidden md:flex mb-10 w-12 h-12 bg-white rounded-2xl items-center justify-center shadow-lg shadow-white/10 group cursor-pointer transition-transform hover:scale-110">
                <div className="w-6 h-6 bg-black rounded-lg transform rotate-45 group-hover:rotate-90 transition-transform duration-500"></div>
            </Link>

            {/* Nav Items */}
            <div className="flex flex-row w-full justify-around md:flex-col md:w-auto md:flex-1 md:justify-start items-center">
                {items.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;

                    return (
                        <Link
                            key={item.label}
                            href={item.href}
                            className={cn("sidebar-item group", isActive && "active")}
                        >
                            <Icon className={cn("w-6 h-6", isActive ? "text-white" : "text-neutral-500 group-hover:text-white")} strokeWidth={1.5} />
                            <span className={cn("sidebar-label", isActive ? "text-white" : "group-hover:text-white")}>
                                {item.label}
                            </span>
                        </Link>
                    );
                })}

                {/* Mobile Logout (Integrated into nav flow) */}
                {session && (
                    <button onClick={handleSignOut} className="sidebar-item group md:hidden">
                        <LogOut className="w-6 h-6 text-neutral-500 group-hover:text-red-400 transition-colors" strokeWidth={1.5} />
                        <span className="sidebar-label group-hover:text-red-400 transition-colors">Logout</span>
                    </button>
                )}
            </div>

            {/* Desktop Bottom Actions (Logout) */}
            <div className="hidden md:flex flex-col items-center gap-4 mt-auto">
                {session && (
                    <button onClick={handleSignOut} className="sidebar-item group">
                        <LogOut className="w-6 h-6 text-neutral-500 group-hover:text-red-400 transition-colors" strokeWidth={1.5} />
                        <span className="sidebar-label group-hover:text-red-400 transition-colors">Logout</span>
                    </button>
                )}
            </div>
        </aside>
    );
}
