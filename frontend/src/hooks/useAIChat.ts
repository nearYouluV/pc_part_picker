import { useState, useCallback } from 'react';
import { aiChatAPI } from '../lib/apiClient';
import { toast } from 'sonner';
import { aiTaskAPI } from '../lib/apiClient';

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

interface UseAIChatReturn {
    chatId: string | null;
    messages: ChatMessage[];
    loading: boolean;
    error: string | null;
    createChat: (buildId: number) => Promise<string | null>;
    sendMessage: (message: string) => Promise<void>;
    clearChat: () => void;
}

export function useAIChat(): UseAIChatReturn {
    const [chatId, setChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Poll for task completion
    const pollTaskStatus = async (
        taskId: string,
        maxAttempts: number = 300,
        interval: number = 1000
    ) => {
        let attempts = 0;

        while (attempts < maxAttempts) {
            try {
                const taskStatus = await aiTaskAPI.getTaskStatus(taskId);

                if (taskStatus.status === 'completed') {
                    return taskStatus.result;
                } else if (taskStatus.status === 'failed') {
                    throw new Error(taskStatus.error || 'AI request failed');
                }

                await new Promise(resolve => setTimeout(resolve, interval));
                attempts++;
            } catch (err) {
                throw err;
            }
        }

        throw new Error('AI request timeout');
    };

    const createChat = useCallback(async (buildId: number) => {
        setLoading(true);
        setError(null);

        try {
            const result = await aiChatAPI.createChat(buildId);
            setChatId(result.id);
            setMessages([]);
            return result.id;
        } catch (err: any) {
            const errorMessage = err?.response?.data?.detail || 'Failed to create chat';
            setError(errorMessage);
            toast.error(errorMessage);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const sendMessage = useCallback(
        async (message: string) => {
            if (!chatId) {
                toast.error('Chat not initialized');
                return;
            }

            setLoading(true);
            setError(null);

            try {
                // Add user message immediately
                setMessages(prev => [...prev, { role: 'user', content: message }]);

                // Dispatch task and poll for result
                const taskResponse = await aiChatAPI.sendMessage(chatId, message);
                const response = await pollTaskStatus(taskResponse.task_id);

                // Add assistant message with response
                setMessages(prev => [...prev, { role: 'assistant', content: response.answer }]);
            } catch (err: any) {
                const errorMessage = err?.response?.data?.detail || 'Failed to send message';
                setError(errorMessage);
                toast.error(errorMessage);
                // Remove the user message that was added
                setMessages(prev => prev.slice(0, -1));
            } finally {
                setLoading(false);
            }
        },
        [chatId]
    );

    const clearChat = useCallback(() => {
        setChatId(null);
        setMessages([]);
        setError(null);
    }, []);

    return {
        chatId,
        messages,
        loading,
        error,
        createChat,
        sendMessage,
        clearChat,
    };
}
