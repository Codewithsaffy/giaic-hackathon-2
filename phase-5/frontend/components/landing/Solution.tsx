'use client';

import { ArrowRight } from 'lucide-react'; // Removing local Icons import as they are defined below

export function Solution() {
    const steps = [
        {
            title: "Capture Everything Instantly",
            description: "Add tasks in seconds with AI-powered quick capture. Never lose a high-impact idea again.",
            icon: <CaptureIcon className="w-6 h-6" />
        },
        {
            title: "AI Plans Your Day",
            description: "Generate intelligent daily summaries and plans based on your true priorities and hard deadlines.",
            icon: <AiIcon className="w-6 h-6" />
        },
        {
            title: "Work on What Matters",
            description: "Focus mode blocks distractions and keeps you on your current active deployment node.",
            icon: <FocusIcon className="w-6 h-6" />
        },
        {
            title: "Review & Improve",
            description: "Weekly AI-powered reflections help you identify patterns and optimize your consistency scores.",
            icon: <ImproveIcon className="w-6 h-6" />
        }
    ];

    return (
        <section className="py-24 px-6 overflow-hidden">
            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col lg:flex-row items-center gap-16">
                    <div className="flex-1">
                        <h2 className="text-4xl md:text-6xl font-black font-heading text-white leading-[1.1] mb-8">
                            Smart Task Management <br />
                            <span className="text-emerald-500">for Real Productivity.</span>
                        </h2>
                        <div className="space-y-10">
                            {steps.map((step, idx) => (
                                <div key={step.title} className="flex gap-6 group">
                                    <div className="flex flex-col items-center">
                                        <div className="w-12 h-12 rounded-xl bg-neutral-900 border border-neutral-800 flex items-center justify-center text-emerald-500 group-hover:bg-emerald-500 group-hover:text-black transition-all duration-300">
                                            {step.icon}
                                        </div>
                                        {idx !== steps.length - 1 && <div className="w-[2px] h-full bg-neutral-900 mt-2"></div>}
                                    </div>
                                    <div className="pt-1">
                                        <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                                        <p className="text-neutral-500 text-sm leading-relaxed max-w-sm">{step.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex-1 relative">
                        <div className="relative glass-card aspect-square rounded-[3rem] p-8 border-emerald-500/10 flex items-center justify-center overflow-hidden group">
                            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--emerald-500)_0%,_transparent_70%)] opacity-5"></div>

                            {/* Visual Representation of "The Process" */}
                            <div className="relative z-10 w-full h-full flex items-center justify-center">
                                <div className="w-64 h-64 border-2 border-dashed border-neutral-800 rounded-full animate-spin-slow flex items-center justify-center">
                                    <div className="w-48 h-48 border-2 border-neutral-800/50 rounded-full flex items-center justify-center">
                                        <div className="w-32 h-32 bg-emerald-500 rounded-full blur-[60px] opacity-20 animate-pulse"></div>
                                    </div>
                                </div>
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-4 bg-white text-black px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">Input</div>
                                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-4 bg-emerald-500 text-black px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">Output</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

// Minimal Icons for the component
function CaptureIcon({ className }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
    );
}

function AiIcon({ className }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v4" /><path d="m4.93 4.93 2.83 2.83" /><path d="M2 12h4" /><path d="m4.93 19.07 2.83-2.83" /><path d="M12 22v-4" /><path d="m19.07 19.07-2.83-2.83" /><path d="M22 12h-4" /><path d="m19.07 4.93-2.83 2.83" />
        </svg>
    );
}

function FocusIcon({ className }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="3" />
        </svg>
    );
}

function ImproveIcon({ className }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
            <polyline points="16 7 22 7 22 13" />
        </svg>
    );
}
