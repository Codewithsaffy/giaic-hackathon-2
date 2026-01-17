'use client';

import { useState, useRef, useEffect } from 'react';
import { X, Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useChatContext } from './chat-provider';
import { useSession } from '@/lib/auth-client';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
}

export function ChatSidebar() {
    const { isOpen, toggle } = useChatContext();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const { data: session } = useSession();

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/chat/simple', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    user_id: session?.user?.id,
                    session_id: session?.user?.id || 'anonymous' // Use user ID as session ID for persistence
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch response');
            }

            const data = await response.json();
            const agentMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
            };

            setMessages((prev) => [...prev, agentMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {/* Backdrop */}
            <div
                className={cn(
                    "fixed inset-0 bg-black/40 backdrop-blur-sm z-50 transition-opacity duration-300",
                    isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
                )}
                onClick={toggle}
            />

            {/* Sidebar Panel */}
            <div
                className={cn(
                    "fixed top-0 right-0 h-full w-[400px] z-50 transform transition-transform duration-300 ease-in-out border-l border-white/10 bg-[#0A0A0A]/95 backdrop-blur-xl shadow-2xl flex flex-col",
                    isOpen ? "translate-x-0" : "translate-x-full"
                )}
            >
                {/* Header */}
                <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-white/[0.02]">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <div>
                            <h2 className="font-heading font-semibold text-white tracking-wide">Gemini Agent</h2>
                            <p className="text-xs text-neutral-400 font-mono">v1.0 • Online</p>
                        </div>
                    </div>
                    <button
                        onClick={toggle}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors text-neutral-400 hover:text-white"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6" ref={scrollRef}>
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-50">
                            <Bot className="w-16 h-16 text-neutral-600 mb-4" />
                            <h3 className="text-lg font-medium text-white mb-2">How can I help?</h3>
                            <p className="text-sm text-neutral-400 max-w-[250px]">
                                I'm your AI assistant. Ask me anything about your tasks or projects.
                            </p>
                        </div>
                    )}

                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={cn(
                                "flex gap-3 max-w-[90%]",
                                msg.role === 'user' ? "ml-auto flex-row-reverse" : ""
                            )}
                        >
                            {/* Avatar */}
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1",
                                msg.role === 'assistant'
                                    ? "bg-gradient-to-br from-neutral-800 to-neutral-900 border border-white/10"
                                    : "bg-white text-black"
                            )}>
                                {msg.role === 'assistant' ? <Bot className="w-4 h-4 text-indigo-400" /> : <User className="w-4 h-4" />}
                            </div>

                            {/* Bubble */}
                            <div className={cn(
                                "rounded-2xl p-4 text-sm leading-relaxed",
                                msg.role === 'assistant'
                                    ? "bg-neutral-900/50 border border-white/5 text-neutral-200"
                                    : "bg-white text-black font-medium",
                                "whitespace-pre-wrap" // Respect newlines and spacing
                            )}>
                                {msg.content}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-3 max-w-[90%]">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neutral-800 to-neutral-900 border border-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                                <Bot className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div className="bg-neutral-900/50 border border-white/5 rounded-2xl p-4 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-indigo-400/50 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                <span className="w-1.5 h-1.5 bg-indigo-400/50 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                <span className="w-1.5 h-1.5 bg-indigo-400/50 rounded-full animate-bounce"></span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input */}
                <div className="p-4 border-t border-white/5 bg-[#0A0A0A]/50">
                    <form
                        onSubmit={handleSubmit}
                        className="relative flex items-center gap-2 bg-neutral-900/50 border border-white/10 rounded-2xl p-2 focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all"
                    >
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-sm placeholder:text-neutral-500 text-white px-2 py-1 outline-none"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="p-2 bg-white text-black rounded-xl hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        </button>
                    </form>
                    <div className="text-[10px] text-center text-neutral-600 mt-2 font-mono">
                        AI can make mistakes. Check important info.
                    </div>
                </div>
            </div>
        </>
    );
}
