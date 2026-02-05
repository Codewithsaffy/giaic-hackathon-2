'use client';

export function SocialProof() {
    const stats = [
        { label: "Tasks Completed Daily", value: "10,000+" },
        { label: "Productivity Increase", value: "40%" },
        { label: "Habits Transformed", value: "100k+" },
    ];

    return (
        <div className="w-full border-y border-neutral-900 bg-black/50 backdrop-blur-md py-12 px-6">
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-12">
                <div className="text-center md:text-left">
                    <p className="text-sm font-bold tracking-[0.2em] text-neutral-500 uppercase mb-2">Trusted by 3,000+ professionals</p>
                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-8 opacity-40 grayscale contrast-125">
                        {/* Simple placeholders for logos */}
                        <span className="text-xl font-black font-heading text-white tracking-tighter">QUANTUM</span>
                        <span className="text-xl font-black font-heading text-white tracking-tighter">VERTEX</span>
                        <span className="text-xl font-black font-heading text-white tracking-tighter">ORBIT.</span>
                        <span className="text-xl font-black font-heading text-white tracking-tighter">FLUX</span>
                    </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 md:gap-16">
                    {stats.map((stat) => (
                        <div key={stat.label} className="text-center md:text-right">
                            <div className="text-3xl font-bold font-heading text-white mb-1">{stat.value}</div>
                            <div className="text-[10px] uppercase font-bold tracking-[0.2em] text-neutral-500">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
