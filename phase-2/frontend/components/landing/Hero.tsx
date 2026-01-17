'use client';

import { ArrowRight, PlayCircle } from 'lucide-react';
import Link from 'next/link';

export function Hero() {
    return (
        <section className="relative pt-24 pb-12 md:pt-32 md:pb-20 px-4 md:px-6 overflow-hidden">
            {/* Background Glows */}
            <div className="absolute top-0 left-1/4 w-[1000px] h-[600px] bg-emerald-500/10 rounded-full blur-[160px] opacity-20 -translate-y-1/2 pointer-events-none"></div>

            <div className="max-w-7xl mx-auto flex flex-col items-center text-center relative z-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-900/50 border border-neutral-800 mb-6 md:mb-8 animate-in slide-in-from-top-4 duration-1000">
                    <span className="badge-new">NEW RELEASE</span>
                    <span className="text-[10px] uppercase font-bold tracking-widest text-neutral-500">Intelligent Habit Tracking</span>
                </div>

                <h1 className="text-4xl sm:text-5xl md:text-8xl font-extrabold font-heading mb-6 md:mb-8 tracking-tighter leading-[0.95] md:leading-[0.9] text-white">
                    Organize Your Work.<br />
                    <span className="text-gradient-white">Achieve Your Goals.</span><br />
                    Stay Consistent.
                </h1>

                <p className="text-base sm:text-lg md:text-xl text-neutral-400 font-light mb-8 md:mb-12 max-w-xl md:max-w-2xl mx-auto leading-relaxed animate-in fade-in duration-1000 delay-300">
                    The intelligent task manager that helps you build productive habits, not just manage to-do lists.
                    Engineered for high-performance teams and focused individuals.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 md:gap-6 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500 w-full sm:w-auto">
                    <Link
                        href="/auth/sign-up"
                        className="group relative px-8 py-4 md:px-10 md:py-5 bg-white text-black font-black uppercase text-xs tracking-widest rounded-full hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3 shadow-2xl shadow-white/10 w-full sm:w-auto"
                    >
                        Start Free
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                    <button
                        className="px-8 py-4 md:px-10 md:py-5 bg-transparent text-white font-black uppercase text-xs tracking-widest rounded-full border border-neutral-800 hover:bg-neutral-900 transition-all duration-300 flex items-center justify-center gap-3 w-full sm:w-auto"
                    >
                        <PlayCircle className="w-4 h-4" />
                        Watch Demo
                    </button>
                </div>

                {/* Interactive Product Preview Mockup */}
                <div className="mt-12 md:mt-24 w-full max-w-5xl perspective-1000 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-700">
                    <div className="relative group rounded-[1.5rem] md:rounded-[2rem] border border-neutral-800 bg-black/40 backdrop-blur-3xl p-2 md:p-4 shadow-2xl rotate-x-12 group-hover:rotate-x-0 transition-transform duration-700">
                        <div className="rounded-[1.5rem] overflow-hidden border border-neutral-800 bg-neutral-900/50 aspect-[16/10] relative">
                            {/* Fake UI Header */}
                            <div className="px-6 py-4 border-b border-neutral-800 flex items-center justify-between">
                                <div className="flex gap-2">
                                    <div className="w-3 h-3 rounded-full bg-neutral-800"></div>
                                    <div className="w-3 h-3 rounded-full bg-neutral-800"></div>
                                    <div className="w-3 h-3 rounded-full bg-neutral-800"></div>
                                </div>
                                <div className="h-4 w-48 bg-neutral-800 rounded-full"></div>
                                <div className="w-8 h-8 rounded-full bg-neutral-800"></div>
                            </div>

                            {/* Fake UI Sidebar & Content */}
                            <div className="flex h-full">
                                <div className="w-16 border-r border-neutral-800 p-4 space-y-4">
                                    <div className="w-8 h-8 bg-neutral-800 rounded-lg"></div>
                                    <div className="w-8 h-8 bg-neutral-800 rounded-lg"></div>
                                    <div className="w-8 h-8 bg-neutral-800 rounded-lg"></div>
                                </div>
                                <div className="flex-1 p-8 space-y-8">
                                    <div className="h-10 w-1/3 bg-neutral-800 rounded-lg"></div>
                                    <div className="grid grid-cols-3 gap-6">
                                        <div className="h-32 bg-white/5 border border-white/10 rounded-2xl animate-pulse"></div>
                                        <div className="h-32 bg-white/5 border border-white/10 rounded-2xl"></div>
                                        <div className="h-32 bg-white/5 border border-white/10 rounded-2xl"></div>
                                    </div>
                                    <div className="h-48 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl relative overflow-hidden">
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <span className="text-[10px] font-bold tracking-[0.3em] text-emerald-500/40 uppercase">AI Habit Analysis Active</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
