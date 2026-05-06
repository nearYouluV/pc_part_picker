import { Markdown } from '../Markdown';

interface AIMessageProps {
    role: 'user' | 'assistant';
    content: string;
    isLoading?: boolean;
}

export function AIMessage({ role, content, isLoading }: AIMessageProps) {
    const isUser = role === 'user';

    return (
        <div className={`flex w-full gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {/* Avatar */}
            {!isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-sm font-medium">
                    AI
                </div>
            )}

            {/* Message bubble */}
            <div
                className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${isUser
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-slate-100 text-slate-900 rounded-bl-none'
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
                    <Markdown content={content} />
                )}
            </div>
        </div>
    );
}
