import { NextRequest, NextResponse } from "next/server";

/**
 * Next.js Middleware
 * Handles authentication-based redirection and route protection.
 */

const authRoutes = ["/auth/sign-in", "/auth/sign-up"];
const protectedRoutes = ["/todo", "/add-task"];

export function middleware(request: NextRequest) {
    const sessionToken = request.cookies.get("better-auth.session_token")?.value ||
        request.cookies.get("__secure-better-auth.session_token")?.value;

    const { pathname } = request.nextUrl;

    // 1. Skip if it's an API route or static asset
    if (
        pathname.startsWith('/api') ||
        pathname.startsWith('/_next') ||
        pathname.includes('favicon.ico')
    ) {
        return NextResponse.next();
    }

    console.log(`[Middleware] Request: ${pathname}, Session: ${!!sessionToken}`);

    const isAuthRoute = authRoutes.some(route => pathname.startsWith(route));
    const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

    // 2. Redirect authenticated users away from auth pages (Sign In / Sign Up)
    if (sessionToken && isAuthRoute) {
        console.log(`[Middleware] REDIRECT: Auth user -> /todo`);
        return NextResponse.redirect(new URL("/todo", request.url));
    }

    // 3. Redirect unauthenticated users away from protected pages (Dashboard / Add Task)
    if (!sessionToken && isProtectedRoute) {
        console.log(`[Middleware] REDIRECT: Guest user -> /auth/sign-in`);
        return NextResponse.redirect(new URL("/auth/sign-in", request.url));
    }

    return NextResponse.next();
}

/**
 * Optimization: Only run middleware on specific routes
 */
export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!_next/static|_next/image|favicon.ico).*)',
    ],
};
