import { useState, useEffect, type FormEvent } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import ComponentSelector from '../components/ComponentSelector.tsx';
import BuildCard from '../components/BuildCard.tsx';
import BuildSummaryPanel from '../components/BuildSummaryPanel';
import CreateBuildModal from '../components/CreateBuildModal';
import { AIBuildButton } from '../components/ai/AIBuildButton';
import { useAIBuild } from '../hooks/useAIBuild';
import type { Build, Product } from '../types';
import { BUILD_GOALS, COMPONENT_CATEGORIES } from '../types';
import apiClient from '../lib/apiClient';
import { getUser } from '../lib/auth';
import { Plus, MessageCircle } from 'lucide-react';
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
    const [componentQuantities, setComponentQuantities] = useState<Record<string, number>>({});

    // AI hooks
    const { loading: aiBuildLoading, generateBuild } = useAIBuild();

    const user = getUser();

    const categoryLabel = (category: string) => (category === 'cooler' ? 'Cooling' : category.charAt(0).toUpperCase() + category.slice(1));

    // AI Build handler
    const handleAIBuild = async () => {
        if (!build || !build.budget || !build.goal) {
            toast.error('Please set budget and goal first');
            return;
        }

        try {
            // Prepare candidates - get components from the builder recommendations
            // For now, we'll use empty candidates and let the backend provide them
            const candidates: Record<string, Product[]> = {};

            // Get selected components map
            const selectedComponents: Record<string, number> = {};
            for (const [category, component] of Object.entries(build.selected_components)) {
                if (component?.product_id) {
                    selectedComponents[category] = component.product_id;
                }
            }

            const result = await generateBuild(
                build.id,
                build.budget,
                build.goal,
                candidates,
                selectedComponents
            );

            if (result) {
                // Refresh build to see the new components
                await fetchBuild(build.id);
                toast.success('AI build generated successfully!');
            }
        } catch (error) {
            toast.error('Failed to generate AI build');
        }
    };

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

    useEffect(() => {
        if (!build) {
            setComponentQuantities({});
            return;
        }

        const nextQuantities: Record<string, number> = {};
        for (const [category, component] of Object.entries(build.selected_components)) {
            if (category === 'storage') {
                for (const storageItem of build.storage_components || []) {
                    nextQuantities[`storage:${storageItem.product_id}`] = Math.max(1, storageItem.quantity || 1);
                }
            } else {
                nextQuantities[category] = Math.max(1, component.quantity || 1);
            }
        }

        setComponentQuantities(nextQuantities);
    }, [build]);

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

    const handleSelectComponent = async (product: Product, quantity: number, append: boolean) => {
        if (!build) return;

        try {
            const response = await apiClient.post(`/builder/${build.id}/add`, {
                category: selectedCategory,
                product_id: product.product_id,
                quantity,
                append,
            });
            setBuild(response.data);
            toast.success(`${categoryLabel(selectedCategory || '')} updated successfully!`);
            // Keep selector open briefly to show confirmation
            setTimeout(() => {
                setSelectedCategory(null);
            }, 800);
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to add component';
            toast.error(message);
        }
    };

    const handleApplyQuantity = async (category: string, productId?: number) => {
        if (!build) return;

        const selectedComp = build.selected_components[category];
        const quantity = category === 'storage'
            ? getStorageQuantity(productId) ?? 1
            : getCategoryQuantity(category, selectedComp || null);

        const targetProductId = category === 'storage' ? productId : selectedComp?.product_id;

        if (!targetProductId) {
            toast.error('Select a component first');
            return;
        }

        try {
            const response = await apiClient.post(`/builder/${build.id}/add`, {
                category,
                product_id: targetProductId,
                quantity,
                append: category === 'storage',
            });
            setBuild(response.data);
            toast.success(`${categoryLabel(category)} quantity updated`);
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to update quantity';
            toast.error(message);
        }
    };

    const getStorageQuantity = (productId?: number | null) => {
        if (productId === null || productId === undefined) {
            return 1;
        }

        return componentQuantities[`storage:${productId}`] ?? build?.storage_components?.find((item) => item.product_id === productId)?.quantity ?? 1;
    };

    const setStorageQuantity = (productId: number, quantity: number) => {
        setComponentQuantities((current) => ({
            ...current,
            [`storage:${productId}`]: Math.max(1, Math.min(8, quantity)),
        }));
    };

    const handleOpenBuild = (build: Build) => {
        navigate(`/builder?buildId=${build.id}`);
    };

    const handleOpenAIChat = () => {
        if (!build) return;

        navigate(`/ai-chat?buildId=${build.id}`);
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

    const getCategoryQuantity = (category: string, selectedComp?: Product | null) => {
        return componentQuantities[category] ?? selectedComp?.quantity ?? 1;
    };

    const setCategoryQuantity = (category: string, quantity: number) => {
        setComponentQuantities((current) => ({
            ...current,
            [category]: Math.max(1, Math.min(8, quantity)),
        }));
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
                        const storageItems = category === 'storage' ? (build?.storage_components || []) : [];
                        const isMissing = !selectedComp;
                        const isExpanded = selectedCategory === category;
                        const label = categoryLabel(category);

                        return (
                            <div key={category} className="soft-card p-6 border border-[var(--border-soft)] rounded-xl transition-all duration-200 hover:-translate-y-[2px] hover:shadow-[var(--shadow-elevated)]">
                                <div className="flex items-start justify-between mb-4 gap-4">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-semibold truncate">{label}</h3>
                                        <div className="flex items-center gap-2">
                                            <p className="text-sm text-[color:var(--text-soft)] mt-2 truncate">
                                                {category === 'storage' && storageItems.length > 0
                                                    ? `${storageItems.length} drive${storageItems.length > 1 ? 's' : ''} selected`
                                                    : (selectedComp ? selectedComp.name : 'No component selected')}
                                            </p>
                                            {selectedComp?.source === 'ai' && (
                                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">AI</span>
                                            )}
                                        </div>
                                    </div>
                                    {(selectedComp || (category === 'storage' && storageItems.length > 0)) && (
                                        <p className="text-lg font-bold text-[color:var(--text-main)]">
                                            ₴{category === 'storage'
                                                ? storageItems.reduce((sum, item) => sum + (item.price || 0) * (item.quantity || 1), 0)
                                                : (selectedComp?.price || 0) * (selectedComp?.quantity || 1)}
                                        </p>
                                    )}
                                </div>

                                {(selectedComp || (category === 'storage' && storageItems.length > 0)) && (
                                    <div className="mb-4 p-3 muted-panel rounded-md">
                                        <p className="text-xs text-[color:var(--text-soft)] mb-1">Selected</p>
                                        {category === 'storage' ? (
                                            <div className="space-y-1">
                                                {storageItems.map((item) => (
                                                    <div
                                                        key={`${item.product_id}-${item.name}`}
                                                        className="w-full flex items-center justify-between gap-2 rounded-lg px-2 py-1"
                                                    >
                                                        <div className="min-w-0">
                                                            <p className="text-sm font-medium truncate">{item.name}</p>
                                                            <p className="text-xs text-[color:var(--text-soft)]">₴{(item.price || 0) * (item.quantity || 1)}</p>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <input
                                                                type="number"
                                                                min={1}
                                                                max={8}
                                                                value={getStorageQuantity(item.product_id)}
                                                                onChange={(e) => setStorageQuantity(item.product_id, Number.parseInt(e.target.value || '1', 10) || 1)}
                                                                className="input-premium w-20 text-right"
                                                            />
                                                            <button
                                                                type="button"
                                                                onClick={() => handleApplyQuantity('storage', item.product_id)}
                                                                className="h-10 px-3 rounded-lg bg-[var(--primary)] text-white text-sm font-semibold hover:opacity-90 transition-opacity"
                                                            >
                                                                Apply
                                                            </button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="flex items-center justify-between gap-2">
                                                <div className="min-w-0 flex items-center gap-2">
                                                    <p className="text-sm font-medium truncate">{selectedComp?.name}</p>
                                                    {selectedComp?.source === 'ai' && (
                                                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">AI</span>
                                                    )}
                                                </div>
                                                {category === 'ram' ? (
                                                    <div className="flex items-center gap-2">
                                                        <input
                                                            type="number"
                                                            min={1}
                                                            max={8}
                                                            value={getCategoryQuantity(category, selectedComp || null)}
                                                            onChange={(e) => setCategoryQuantity(category, Number.parseInt(e.target.value || '1', 10) || 1)}
                                                            className="input-premium w-20 text-right"
                                                        />
                                                        <button
                                                            type="button"
                                                            onClick={() => handleApplyQuantity(category)}
                                                            className="h-10 px-3 rounded-lg bg-[var(--primary)] text-white text-sm font-semibold hover:opacity-90 transition-opacity"
                                                        >
                                                            Apply
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <p className="text-sm font-semibold">₴{(selectedComp?.price || 0) * (selectedComp?.quantity || 1)}</p>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                )}

                                <button
                                    onClick={() => {
                                        setSelectedCategory((current) => (current === category ? null : category));
                                    }}
                                    className={`w-full min-h-11 font-medium flex items-center justify-center gap-2 ${isMissing ? 'btn-primary' : 'btn-secondary'} transition-all duration-150`}
                                >
                                    <Plus className="w-4 h-4" />
                                    {selectedComp ? 'Change' : 'Select'} {label}
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
                                            hasExistingStorage={(build.storage_components || []).length > 0}
                                        />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Sidebar - Build Summary & AI */}
                <aside className="space-y-6">
                    {/* AI Buttons */}
                    {build && (
                        <div className="space-y-3">
                            <AIBuildButton
                                onClick={handleAIBuild}
                                loading={aiBuildLoading}
                                className="w-full"
                            />
                            <button
                                onClick={handleOpenAIChat}
                                className="w-full min-h-11 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-900 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
                            >
                                <MessageCircle className="w-4 h-4" />
                                Ask AI Assistant
                            </button>
                        </div>
                    )}

                    {build && (
                        <BuildSummaryPanel build={build} onBuildUpdate={handleBuildUpdate} onRemoveComponent={handleRemoveComponent} />
                    )}
                </aside>
            </div>

        </Layout>
    );
}



