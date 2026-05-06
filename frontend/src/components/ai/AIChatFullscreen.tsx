import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2 } from 'lucide-react';
import { AIMessage } from './AIMessage';
import type { Build } from '../../types';

interface AIChatFullscreenProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    chatMessages: Array<{ role: 'user' | 'assistant'; content: string }>;
    build: Build | null;
    onSendMessage: (message: string) => Promise<void>;
    loading: boolean;
}

export function AIChatFullscreen({
    open,
    onOpenChange,
    chatMessages,
    build,
    onSendMessage,
    loading,
}: AIChatFullscreenProps) {
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatMessages, sending]);

    const handleSendMessage = async () => {
        if (!input.trim() || sending) return;

        const message = input;
        setInput('');
        setSending(true);

        try {
            await onSendMessage(message);
        } finally {
            setSending(false);
        }
    };

    if (!mounted || !open) return null;

    return (
        <div className="fixed inset-0 z-50 bg-black/50">
            <div className="absolute inset-0 bg-slate-50 flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0 shadow-sm">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <h2 className="text-xl font-semibold text-slate-900">
                                AI Assistant
                            </h2>
                            {build && (
                                <p className="text-sm text-slate-500 mt-1">
                                    Chat about {build.name} (Budget: ${build.budget?.toLocaleString() || 'Flexible'})
                                </p>
                            )}
                        </div>
                        <button
                            onClick={() => onOpenChange(false)}
                            className="p-2 hover:bg-slate-100 rounded-lg transition-colors flex-shrink-0"
                        >
                            <X className="w-5 h-5 text-slate-500" />
                        </button>
                    </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto px-6 py-6 bg-slate-50">
                    <div className="max-w-3xl mx-auto space-y-4">
                        {chatMessages.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center py-12">
                                <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
                                    <span className="text-2xl">💬</span>
                                </div>
                                <h3 className="text-lg font-medium text-slate-900 mb-2">
                                    Start a conversation
                                </h3>
                                <p className="text-sm text-slate-600 max-w-sm">
                                    Ask me anything about your PC build. I can help you optimize components, check compatibility, and answer hardware questions.
                                </p>
                                <div className="mt-6 space-y-2 text-left">
                                    <p className="text-xs font-medium text-slate-600">Try asking:</p>
                                    <ul className="text-xs text-slate-600 space-y-1">
                                        <li>• Is this CPU powerful enough for gaming?</li>
                                        <li>• Will there be a bottleneck with this GPU?</li>
                                        <li>• Should I upgrade anything for better performance?</li>
                                    </ul>
                                </div>
                            </div>
                        ) : (
                            <>
                                {chatMessages.map((msg, idx) => (
                                    <AIMessage
                                        key={idx}
                                        role={msg.role}
                                        content={msg.content}
                                    />
                                ))}
                                {sending && (
                                    <AIMessage
                                        role="assistant"
                                        content=""
                                        isLoading={true}
                                    />
                                )}
                                <div ref={messagesEndRef} />
                            </>
                        )}
                    </div>
                </div>

                {/* Input Area */}
                <div className="border-t border-slate-200 bg-white p-6 flex-shrink-0 shadow-sm">
                    <div className="max-w-3xl mx-auto flex gap-3">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSendMessage();
                                }
                            }}
                            placeholder="Ask about your build..."
                            disabled={sending || loading}
                            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:bg-slate-100"
                        />
                        <button
                            onClick={handleSendMessage}
                            disabled={!input.trim() || sending || loading}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg transition-colors flex items-center gap-2"
                        >
                            {sending ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Send className="w-4 h-4" />
                            )}
                        </button>
                    </div>
                    <p className="text-xs text-slate-500 mt-3 text-center">
                        Press Enter to send • Shift+Enter for new line
                    </p>
                </div>
            </div>
        </div>
    );
}
