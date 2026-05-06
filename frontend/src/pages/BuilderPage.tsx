import { useState, useEffect, type FormEvent } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import ComponentSelector from '../components/ComponentSelector.tsx';
import BuildCard from '../components/BuildCard.tsx';
import BuildSummaryPanel from '../components/BuildSummaryPanel';
import CreateBuildModal from '../components/CreateBuildModal';
import type { Build, Product } from '../types';
import { BUILD_GOALS, COMPONENT_CATEGORIES } from '../types';
import apiClient from '../lib/apiClient';
import { getUser } from '../lib/auth';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';

export default function BuilderPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const buildId = searchParams.get('buildId');

    const [build, setBuild] = useState<Build | null>(null);
    const [loading, setLoading] = useState(buildId ? true : false);
    const [builds, setBuilds] = useState<Build[]>([]);
    const [loadingBuilds, setLoadingBuilds] = useState<boolean>(true);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newBuildName, setNewBuildName] = useState('');
    const [newBuildBudget, setNewBuildBudget] = useState('');
    const [newBuildGoal, setNewBuildGoal] = useState('balanced');
    const [creating, setCreating] = useState(false);
    const user = getUser();

    useEffect(() => {
        if (buildId) {
            fetchBuild(parseInt(buildId));
        } else {
            // When navigating to /builder without buildId, ensure previous build view is cleared.
            setBuild(null);
            setSelectedCategory(null);
            setLoading(false);
        }
        // also fetch user's builds for dashboard view
        fetchBuilds();
    }, [buildId]);

    const fetchBuilds = async () => {
        setLoadingBuilds(true);
        try {
            const response = await apiClient.get('/builder/builds');
            setBuilds(response.data);
        } catch (error: any) {
            console.log('Could not fetch builds:', error);
            setBuilds([]);
        } finally {
            setLoadingBuilds(false);
        }
    };

    const fetchBuild = async (id: number) => {
        setLoading(true);
        try {
            const response = await apiClient.get(`/builder/${id}`);
            setBuild(response.data);
        } catch (error) {
            toast.error('Failed to load build');
            navigate('/builder');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateNewBuild = () => {
        setShowCreateForm(true);
    };

    const handleCreateBuild = async (e: FormEvent) => {
        e.preventDefault();
        setCreating(true);

        try {
            const response = await apiClient.post('/builder/create', {
                name: newBuildName || `Build ${new Date().toLocaleDateString()}`,
                budget: newBuildBudget ? parseInt(newBuildBudget) : null,
                goal: newBuildGoal,
            });

            setBuild(response.data);
            setShowCreateForm(false);
            setNewBuildName('');
            setNewBuildBudget('');
            setNewBuildGoal('balanced');
            toast.success('New build created');
            navigate(`/builder?buildId=${response.data.id}`);
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to create build';
            toast.error(message);
        } finally {
            setCreating(false);
        }
    };

    const handleSelectComponent = async (product: Product) => {
        if (!build) return;

        try {
            const response = await apiClient.post(`/builder/${build.id}/add`, {
                category: selectedCategory,
                product_id: product.product_id,
            });
            setBuild(response.data);
            toast.success(`${selectedCategory} added successfully!`);
            // Keep selector open briefly to show confirmation
            setTimeout(() => {
                setSelectedCategory(null);
            }, 800);
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to add component';
            toast.error(message);
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

    const handleRemoveComponent = () => {
        // This will be called by BuildSummaryPanel
    };

    const handleBuildUpdate = (updatedBuild: Build) => {
        setBuild(updatedBuild);
    };

    if (!build && !loading) {
        return (
            <Layout>
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

                <div className="mb-8">
                    <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5 mb-8">
                        <div>
                            <h1 className="text-4xl font-bold">Dashboard</h1>
                            <p className="text-sm text-[color:var(--text-soft)] mt-2">Welcome back, {user?.username}! Manage your PC builds here.</p>
                        </div>
                        <button
                            onClick={handleCreateNewBuild}
                            className="inline-flex items-center gap-2 min-h-11 btn-primary"
                        >
                            <Plus className="w-4 h-4" />
                            Create a build
                        </button>
                    </div>

                    {/* Builds Grid */}
                    {loadingBuilds ? (
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
                            {builds.map((b) => (
                                <BuildCard key={b.id} build={b} onOpen={handleOpenBuild} onDelete={handleDeleteBuild} />
                            ))}
                        </div>
                    )}
                </div>
            </Layout>
        );
    }

    if (loading) {
        return (
            <Layout>
                <div className="space-y-6">
                    <div className="soft-card p-6">
                        <div className="skeleton-line w-48 mb-3" />
                        <div className="skeleton-line w-full h-4 mb-2" />
                        <div className="skeleton-line w-56 h-4" />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2 space-y-4">
                            {Array.from({ length: 3 }).map((_, i) => (
                                <div key={i} className="soft-card p-6 animate-pulse">
                                    <div className="skeleton-line w-40 mb-4" />
                                    <div className="skeleton-line w-full h-4 mb-2" />
                                    <div className="skeleton-line w-32 h-4" />
                                </div>
                            ))}
                        </div>

                        <div>
                            <div className="soft-card p-6 animate-pulse">
                                <div className="skeleton-line w-36 mb-4" />
                                <div className="skeleton-line w-full h-4 mb-2" />
                                <div className="skeleton-line w-20 h-4" />
                            </div>
                        </div>
                    </div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
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

            <div className="mb-8">
                <div className="flex items-start justify-between gap-6">
                    <div>
                        <h1 className="text-4xl font-bold">{build?.name}</h1>
                        <p className="text-sm text-[color:var(--text-soft)] mt-2">Configure your PC by selecting components for each category.</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button onClick={() => handleCreateNewBuild()} className="min-h-11 btn-secondary">Create a build</button>
                        <button onClick={() => { if (build) { /* save handled in summary */ } }} className="min-h-11 btn-accent">Preview</button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content - Component Selection */}
                <div className="lg:col-span-2 space-y-4">
                    {COMPONENT_CATEGORIES.map((category) => {
                        const selectedComp = build?.selected_components[category];
                        const isMissing = !selectedComp;
                        const isExpanded = selectedCategory === category;

                        return (
                            <div key={category} className="soft-card p-6 border border-[var(--border-soft)] rounded-xl transition-all duration-200 hover:-translate-y-[2px] hover:shadow-[var(--shadow-elevated)]">
                                <div className="flex items-start justify-between mb-4 gap-4">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-semibold capitalize truncate">{category}</h3>
                                        <p className="text-sm text-[color:var(--text-soft)] mt-2 truncate">{selectedComp ? selectedComp.name : 'No component selected'}</p>
                                    </div>
                                    {selectedComp && (
                                        <p className="text-lg font-bold text-[color:var(--text-main)]">${selectedComp.price}</p>
                                    )}
                                </div>

                                {selectedComp && (
                                    <div className="mb-4 p-3 muted-panel rounded-md">
                                        <p className="text-xs text-[color:var(--text-soft)] mb-1">Selected</p>
                                        <p className="text-sm font-medium truncate">{selectedComp.name}</p>
                                    </div>
                                )}

                                <button
                                    onClick={() => {
                                        setSelectedCategory((current) => (current === category ? null : category));
                                    }}
                                    className={`w-full min-h-11 font-medium flex items-center justify-center gap-2 ${isMissing ? 'btn-primary' : 'btn-secondary'} transition-all duration-150`}
                                >
                                    <Plus className="w-4 h-4" />
                                    {selectedComp ? 'Change' : 'Select'} {category}
                                </button>

                                {isExpanded && build?.id && (
                                    <div className="mt-4 animate-in fade-in duration-200">
                                        <ComponentSelector
                                            buildId={build.id}
                                            category={category}
                                            selectedProduct={selectedComp || null}
                                            onSelect={handleSelectComponent}
                                            onClose={() => setSelectedCategory(null)}
                                            buildGoal={build.goal}
                                            buildBudget={build.budget}
                                        />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Sidebar - Build Summary */}
                <aside>
                    {build && (
                        <BuildSummaryPanel build={build} onBuildUpdate={handleBuildUpdate} onRemoveComponent={handleRemoveComponent} />
                    )}
                </aside>
            </div>

        </Layout>
    );
}



