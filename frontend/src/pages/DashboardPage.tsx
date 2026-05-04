import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import BuildCard from '../components/BuildCard';
import CreateBuildModal from '../components/CreateBuildModal';
import type { Build } from '../types';
import { BUILD_GOALS } from '../types';
import { getUser } from '../lib/auth';
import apiClient from '../lib/apiClient';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';

export default function DashboardPage() {
    const navigate = useNavigate();
    const user = getUser();
    const [builds, setBuilds] = useState<Build[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newBuildName, setNewBuildName] = useState('');
    const [newBuildBudget, setNewBuildBudget] = useState('');
    const [newBuildGoal, setNewBuildGoal] = useState('balanced');
    const [creating, setCreating] = useState(false);

    useEffect(() => {
        fetchBuilds();
    }, []);

    const fetchBuilds = async () => {
        setLoading(true);
        try {
            const response = await apiClient.get('/builder/builds');
            setBuilds(response.data);
        } catch (error: any) {
            // If endpoint doesn't exist, start with empty list
            console.log('Could not fetch builds:', error);
            setBuilds([]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateBuild = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreating(true);

        try {
            const response = await apiClient.post('/builder/create', {
                name: newBuildName || `Build ${new Date().toLocaleDateString()}`,
                budget: newBuildBudget ? parseInt(newBuildBudget) : null,
                goal: newBuildGoal,
            });

            setBuilds([response.data, ...builds]);
            setShowCreateForm(false);
            setNewBuildName('');
            setNewBuildBudget('');
            setNewBuildGoal('balanced');

            toast.success('Build created');

            // Navigate to builder with the new build
            navigate(`/builder?buildId=${response.data.id}`);
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to create build';
            toast.error(message);
        } finally {
            setCreating(false);
        }
    };

    const handleOpenBuild = (build: Build) => {
        navigate(`/builder?buildId=${build.id}`);
    };

    const handleDeleteBuild = async (buildId: number) => {
        if (!confirm('Are you sure you want to delete this build?')) return;

        try {
            await apiClient.delete(`/builder/${buildId}`);
            setBuilds(builds.filter((b) => b.id !== buildId));
            toast.success('Build deleted');
        } catch (error) {
            toast.error('Failed to delete build');
        }
    };

    return (
        <Layout>
            <div className="mb-8">
                <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5 mb-8">
                    <div>
                        <h1 className="text-4xl font-bold">Dashboard</h1>
                        <p className="text-sm text-[color:var(--text-soft)] mt-2">Welcome back, {user?.username}! Manage your PC builds here.</p>
                    </div>
                </div>

                {/* Create Build Modal */}
                <CreateBuildModal
                    show={showCreateForm}
                    onClose={() => setShowCreateForm(false)}
                    name={newBuildName}
                    setName={setNewBuildName}
                    budget={newBuildBudget}
                    setBudget={setNewBuildBudget}
                    goal={newBuildGoal}
                    setGoal={setNewBuildGoal}
                    creating={creating}
                    onSubmit={handleCreateBuild}
                    goals={BUILD_GOALS}
                />

                {/* Builds Grid */}
                {loading ? (
                    <div className="dashboard-builds-grid gap-6">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <div key={i} className="soft-card p-6 animate-pulse">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1">
                                        <div className="skeleton-line w-48" />
                                        <div className="skeleton-line w-32 mt-3" />
                                    </div>
                                    <div className="text-right">
                                        <div className="skeleton-line w-20 h-6" />
                                    </div>
                                </div>
                                <div className="skeleton-line w-full h-4 mb-3" />
                                <div className="flex gap-2">
                                    <div className="skeleton-line w-20 h-8 rounded-md" />
                                    <div className="skeleton-line w-10 h-8 rounded-md" />
                                </div>
                            </div>
                        ))}
                    </div>
                ) : builds.length === 0 ? (
                    <div className="soft-card p-12 text-center">
                        <div className="flex flex-col items-center gap-4">
                            <button
                                onClick={() => setShowCreateForm(true)}
                                className="h-16 w-16 rounded-full border border-[var(--border-strong)] bg-[var(--surface)] text-[color:var(--primary)] inline-flex items-center justify-center shadow-sm hover:shadow-md hover:-translate-y-[2px] transition-all duration-150"
                                aria-label="Create first build"
                            >
                                <Plus className="w-8 h-8" />
                            </button>
                            <p className="text-2xl font-semibold">No builds yet</p>
                            <p className="text-sm text-[color:var(--text-soft)] max-w-md mb-2">Create your first PC build to get started. We'll help with compatible parts and recommendations.</p>
                            <button
                                onClick={() => setShowCreateForm(true)}
                                className="inline-flex items-center gap-2 min-h-11 btn-primary"
                            >
                                <Plus className="w-4 h-4" />
                                Create First Build
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="dashboard-builds-grid gap-6">
                        {builds.map((build) => (
                            <BuildCard
                                key={build.id}
                                build={build}
                                onOpen={handleOpenBuild}
                                onDelete={handleDeleteBuild}
                            />
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
}
