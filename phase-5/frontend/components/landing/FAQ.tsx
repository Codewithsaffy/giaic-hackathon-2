'use client';

import { Plus, Minus } from 'lucide-react';
import { useState } from 'react';

export function FAQ() {
    const faqs = [
        {
            q: "Can I migrate my existing tasks?",
            a: "Absolutely. We support direct imports from Todoist, Notion, Trello, and simple CSV files. Our AI migration tool will even try to categorize them automatically."
        },
        {
            q: "Does it work offline?",
            a: "Yes. TaskFlow is built with a local-first architecture. Work offline anywhere, and your changes will sync as soon as you reconnect to a deployment node."
        },
        {
            q: "How is this different from Todoist/Notion?",
            a: "Unlike traditional lists, TaskFlow focuses on consistency and habit building through AI analysis. We don't just help you list work; we help you find absolute flow."
        },
        {
            q: "Is my data secure?",
            a: "We use enterprise-grade end-to-end encryption. Your task descriptions and habit data are encrypted before they even leave your device."
        },
        {
            q: "Can I cancel anytime?",
            a: "Yes. No restrictive contracts. You can export your data and close your account with a single click at any time."
        }
    ];

    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <section className="py-24 px-6 bg-[#020202]">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-6xl font-black font-heading text-white mb-6">Common Questions</h2>
                    <p className="text-neutral-500 font-light">Everything you need to know about starting your flow.</p>
                </div>

                <div className="space-y-4">
                    {faqs.map((faq, idx) => (
                        <div
                            key={faq.q}
                            className={`inspiration-card !p-0 overflow-hidden transition-all duration-300 ${openIndex === idx ? 'border-emerald-500/30 ring-1 ring-emerald-500/20' : 'hover:border-neutral-700'}`}
                        >
                            <button
                                onClick={() => setOpenIndex(openIndex === idx ? null : idx)}
                                className="w-full px-8 py-6 flex items-center justify-between text-left group"
                            >
                                <span className={`text-lg font-bold tracking-tight transition-colors ${openIndex === idx ? 'text-emerald-400' : 'text-white'}`}>
                                    {faq.q}
                                </span>
                                <div className={`p-2 rounded-full transition-all ${openIndex === idx ? 'bg-emerald-500 text-black' : 'bg-neutral-900 text-neutral-500 group-hover:bg-neutral-800'}`}>
                                    {openIndex === idx ? <Minus className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                                </div>
                            </button>
                            <div className={`transition-all duration-300 ease-in-out ${openIndex === idx ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
                                <div className="px-8 pb-8 text-neutral-400 font-light leading-relaxed">
                                    {faq.a}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
