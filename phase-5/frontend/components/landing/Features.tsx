'use client';

import { Bot, Calendar, Share2, BarChart3, Smartphone, Lock } from 'lucide-react';

export function Features() {
    const features = [
        {
            title: "AI Task Assistant",
            description: "AI drafts descriptions, suggests due dates, and highlights risks automatically using advanced semantic analysis.",
            icon: <Bot className="w-6 h-6" />,
            tag: "CORE AI"
        },
        {
            title: "Smart Scheduling",
            description: "AI creates personalized weekly schedules considering priorities, deadlines, and your energy patterns.",
            icon: <Calendar className="w-6 h-6" />,
            tag: "AUTOMATION"
        },
        {
            title: "Works With Your Tools",
            description: "Seamless integration with Google Calendar, Slack, and Gmail. Your workflow, unified.",
            icon: <Share2 className="w-6 h-6" />,
            tag: "ECOSYSTEM"
        },
        {
            title: "Progress Analytics",
            description: "Visual dashboards showing completion trends and productivity patterns based on your behavior.",
            icon: <BarChart3 className="w-6 h-6" />,
            tag: "INSIGHTS"
        },
        {
            title: "Mobile First",
            description: "Native apps for iOS and Android with offline mode. Keep your flow consistent everywhere.",
            icon: <Smartphone className="w-6 h-6" />,
            tag: "PLATFORM"
        },
        {
            title: "Secure & Private",
            description: "End-to-end encryption. Your tasks, your data, your privacy—guaranteed by enterprise standards.",
            icon: <Lock className="w-6 h-6" />,
            tag: "SECURITY"
        }
    ];

    return (
        <section className="py-24 px-6 relative">
            <div className="max-w-7xl mx-auto">
                <div className="mb-20">
                    <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-[0.3em] mb-4 block">Capabilities</span>
                    <h2 className="text-4xl md:text-6xl font-black font-heading text-white">
                        Everything You Need.<br />
                        <span className="opacity-40">Nothing You Don't.</span>
                    </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((f) => (
                        <div key={f.title} className="inspiration-card group relative">
                            <div className="absolute top-6 right-6">
                                <span className="text-[9px] font-bold tracking-widest text-neutral-600 group-hover:text-emerald-500 transition-colors uppercase">{f.tag}</span>
                            </div>
                            <div className="w-12 h-12 rounded-xl bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white mb-8 group-hover:border-emerald-500/50 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.1)] transition-all">
                                {f.icon}
                            </div>
                            <h3 className="text-xl font-bold text-white mb-4">{f.title}</h3>
                            <p className="text-neutral-500 text-sm leading-relaxed font-light">{f.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
