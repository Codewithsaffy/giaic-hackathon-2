'use client';

import { Briefcase, User, GraduationCap } from 'lucide-react';

export function UseCases() {
    const personas = [
        {
            title: "Freelancers & Solopreneurs",
            description: "Juggle multiple clients and high-stakes projects without dropping the ball. TaskFlow acts as your virtual project manager.",
            icon: <Briefcase className="w-6 h-6" />,
            image: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&q=80&w=800"
        },
        {
            title: "Small Teams",
            description: "Coordinate complex sprints and stay aligned without endless meetings. Built for speed and absolute clarity.",
            icon: <User className="w-6 h-6" />,
            image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80&w=800"
        },
        {
            title: "Students & Professionals",
            description: "Balance work, learning, and personal goals in one unified flow. Achieve more while maintaining peak mental state.",
            icon: <GraduationCap className="w-6 h-6" />,
            image: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=800"
        }
    ];

    return (
        <section className="py-24 px-6 bg-[#020202]">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-20">
                    <h2 className="text-4xl md:text-6xl font-black font-heading text-white mb-6">
                        Built For How You Actually Work
                    </h2>
                    <p className="text-neutral-500 max-w-2xl mx-auto font-light leading-relaxed">
                        TaskFlow isn't a one-size-fits-all tool. It adapts to your role, your goals, and your specific productivity environment.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                    {personas.map((p) => (
                        <div key={p.title} className="group flex flex-col items-center text-center">
                            <div className="relative w-full aspect-[4/5] rounded-[2.5rem] overflow-hidden mb-8 border border-neutral-900 group-hover:border-emerald-500/30 transition-all duration-500">
                                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent z-10"></div>
                                <img
                                    src={p.image}
                                    alt={p.title}
                                    className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:scale-110 transition-transform duration-700 grayscale group-hover:grayscale-0"
                                />
                                <div className="absolute bottom-10 left-0 right-0 z-20 px-8">
                                    <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-white mx-auto mb-6">
                                        {p.icon}
                                    </div>
                                    <h3 className="text-2xl font-bold text-white mb-4">{p.title}</h3>
                                    <p className="text-neutral-400 text-sm leading-relaxed font-light opacity-0 group-hover:opacity-100 transition-opacity duration-500">{p.description}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
