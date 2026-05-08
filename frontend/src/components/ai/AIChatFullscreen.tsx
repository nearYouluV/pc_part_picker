import { useState, useRef, useEffect } from 'react';
import { ChevronLeft, X, Send, Loader2 } from 'lucide-react';
import { AIMessage } from './AIMessage';
import type { AIChatChange, Build } from '../../types';

interface AIChatFullscreenProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onBack?: () => void;
    chatMessages: Array<{ role: 'user' | 'assistant'; content: string; changes?: AIChatChange[] }>;
    build: Build | null;
    recentChanges?: AIChatChange[];
    onSendMessage: (message: string) => Promise<void>;
    loading: boolean;
    variant?: 'modal' | 'page';
}

export function AIChatFullscreen({
    open,
    onOpenChange,
    onBack,
    chatMessages,
    build,
    recentChanges = [],
    onSendMessage,
    loading,
    variant = 'modal',
}: AIChatFullscreenProps) {
    const formatPrice = (value?: number | null) => (typeof value === 'number' ? `UAH ${value.toLocaleString()}` : 'Price unavailable');

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

    const buildComponents = build ? Object.entries(build.selected_components) : [];
    const budgetDelta = build && build.budget ? build.budget - build.total_price : null;

    const isPage = variant === 'page';

    return (
        <div className={isPage ? 'min-h-[calc(100vh-2rem)]' : 'chat-window-overlay'}>
            <div className={isPage ? 'chat-window-shell chat-window-page min-h-[calc(100vh-2rem)]' : 'chat-window-shell chat-window-modal absolute inset-0'}>
                {/* Header */}
                <div className="chat-window-header px-6 py-4 flex-shrink-0">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <h2 className="text-xl font-semibold text-[var(--text-main)]">
                                AI Assistant
                            </h2>
                            {build && (
                                <p className="text-sm text-[var(--text-soft)] mt-1">
                                    Chat about {build.name}
                                </p>
                            )}
                        </div>
                        <button
                            onClick={() => (isPage ? onBack?.() : onOpenChange(false))}
                            className="inline-flex items-center gap-2 px-3 py-2 hover:bg-[var(--surface-muted)] rounded-lg transition-colors flex-shrink-0 text-sm font-medium text-[var(--text-soft)]"
                        >
                            {isPage ? <ChevronLeft className="w-4 h-4" /> : <X className="w-5 h-5 text-[var(--text-soft)]" />}
                            {isPage ? 'Back to Builder' : ''}
                        </button>
                    </div>
                </div>

                {/* Body */}
                <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-0">
                    {/* Left: Current Build */}
                    <aside className="chat-window-sidebar hidden lg:flex flex-col min-h-0">
                        <div className="px-5 py-4 border-b border-[var(--border-soft)]">
                            <h3 className="text-sm font-semibold uppercase tracking-wide text-[var(--text-soft)]">Current Build</h3>
                            {build ? (
                                <>
                                    <p className="mt-2 text-base font-semibold text-[var(--text-main)] truncate">{build.name}</p>
                                    <p className="text-xs text-[var(--text-soft)]">Goal: {build.goal}</p>
                                </>
                            ) : (
                                <p className="mt-2 text-sm text-[var(--text-soft)]">No active build selected</p>
                            )}
                        </div>

                        {build && (
                            <>
                                {recentChanges.length > 0 && (
                                    <div className="px-5 py-4 border-b border-[var(--border-soft)] bg-[#13283d]">
                                        <h3 className="text-sm font-semibold uppercase tracking-wide text-[var(--text-soft)]">Latest AI change</h3>
                                        <div className="mt-3 space-y-2">
                                            {recentChanges.map((change) => (
                                                <div key={`${change.category}-${change.product_id}`} className="rounded-lg border border-[var(--border-soft)] bg-[#182a3e] px-3 py-2">
                                                    <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-soft)]">{change.category}</p>
                                                    <div className="mt-2 space-y-2">
                                                        <div className="chat-change-card">
                                                            {change.from_component?.image_small ? (
                                                                <img src={change.from_component.image_small} alt={change.from_component.name || 'Previous component'} className="chat-change-thumb" />
                                                            ) : (
                                                                <div className="chat-change-thumb chat-change-thumb-fallback">Old</div>
                                                            )}
                                                            <div className="min-w-0">
                                                                <p className="chat-change-label">Replaced</p>
                                                                <p className="chat-change-name" title={change.from_component?.name || change.from_name || 'Previous component'}>
                                                                    {change.from_component?.name || change.from_name || 'Previous component'}
                                                                </p>
                                                                <p className="chat-change-price">{formatPrice(change.from_component?.price)}</p>
                                                            </div>
                                                        </div>

                                                        <div className="chat-change-card">
                                                            {change.to_component?.image_small ? (
                                                                <img src={change.to_component.image_small} alt={change.to_component.name || 'New component'} className="chat-change-thumb" />
                                                            ) : (
                                                                <div className="chat-change-thumb chat-change-thumb-fallback">New</div>
                                                            )}
                                                            <div className="min-w-0">
                                                                <p className="chat-change-label">Now using</p>
                                                                <p className="chat-change-name" title={change.to_component?.name || change.to_name || 'New component'}>
                                                                    {change.to_component?.name || change.to_name || 'New component'}
                                                                </p>
                                                                <p className="chat-change-price">{formatPrice(change.to_component?.price)}</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    {change.reason && (
                                                        <p className="mt-1 text-xs text-[var(--text-soft)]">{change.reason}</p>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="px-5 py-4 border-b border-[var(--border-soft)] bg-[var(--surface-soft)]">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-[var(--text-soft)]">Total</span>
                                        <span className="font-semibold text-[var(--text-main)]">₴{build.total_price.toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center justify-between text-sm mt-1">
                                        <span className="text-[var(--text-soft)]">Budget</span>
                                        <span className="font-semibold text-[var(--text-main)]">
                                            {build.budget ? `₴${build.budget.toLocaleString()}` : 'Flexible'}
                                        </span>
                                    </div>
                                    {budgetDelta !== null && (
                                        <p className={`mt-2 text-xs ${budgetDelta >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                                            {budgetDelta >= 0
                                                ? `Under budget by ₴${Math.abs(budgetDelta).toLocaleString()}`
                                                : `Over budget by ₴${Math.abs(budgetDelta).toLocaleString()}`}
                                        </p>
                                    )}
                                </div>

                                <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-2">
                                    {buildComponents.length === 0 ? (
                                        <p className="text-sm text-[var(--text-soft)] px-1">No components selected yet</p>
                                    ) : (
                                        buildComponents.map(([category, comp]) => (
                                            <div key={category} className="chat-window-sidebar-card rounded-lg border px-3 py-2">
                                                <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-soft)]">{category}</p>
                                                <p className="text-sm text-[var(--text-main)] mt-1 truncate" title={comp.name}>{comp.name}</p>
                                                <div className="mt-1 flex items-center justify-between">
                                                    <p className="text-xs text-[var(--text-soft)]">₴{comp.price?.toLocaleString?.() ?? comp.price}</p>
                                                    {comp.source === 'ai' && (
                                                        <span className="text-[11px] font-semibold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">AI</span>
                                                    )}
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </>
                        )}
                    </aside>

                    {/* Right: Chat */}
                    <section className="min-h-0 flex flex-col">
                        <div className="chat-window-content flex-1 min-h-0 overflow-y-auto px-4 md:px-6 py-5">
                            <div className="max-w-3xl mx-auto space-y-4">
                                {chatMessages.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center min-h-full text-center py-8 md:py-12">
                                        <div className="chat-window-empty-icon w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                                            <span className="text-2xl">💬</span>
                                        </div>
                                        <h3 className="text-lg font-medium text-[var(--text-main)] mb-2">
                                            Start a conversation
                                        </h3>
                                        <p className="text-sm text-[var(--text-soft)] max-w-sm">
                                            Ask me anything about your PC build. I can help optimize parts, check compatibility, and explain trade-offs.
                                        </p>
                                        <div className="mt-6 space-y-2 text-left">
                                            <p className="text-xs font-medium text-[var(--text-soft)]">Try asking:</p>
                                            <ul className="text-xs text-[var(--text-soft)] space-y-1">
                                                <li>• Is this CPU powerful enough for gaming?</li>
                                                <li>• Will there be a bottleneck with this GPU?</li>
                                                <li>• Which part gives best FPS per price?</li>
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
                                                changes={msg.changes}
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

                        <div className="chat-window-footer p-4 md:p-5 flex-shrink-0">
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
                                    className="chat-window-input flex-1 px-4 py-3 rounded-lg disabled:bg-[#142436] disabled:opacity-70"
                                />
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!input.trim() || sending || loading}
                                    className="chat-window-send px-4 py-3 rounded-lg transition-colors flex items-center gap-2"
                                >
                                    {sending ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <Send className="w-4 h-4" />
                                    )}
                                </button>
                            </div>
                            <p className="text-xs text-[var(--text-soft)] mt-2 text-center">
                                Press Enter to send • Shift+Enter for new line
                            </p>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
