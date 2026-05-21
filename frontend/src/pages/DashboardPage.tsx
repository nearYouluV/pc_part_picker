import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Plus } from 'lucide-react';
import Layout from '../components/Layout';
import CommunityBuildCard from '../components/CommunityBuildCard';
import { communityAPI } from '../lib/apiClient';
import type { Build } from '../types';

export default function DashboardPage() {
    const navigate = useNavigate();
    const [builds, setBuilds] = useState<Build[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        const loadPublicBuilds = async () => {
            setLoading(true);
            try {
                const data = await communityAPI.getPublicBuilds();
                if (!mounted) return;
                setBuilds(Array.isArray(data) ? data : []);
            } catch {
                if (mounted) setBuilds([]);
            } finally {
                if (mounted) setLoading(false);
            }
        };

        void loadPublicBuilds();

        return () => {
            mounted = false;
        };
    }, []);

    return (
        <Layout>
            <div className="mb-8">
                <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5 mb-8">
                    <div>
                        <h1 className="text-4xl font-bold">Community Builds</h1>
                        <p className="text-sm text-[color:var(--text-soft)] mt-2">
                            Browse public builds shared by other users, then open any build to read reviews or leave your own rating.
                        </p>
                    </div>
                    <button
                        onClick={() => navigate('/builder')}
                        className="inline-flex items-center gap-2 min-h-11 btn-primary"
                    >
                        <Plus className="w-4 h-4" />
                        Go to Builder
                    </button>
                </div>

                {loading ? (
                    <div className="soft-card p-12 flex items-center justify-center">
                        <Loader2 className="w-6 h-6 animate-spin text-[color:var(--text-soft)]" />
                    </div>
                ) : builds.length === 0 ? (
                    <div className="soft-card p-10 text-center">
                        <h2 className="text-2xl font-semibold mb-3">No public builds yet</h2>
                        <p className="text-[color:var(--text-soft)] max-w-2xl mx-auto">
                            Publish one of your builds from the Builder page to start the community feed.
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        {builds.map((build) => (
                            <CommunityBuildCard key={build.id} build={build} />
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
}
