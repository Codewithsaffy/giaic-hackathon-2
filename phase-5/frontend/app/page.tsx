'use client';

import { Hero } from '@/components/landing/Hero';
import { SocialProof } from '@/components/landing/SocialProof';
import { Problem } from '@/components/landing/Problem';
import { Solution } from '@/components/landing/Solution';
import { Features } from '@/components/landing/Features';
import { UseCases } from '@/components/landing/UseCases';
import { Testimonials } from '@/components/landing/Testimonials';
import { FAQ } from '@/components/landing/FAQ';
import { FinalCTA } from '@/components/landing/FinalCTA';

export default function LandingPage() {
    return (
        <main className="min-h-screen bg-black">
            {/* Background elements */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle_at_50%_0%,_#0a0a0a_0%,_#000000_100%)]"></div>
                <div className="noise-overlay absolute inset-0 opacity-[0.03]"></div>
            </div>

            <div className="relative z-10">
                <Hero />
                <SocialProof />
                <Problem />
                <Solution />
                <Features />
                <UseCases />
                <Testimonials />
                <FAQ />
                <FinalCTA />
            </div>
        </main>
    );
}