import { Markdown } from '../Markdown';
import type { AIChatChange } from '../../types';

interface AIMessageProps {
    role: 'user' | 'assistant';
    content: string;
    isLoading?: boolean;
    changes?: AIChatChange[];
}

function formatPrice(value?: number | null) {
    if (typeof value !== 'number') return null;
    return `UAH ${value.toLocaleString()}`;
}

export function AIMessage({ role, content, isLoading, changes = [] }: AIMessageProps) {
    const isUser = role === 'user';

    return (
        <div className={`flex w-full gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {/* Avatar */}
            {!isUser && (
                <div className="chat-message-avatar flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-medium">
                    AI
                </div>
            )}

            {/* Message bubble */}
            <div
                className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${isUser
                    ? 'chat-message-user rounded-br-none'
                    : 'chat-message-assistant rounded-bl-none'
                    }`}
            >
                {isLoading ? (
                    <div className="flex gap-1 items-center">
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                ) : isUser ? (
                    <p className="text-sm">{content}</p>
                ) : (
                    <>
                        <Markdown content={content} />
                        {changes.length > 0 && (
                            <div className="mt-3 space-y-2">
                                {changes.map((change, idx) => {
                                    const fromCard = change.from_component;
                                    const toCard = change.to_component;
                                    return (
                                        <div key={`${change.category}-${change.product_id}-${idx}`} className="chat-change-block">
                                            <p className="chat-change-title">{change.category} updated</p>
                                            <div className="chat-change-grid">
                                                <div className="chat-change-card">
                                                    {fromCard?.image_small ? (
                                                        <img src={fromCard.image_small} alt={fromCard.name || 'Previous component'} className="chat-change-thumb" />
                                                    ) : (
                                                        <div className="chat-change-thumb chat-change-thumb-fallback">Old</div>
                                                    )}
                                                    <div className="min-w-0">
                                                        <p className="chat-change-label">Replaced</p>
                                                        <p className="chat-change-name" title={fromCard?.name || change.from_name || 'Previous component'}>
                                                            {fromCard?.name || change.from_name || 'Previous component'}
                                                        </p>
                                                        <p className="chat-change-price">{formatPrice(fromCard?.price) || 'Price unavailable'}</p>
                                                    </div>
                                                </div>
                                                <div className="chat-change-card">
                                                    {toCard?.image_small ? (
                                                        <img src={toCard.image_small} alt={toCard.name || 'New component'} className="chat-change-thumb" />
                                                    ) : (
                                                        <div className="chat-change-thumb chat-change-thumb-fallback">New</div>
                                                    )}
                                                    <div className="min-w-0">
                                                        <p className="chat-change-label">Now using</p>
                                                        <p className="chat-change-name" title={toCard?.name || change.to_name || 'New component'}>
                                                            {toCard?.name || change.to_name || 'New component'}
                                                        </p>
                                                        <p className="chat-change-price">{formatPrice(toCard?.price) || 'Price unavailable'}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
