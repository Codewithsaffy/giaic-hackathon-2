'use client';

import { ArrowRight, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

export function FinalCTA() {
    const trustSignals = ["Free forever plan", "No credit card needed", "Cancel anytime"];

    return (
        <section className="py-24 px-6 relative">
            {/* Background Mesh */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-emerald-500/10 rounded-full blur-[160px] opacity-10 pointer-events-none"></div>

            <div className="max-w-5xl mx-auto rounded-[3.5rem] bg-neutral-900/30 border border-neutral-800 p-12 md:p-24 text-center relative z-10 overflow-hidden group">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_var(--emerald-500)_0%,_transparent_70%)] opacity-0 group-hover:opacity-5 transition-opacity duration-700"></div>

                <h2 className="text-5xl md:text-7xl font-black font-heading text-white mb-8 tracking-tighter leading-tight">
                    Start Building <br />
                    <span className="text-emerald-500 underline decoration-white/10 underline-offset-8">Better Habits</span> Today.
                </h2>

                <p className="text-xl text-neutral-400 font-light mb-12 max-w-xl mx-auto leading-relaxed">
                    Join thousands of professionals who have transformed their productivity and found absolute flow.
                </p>

                <div className="flex flex-col items-center gap-8">
                    <Link
                        href="/auth/sign-up"
                        className="group relative px-12 py-6 bg-white text-black font-black uppercase text-sm tracking-widest rounded-full hover:scale-105 transition-all duration-300 flex items-center gap-4 shadow-2xl shadow-white/10"
                    >
                        Start Free - No Credit Card Required
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>

                    <div className="flex flex-wrap justify-center gap-6">
                        {trustSignals.map((signal) => (
                            <div key={signal} className="flex items-center gap-2 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">
                                <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                                {signal}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer Minimal */}
            <footer className="mt-32 pt-20 border-t border-neutral-900 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8 pb-12">
                <div className="flex items-center gap-4">
                    <span className="text-xl font-black font-heading text-white tracking-tighter">TASKFLOW.</span>
                    <span className="text-[10px] font-bold text-neutral-600 uppercase tracking-widest">© 2026 Advanced AI Systems</span>
                </div>
                <div className="flex gap-8">
                    {["Protocol", "Security", "Infrastructure", "Support"].map((link) => (
                        <a key={link} href="#" className="text-[10px] font-bold text-neutral-500 hover:text-white uppercase tracking-widest transition-colors">{link}</a>
                    ))}
                </div>
                <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center hover:border-emerald-500 transition-colors cursor-pointer">
                        <div className="w-3 h-3 bg-white rounded-sm"></div>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center hover:border-emerald-500 transition-colors cursor-pointer">
                        <div className="w-3 h-3 bg-white rounded-full"></div>
                    </div>
                </div>
            </footer>
        </section>
    );
}
