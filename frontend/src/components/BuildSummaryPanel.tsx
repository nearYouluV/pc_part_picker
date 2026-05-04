import type { Build } from '../types';
import { Trash2, AlertCircle } from 'lucide-react';
import apiClient from '../lib/apiClient';
import { toast } from 'sonner';

interface BuildSummaryPanelProps {
    build: Build;
    onBuildUpdate: (build: Build) => void;
    onRemoveComponent: (category: string) => void;
}

export default function BuildSummaryPanel({
    build,
    onBuildUpdate,
    onRemoveComponent,
}: BuildSummaryPanelProps) {
    const handleSaveBuild = async () => {
        try {
            const response = await apiClient.put(`/builder/${build.id}`, {
                name: build.name,
                budget: build.budget,
                goal: build.goal,
            });
            onBuildUpdate(response.data);
            toast.success('Build saved successfully');
        } catch (error) {
            toast.error('Failed to save build');
        }
    };

    const handleRemoveComponent = async (category: string) => {
        try {
            const response = await apiClient.delete(
                `/builder/${build.id}/component/${category}`
            );
            onBuildUpdate(response.data);
            onRemoveComponent(category);
            toast.success(`${category} removed`);
        } catch (error) {
            toast.error(`Failed to remove ${category}`);
        }
    };

    const budgetStatus = build.budget && build.total_price > build.budget ? 'Over budget' : 'Within budget';
    const budgetColor = build.budget && build.total_price > build.budget ? 'text-rose-700' : 'text-[color:var(--text-soft)]';

    return (
        <div className="soft-card p-6 sticky top-24 transition-all duration-200">
            <h2 className="text-xl font-semibold mb-5">Build Summary</h2>

            <div className="mb-6">
                <input
                    type="text"
                    value={build.name}
                    className="input-premium mb-4"
                    readOnly
                />
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-sm text-[color:var(--text-soft)]">Goal</p>
                        <p className="font-semibold capitalize">{build.goal}</p>
                    </div>
                    <div>
                        <p className="text-sm text-[color:var(--text-soft)]">Budget</p>
                        <p className="font-semibold">₴{build.budget || 'Unlimited'}</p>
                    </div>
                </div>
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
                                    <p className="text-xs text-[color:var(--text-soft)] truncate">{comp.name}</p>
                                    <p className="text-sm font-semibold">₴{comp.price}</p>
                                </div>
                                <button
                                    onClick={() => handleRemoveComponent(category)}
                                    className="ml-2 h-8 w-8 inline-flex items-center justify-center icon-btn-danger opacity-80 group-hover:opacity-100"
                                    title={`Remove ${category}`}
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {build.compatibility_warnings.length > 0 && (
                <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-lg">
                    <div className="flex gap-2 mb-2">
                        <AlertCircle className="w-5 h-5 text-rose-700 flex-shrink-0 mt-0.5" />
                        <h4 className="font-semibold text-rose-700">Compatibility Warnings</h4>
                    </div>
                    <ul className="text-sm text-rose-700/90 space-y-1 ml-7">
                        {build.compatibility_warnings.map((warning, idx) => (
                            <li key={idx}>• {warning}</li>
                        ))}
                    </ul>
                </div>
            )}

            <button onClick={handleSaveBuild} className="w-full min-h-11 btn-primary">
                Save Build
            </button>
        </div>
    );
}
