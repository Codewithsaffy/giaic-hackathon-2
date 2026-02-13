'use client';

import { XCircle, AlertCircle, ZapOff } from 'lucide-react';

export function Problem() {
    const problems = [
        {
            icon: <XCircle className="w-8 h-8 text-red-500" />,
            title: "Scattered Work Everywhere",
            description: "Your tasks live across 5 different apps, sticky notes, and your memory. Fragmented focus leads to catastrophic leaks."
        },
        {
            icon: <AlertCircle className="w-8 h-8 text-red-500" />,
            title: "No System, Just Chaos",
            description: "Random bursts of productivity followed by weeks of procrastination. Without structure, consistency is an impossible dream."
        },
        {
            icon: <ZapOff className="w-8 h-8 text-red-500" />,
            title: "Manual Planning Takes Forever",
            description: "Spending hours organizing instead of actually working. Your system should work for you, not the other way around."
        }
    ];

    return (
        <section className="py-24 px-6 bg-neutral-950/50">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-20">
                    <h2 className="text-3xl md:text-5xl font-bold font-heading text-white mb-6">
                        Task Lists Aren't Enough Anymore
                    </h2>
                    <p className="text-neutral-500 max-w-2xl mx-auto font-light">
                        Traditional tools only track what you've done. They don't help you decide what's next or how to stay consistent.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {problems.map((p) => (
                        <div key={p.title} className="inspiration-card border-red-500/10 hover:border-red-500/30">
                            <div className="w-16 h-16 rounded-2xl bg-red-500/5 flex items-center justify-center mb-6">
                                {p.icon}
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3 tracking-tight">{p.title}</h3>
                            <p className="text-neutral-500 text-sm leading-relaxed font-light">{p.description}</p>
                        </div>
                    ))}
                </div>

                {/* Before/After Split */}
                <div className="mt-20 grid grid-cols-1 md:grid-cols-2 gap-px bg-neutral-900 rounded-[2rem] overflow-hidden border border-neutral-900">
                    <div className="bg-black p-12 flex flex-col items-center justify-center text-center">
                        <span className="text-[10px] font-bold text-red-500 uppercase tracking-widest mb-4">Old Workflow</span>
                        <div className="space-y-3 w-full max-w-xs opacity-40">
                            <div className="h-4 bg-neutral-900 rounded-full w-3/4 mx-auto"></div>
                            <div className="h-4 bg-neutral-900 rounded-full w-1/2 mx-auto"></div>
                            <div className="h-4 bg-neutral-900 rounded-full w-5/6 mx-auto"></div>
                        </div>
                        <p className="mt-8 text-neutral-500 text-sm">Messy, overwhelming, and unranked.</p>
                    </div>
                    <div className="bg-neutral-950 p-12 flex flex-col items-center justify-center text-center relative overflow-hidden group">
                        <div className="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest mb-4">TaskFlow Sync</span>
                        <div className="space-y-3 w-full max-w-xs">
                            <div className="h-4 bg-emerald-500/20 rounded-full w-3/4 mx-auto border border-emerald-500/20"></div>
                            <div className="h-4 bg-emerald-500/10 rounded-full w-1/2 mx-auto border border-emerald-500/10"></div>
                            <div className="h-4 bg-emerald-500/10 rounded-full w-5/6 mx-auto border border-emerald-500/10"></div>
                        </div>
                        <p className="mt-8 text-emerald-400 text-sm">Clean, high-priority focus mode.</p>
                    </div>
                </div>
            </div>
        </section>
    );
}
