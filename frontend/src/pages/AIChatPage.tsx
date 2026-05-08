import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { AIChatFullscreen } from '../components/ai/AIChatFullscreen';
import { useAIChat } from '../hooks/useAIChat';
import type { AIChatChange, Build } from '../types';
import apiClient from '../lib/apiClient';
import { toast } from 'sonner';

export default function AIChatPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const buildIdParam = searchParams.get('buildId');

    const [build, setBuild] = useState<Build | null>(null);
    const [loadingBuild, setLoadingBuild] = useState(true);
    const [recentChanges, setRecentChanges] = useState<AIChatChange[]>([]);

    const {
        messages,
        loading: chatLoading,
        createChat,
        loadHistory,
        sendMessage,
        clearChat,
    } = useAIChat();

    const loadBuildData = async (buildId: number) => {
        const response = await apiClient.get(`/builder/${buildId}`);
        setBuild(response.data);
        return response.data as Build;
    };

    useEffect(() => {
        if (!buildIdParam) {
            setBuild(null);
            setLoadingBuild(false);
            return;
        }

        const buildId = Number.parseInt(buildIdParam, 10);
        if (Number.isNaN(buildId)) {
            toast.error('Invalid build id');
            navigate('/builder');
            return;
        }

        let active = true;

        const loadBuild = async () => {
            setLoadingBuild(true);
            clearChat();
            setRecentChanges([]);

            try {
                if (!active) return;

                await loadBuildData(buildId);
                if (!active) return;

                const chatIdValue = await createChat(buildId);
                if (chatIdValue && active) {
                    await loadHistory(chatIdValue);
                }
            } catch (error) {
                if (!active) return;
                toast.error('Failed to load build chat');
                navigate('/builder');
            } finally {
                if (active) {
                    setLoadingBuild(false);
                }
            }
        };

        void loadBuild();

        return () => {
            active = false;
        };
    }, [buildIdParam, clearChat, createChat, loadHistory, navigate]);

    if (loadingBuild) {
        return (
            <Layout>
                <div className="soft-card p-8 animate-pulse">
                    <div className="skeleton-line w-40 mb-3" />
                    <div className="skeleton-line w-64 mb-2" />
                    <div className="skeleton-line w-full h-[60vh]" />
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold">AI Chat</h1>
                    <p className="text-sm text-[color:var(--text-soft)] mt-2">
                        Discuss the current build, ask follow-up questions, or request optimization advice.
                    </p>
                </div>
            </div>

            <AIChatFullscreen
                open={Boolean(build)}
                onOpenChange={() => navigate('/builder')}
                onBack={() => navigate(`/builder?buildId=${build?.id}`)}
                chatMessages={messages}
                build={build}
                recentChanges={recentChanges}
                onSendMessage={async (message) => {
                    const result = await sendMessage(message);
                    if (result?.changes?.length && build?.id) {
                        setRecentChanges(result.changes);
                        try {
                            await loadBuildData(build.id);
                        } catch {
                            toast.error('Updated build could not be reloaded');
                        }
                    } else {
                        setRecentChanges([]);
                    }
                }}
                loading={chatLoading}
                variant="page"
            />
        </Layout>
    );
}