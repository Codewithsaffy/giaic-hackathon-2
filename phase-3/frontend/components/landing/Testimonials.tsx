'use client';

import { Star, Quote } from 'lucide-react';

export function Testimonials() {
    const testimonials = [
        {
            name: "Sarah Chen",
            role: "Lead Designer at Vertex",
            text: "TaskFlow completely transformed how our design team syncs. The AI habit analysis caught patterns we didn't even know existed. Consistency is up 40%.",
            avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200"
        },
        {
            name: "Marcus Thorne",
            role: "Independent Consultant",
            text: "I've tried every task manager. This is the first one that doesn't feel like more work. It's an extension of my own brain. Absolute flow state.",
            avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=200"
        },
        {
            name: "Elena Rodriguez",
            role: "Engineering Manager",
            text: "The 'Focus Mode' is a game changer. We've eliminated 3 hours of trivial planning weekly. Finally, my team is working on what actually matters.",
            avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&q=80&w=200"
        }
    ];

    return (
        <section className="py-24 px-6 relative overflow-hidden">
            <div className="absolute top-1/2 left-0 w-full h-px bg-neutral-900 -z-10"></div>

            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col md:flex-row items-end justify-between mb-20 gap-8">
                    <div className="max-w-xl">
                        <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-[0.3em] mb-4 block">Social Proof</span>
                        <h2 className="text-4xl md:text-6xl font-black font-heading text-white">
                            Trusted by Those Who <br />
                            <span className="text-gradient-white">Build the Future.</span>
                        </h2>
                    </div>
                    <div className="flex gap-2 pb-2">
                        {[1, 2, 3, 4, 5].map((s) => <Star key={s} className="w-5 h-5 fill-emerald-500 text-emerald-500" />)}
                        <span className="ml-2 text-white font-bold tracking-tighter">4.9/5 RATING</span>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {testimonials.map((t) => (
                        <div key={t.name} className="inspiration-card relative group">
                            <Quote className="absolute top-6 right-6 w-8 h-8 text-neutral-800 opacity-20 group-hover:text-emerald-500 transition-colors" />
                            <p className="text-white text-lg font-light leading-relaxed mb-8 italic">"{t.text}"</p>
                            <div className="flex items-center gap-4">
                                <img src={t.avatar} alt={t.name} className="w-12 h-12 rounded-full border border-neutral-800 grayscale" />
                                <div>
                                    <h4 className="text-white font-bold text-sm tracking-tight">{t.name}</h4>
                                    <p className="text-neutral-500 text-[10px] uppercase font-bold tracking-widest">{t.role}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-20 text-center">
                    <div className="inline-flex items-center gap-4 px-6 py-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer group">
                        <span className="text-white font-bold text-sm">Read the full story: How Vertex boosted velocity by 40%</span>
                        <ArrowRight className="w-4 h-4 text-emerald-500 group-hover:translate-x-1 transition-transform" />
                    </div>
                </div>
            </div>
        </section>
    );
}

// Re-using ArrowRight for the Bottom component
function ArrowRight({ className }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
        </svg>
    );
}
