import { NextRequest, NextResponse } from "next/server";

/**
 * Next.js 16 Proxy Middleware
 * Handles authentication-based redirection and route protection.
 */

const authRoutes = ["/auth/sign-in", "/auth/sign-up", "/sign-in", "/sign-up"];
const protectedRoutes = ["/todo", "/add-task"];

export function proxy(request: NextRequest) {
    const sessionToken = request.cookies.get("better-auth.session_token") ||
        request.cookies.get("__secure-better-auth.session_token");

    const pathname = request.nextUrl.pathname.toLowerCase();

    console.log(`[Proxy] Request: ${pathname}, Session: ${!!sessionToken}`);

    // 1. Authenticated users should not access auth pages (Sign In / Sign Up)
    if (sessionToken && authRoutes.some(route => pathname.startsWith(route.toLowerCase()))) {
        console.log(`[Proxy] REDIRECT: Auth user -> /todo`);
        return NextResponse.redirect(new URL("/todo", request.url));
    }

    // 2. Unauthenticated users should not access protected pages (Dashboard / Add Task)
    if (!sessionToken && protectedRoutes.some(route => pathname.startsWith(route.toLowerCase()))) {
        console.log(`[Proxy] REDIRECT: Guest user -> /auth/sign-in`);
        return NextResponse.redirect(new URL("/auth/sign-in", request.url));
    }

    return NextResponse.next();
}

export default proxy;

/**
 * Optimization: Only run proxy on specific routes
 */
export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
};
