import { useEffect, useState } from 'react';
import { SCRAPING_CATEGORIES } from '../types';
import apiClient from '../lib/apiClient';
import { Loader2, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

export default function ScrapingPanel() {
    const [selectedCategory, setSelectedCategory] = useState('cpu');
    const [loading, setLoading] = useState(false);
    const [lastTaskId, setLastTaskId] = useState<string | null>(null);
    const [lastStatus, setLastStatus] = useState<string | null>(null);
    const [lastCategory, setLastCategory] = useState<string | null>(null);

    useEffect(() => {
        if (!lastTaskId || !lastStatus || ['completed', 'failed'].includes(lastStatus)) {
            return;
        }

        let cancelled = false;
        const intervalId = window.setInterval(async () => {
            try {
                const response = await apiClient.get(`/scraping/status/${lastTaskId}`);
                if (cancelled) return;

                setLastStatus(response.data.status);
                if (response.data.category) {
                    setLastCategory(response.data.category);
                }

                if (['completed', 'failed'].includes(response.data.status)) {
                    window.clearInterval(intervalId);
                }
            } catch {
                // Keep the latest known status if polling fails transiently.
            }
        }, 3000);

        return () => {
            cancelled = true;
            window.clearInterval(intervalId);
        };
    }, [lastTaskId, lastStatus]);

    const handleTriggerScraping = async () => {
        setLoading(true);
        try {
            const response = await apiClient.post('/scraping/trigger', {
                category: selectedCategory,
            });

            setLastTaskId(response.data.task_id);
            setLastStatus(response.data.status);
            setLastCategory(response.data.category);
            toast.success(`Scraping triggered for ${selectedCategory}`);
        } catch (error: any) {
            const message =
                error.response?.data?.detail || 'Failed to trigger scraping';
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="soft-card p-6 md:p-7">
            <h2 className="text-xl font-semibold mb-5">Trigger Scraping</h2>

            <div className="space-y-5">
                <div>
                    <label className="block text-sm font-semibold mb-2">Select Category</label>
                    <select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        disabled={loading}
                        className="select-premium"
                    >
                        {SCRAPING_CATEGORIES.map((cat) => (
                            <option key={cat} value={cat}>
                                {cat.toUpperCase()}
                            </option>
                        ))}
                    </select>
                </div>

                <button
                    onClick={handleTriggerScraping}
                    disabled={loading}
                    className="w-full min-h-11 btn-accent disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Scraping...
                        </>
                    ) : (
                        'Trigger Scraping'
                    )}
                </button>

                {lastTaskId && (
                    <div className="p-4 muted-panel">
                        <div className="flex items-start gap-3 mb-2">
                            <CheckCircle className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                            <div>
                                <p className="font-medium">Scraping {lastStatus === 'completed' ? 'Completed' : lastStatus === 'failed' ? 'Failed' : 'In Progress'}</p>
                                <p className="text-sm text-[color:var(--text-soft)]">Category: {(lastCategory || selectedCategory).toUpperCase()}</p>
                            </div>
                        </div>
                        <div className="mt-3 p-2.5 bg-white rounded-lg border border-[var(--border-soft)]">
                            <p className="text-xs text-[color:var(--text-soft)]">Task ID:</p>
                            <p className="text-xs font-mono break-all">{lastTaskId}</p>
                        </div>
                        <p className="text-xs text-[color:var(--text-soft)] mt-2">Status: <span className="font-semibold capitalize text-[color:var(--text-main)]">{lastStatus}</span></p>
                    </div>
                )}

                <div className="p-4 muted-panel">
                    <p className="text-sm text-[color:var(--text-soft)]">Scraping tasks are processed asynchronously. The selected category will be scraped and products will be added to the database.</p>
                </div>
            </div>
        </div>
    );
}
