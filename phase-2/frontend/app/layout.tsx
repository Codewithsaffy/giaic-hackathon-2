import type { Metadata } from "next";
import { Outfit, Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { Sidebar } from "@/components/sidebar";
import { Search, Bell, User } from "lucide-react";
import Link from 'next/link';

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-heading",
  weight: ["300", "400", "500", "600", "700", "800"],
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "TaskFlow | Modern Intelligence",
  description: "High-performance task management with a sleek interface.",
};

import { Toaster } from "@/components/ui/sonner";

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  return (
    <html lang="en" className="dark">
      <body
        className={`${outfit.variable} ${plusJakarta.variable} ${jetbrainsMono.variable} font-body bg-[#020202] text-foreground min-h-screen overflow-x-hidden`}
      >
        <div className="flex">
          <Sidebar />

          <div className="flex-1 flex flex-col min-h-screen pl-20">
            {/* Header */}
            <header className="sticky top-0 z-40 w-full h-16 border-b border-neutral-900 bg-black/50 backdrop-blur-xl flex items-center px-8">
              <Link href="/" className="font-heading font-bold text-xl tracking-tighter text-white">
                TASKFLOW<span className="text-neutral-500">.</span>
              </Link>
            </header>

            {/* Main Content */}
            <main className="flex-1 relative">
              {/* Ambient Background Noise/Grain Overlay */}
              <div className="absolute inset-0 noise-overlay pointer-events-none opacity-[0.03]"></div>
              {children}
            </main>
          </div>
        </div>
        <Toaster theme="dark" position="top-right" closeButton />
      </body>
    </html>
  );
}
