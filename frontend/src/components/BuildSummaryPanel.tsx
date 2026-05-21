import { useEffect, useState } from 'react';
import type { Build } from '../types';
import { Trash2, AlertCircle } from 'lucide-react';
import apiClient from '../lib/apiClient';
import ProductModal from './ProductModal';
import { toast } from 'sonner';

interface BuildSummaryPanelProps {
    build: Build;
    onBuildUpdate: (build: Build) => void;
    onRemoveComponent: (category: string, productId?: number) => void;
}

export default function BuildSummaryPanel({
    build,
    onBuildUpdate,
    onRemoveComponent,
}: BuildSummaryPanelProps) {
    const [name, setName] = useState(build.name);
    const [budget, setBudget] = useState(build.budget ? String(build.budget) : '');
    const [goal, setGoal] = useState(build.goal);
    const [isPublic, setIsPublic] = useState(Boolean(build.is_public));
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        setName(build.name);
        setBudget(build.budget ? String(build.budget) : '');
        setGoal(build.goal);
        setIsPublic(Boolean(build.is_public));
    }, [build.id, build.name, build.budget, build.goal, build.is_public]);

    const normalizedName = name.trim() || build.name;
    const parsedBudget = budget.trim() ? parseInt(budget, 10) : null;
    const originalBudget = build.budget ?? null;
    const hasUnsavedChanges =
        normalizedName !== build.name ||
        parsedBudget !== originalBudget ||
        goal !== build.goal ||
        isPublic !== Boolean(build.is_public);

    const handleSaveBuild = async () => {
        if (!hasUnsavedChanges) return;

        setSaving(true);
        try {
            const response = await apiClient.put(`/builder/${build.id}`, {
                name: normalizedName,
                budget: parsedBudget,
                goal,
                is_public: isPublic,
            });
            onBuildUpdate(response.data);
            toast.success('Build saved successfully');
        } catch (error) {
            toast.error('Failed to save build');
        } finally {
            setSaving(false);
        }
    };

    const handleRemoveComponent = async (category: string, productId?: number) => {
        try {
            const response = await apiClient.delete(
                productId !== undefined
                    ? `/builder/${build.id}/component/${category}/${productId}`
                    : `/builder/${build.id}/component/${category}`
            );
            onBuildUpdate(response.data);
            onRemoveComponent(category, productId);
            toast.success(productId !== undefined ? `${category} item removed` : `${category} removed`);
        } catch (error) {
            toast.error(`Failed to remove ${category}`);
        }
    };

    const [modalOpen, setModalOpen] = useState(false);
    const [modalProductId, setModalProductId] = useState<number | null>(null);

    const openProductModal = (productId: number) => {
        setModalProductId(productId);
        setModalOpen(true);
    };

    const budgetStatus = build.budget && build.total_price > build.budget ? 'Over budget' : 'Within budget';
    const budgetColor = build.budget && build.total_price > build.budget ? 'text-rose-700' : 'text-[color:var(--text-soft)]';
    const publicBuildUrl = `${window.location.origin}/community/builds/${build.id}`;

    const handleCopyPublicLink = async () => {
        try {
            await navigator.clipboard.writeText(publicBuildUrl);
            toast.success('Public link copied');
        } catch {
            toast.error('Failed to copy public link');
        }
    };

    return (
        <div className="soft-card p-6 sticky top-24 transition-all duration-200">
            <h2 className="text-xl font-semibold mb-5">Build Summary</h2>

            <div className="mb-6">
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="input-premium mb-4"
                    placeholder="Build name"
                />
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-sm text-[color:var(--text-soft)] mb-1">Goal</p>
                        <select
                            value={goal}
                            onChange={(e) => setGoal(e.target.value)}
                            className="select-premium"
                        >
                            <option value="balanced">Balanced</option>
                            <option value="esports">Esports</option>
                            <option value="aaa">AAA</option>
                            <option value="office">Office</option>
                        </select>
                    </div>
                    <div>
                        <p className="text-sm text-[color:var(--text-soft)] mb-1">Budget (₴)</p>
                        <input
                            type="number"
                            min="0"
                            value={budget}
                            onChange={(e) => setBudget(e.target.value)}
                            className="input-premium"
                            placeholder="Unlimited"
                        />
                    </div>
                </div>

                <label className="mt-4 flex items-start gap-3 rounded-xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-3">
                    <input
                        type="checkbox"
                        checked={isPublic}
                        onChange={(e) => setIsPublic(e.target.checked)}
                        className="mt-1 h-4 w-4 rounded border-[var(--border-strong)]"
                    />
                    <span className="text-sm">
                        <span className="block font-semibold text-[color:var(--text-main)]">Publish to community</span>
                        <span className="block text-[color:var(--text-soft)]">Other users can view, rate, and review this build.</span>
                    </span>
                </label>
            </div>

            <div className="mb-6 p-4 muted-panel">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-[color:var(--text-soft)]">Total Price:</span>
                    <span className="text-2xl font-bold">₴{build.total_price}</span>
                </div>
                {build.budget && (
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-sm text-[color:var(--text-soft)]">{budgetStatus}</span>
                        <span className={budgetColor}>
                            {build.total_price > build.budget ? `+₴${build.total_price - build.budget}` : `-₴${build.budget - build.total_price}`}
                        </span>
                    </div>
                )}
            </div>

            <div className="mb-6">
                <h3 className="font-semibold mb-3">Components</h3>
                <div className="space-y-2 max-h-64 overflow-auto">
                    {Object.entries(build.selected_components).length === 0 ? (
                        <p className="text-sm text-[color:var(--text-soft)]">No components selected</p>
                    ) : (
                        Object.entries(build.selected_components).map(([category, comp]) => (
                            <div key={category} className="flex items-start justify-between p-3 muted-panel group transition-all duration-150 hover:shadow-sm hover:-translate-y-[2px]">
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium capitalize">{category}</p>
                                    {category === 'storage' && (build.storage_components || []).length > 0 ? (
                                        <div className="space-y-1 mt-1">
                                            {(build.storage_components || []).map((storageItem) => (
                                                <div key={`${storageItem.product_id}-${storageItem.name}`} className="flex items-center justify-between gap-2">
                                                    <div className="min-w-0">
                                                        <p className="text-xs text-[color:var(--text-soft)] truncate">{storageItem.name}{storageItem.quantity && storageItem.quantity > 1 ? ` x${storageItem.quantity}` : ''}</p>
                                                        <p className="text-xs font-semibold">₴{(storageItem.price || 0) * (storageItem.quantity || 1)}</p>
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleRemoveComponent('storage', storageItem.product_id)}
                                                        className="h-7 w-7 inline-flex items-center justify-center rounded-lg hover:bg-[var(--surface-muted)] text-[color:var(--text-soft)] hover:text-rose-700 transition-colors"
                                                        title="Remove one storage item"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex items-center gap-2">
                                                <p
                                                    className="text-xs text-[color:var(--text-soft)] truncate cursor-pointer"
                                                    onClick={() => openProductModal(comp.product_id)}
                                                >{comp.name}{comp.quantity && comp.quantity > 1 ? ` x${comp.quantity}` : ''}</p>
                                                {comp.source === 'ai' && (
                                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">AI</span>
                                                )}
                                            </div>
                                            <p className="text-sm font-semibold">₴{(comp.price || 0) * (comp.quantity || 1)}</p>
                                        </>
                                    )}
                                </div>
                                {category !== 'storage' && (
                                    <button
                                        onClick={() => handleRemoveComponent(category)}
                                        className="ml-2 h-8 w-8 inline-flex items-center justify-center icon-btn-danger opacity-80 group-hover:opacity-100"
                                        title={`Remove ${category}`}
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {build.compatibility_warnings.length > 0 && (
                <div className="mb-6 p-4 rounded-xl border border-[var(--border-soft)] bg-[linear-gradient(135deg,color-mix(in_srgb,var(--surface-muted)_85%,#f0f7ff)_0%,color-mix(in_srgb,var(--surface)_88%,#eaf2fd)_100%)] shadow-[var(--shadow-soft)]">
                    <div className="flex gap-2 mb-2">
                        <AlertCircle className="w-5 h-5 text-[color:var(--primary)] flex-shrink-0 mt-0.5" />
                        <h4 className="font-semibold text-[color:var(--text-main)]">Compatibility Warnings</h4>
                    </div>
                    <ul className="text-sm text-[color:var(--text-soft)] space-y-1 ml-7">
                        {build.compatibility_warnings.map((warning, idx) => (
                            <li key={idx}>• {warning}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="mb-3 flex items-center justify-between text-sm">
                <span className={hasUnsavedChanges ? 'text-[color:var(--accent-strong)] font-semibold' : 'text-[color:var(--text-soft)]'}>
                    {hasUnsavedChanges ? 'Unsaved changes' : 'All changes saved'}
                </span>
            </div>

            <button
                onClick={handleSaveBuild}
                disabled={saving || !hasUnsavedChanges}
                className="w-full min-h-11 btn-primary disabled:opacity-70 disabled:cursor-not-allowed"
            >
                {saving ? 'Saving...' : hasUnsavedChanges ? 'Save Changes' : 'Saved'}
            </button>

            {build.is_public && (
                <button
                    type="button"
                    onClick={handleCopyPublicLink}
                    className="mt-3 w-full min-h-11 btn-secondary"
                >
                    Copy public link
                </button>
            )}
            <ProductModal productId={modalProductId} open={modalOpen} onClose={() => setModalOpen(false)} />
        </div>
    );
}
