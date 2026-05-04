import React, { useMemo, useState } from 'react';
import { Loader2, X, Plus } from 'lucide-react';

interface Props {
    show: boolean;
    onClose: () => void;
    name: string;
    setName: (v: string) => void;
    budget: string;
    setBudget: (v: string) => void;
    goal: string;
    setGoal: (v: string) => void;
    creating: boolean;
    onSubmit: (e: React.FormEvent) => void;
    goals: string[];
}

export default function CreateBuildModal({
    show,
    onClose,
    name,
    setName,
    budget,
    setBudget,
    goal,
    setGoal,
    creating,
    onSubmit,
}: Props) {
    const goalLabels = useMemo(() => ['office', 'esports', 'balanced', 'aaa'], []);

    const descriptions: Record<string, string> = {
        office: 'Optimized for everyday tasks like browsing, documents, and light multitasking. Quiet, efficient, and budget-friendly.',
        esports: 'Built for maximum FPS in competitive games. Prioritizes CPU performance and low latency over graphics quality.',
        balanced: 'A well-rounded setup for both gaming and productivity. Good performance across the board without overspending.',
        aaa: 'Designed for modern high-end games with stunning graphics. Focuses on GPU power and visual quality.',
    };

    const normalizedGoal = goal ? (goal.toLowerCase() === 'cybersport' ? 'esports' : goal.toLowerCase()) : '';
    const initialIndex = Math.max(0, goalLabels.indexOf(normalizedGoal));
    const [step, setStep] = useState<number>(1);
    const [selectedIndex, setSelectedIndex] = useState<number>(initialIndex >= 0 ? initialIndex : 0);
    const [hoverIndex, setHoverIndex] = useState<number | null>(null);

    React.useEffect(() => {
        if (!show) {
            return;
        }

        const nextIndex = Math.max(0, goalLabels.indexOf(normalizedGoal));
        setStep(1);
        setHoverIndex(null);
        setSelectedIndex(nextIndex >= 0 ? nextIndex : 0);
    }, [show]);

    // keep prop `goal` in sync when selectedIndex changes
    React.useEffect(() => {
        const g = goalLabels[selectedIndex] ?? goalLabels[0];
        if (g !== goal) setGoal(g);
    }, [selectedIndex]);

    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="soft-card w-full max-w-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">{step === 1 ? 'Create New Build' : 'Goal'}</h3>
                    <button onClick={onClose} className="btn-secondary h-9 w-9 inline-flex items-center justify-center !p-0">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {step === 1 ? (
                    <div className="space-y-5">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-semibold mb-2">Build Name</label>
                                <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="My Gaming PC" className="input-premium" />
                            </div>

                            <div>
                                <label className="block text-sm font-semibold mb-2">Budget (₴)</label>
                                <input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="2000" className="input-premium" />
                            </div>
                        </div>

                        <div className="flex gap-3 justify-end">
                            <button type="button" onClick={onClose} className="min-h-11 btn-secondary">Cancel</button>
                            <button type="button" onClick={() => setStep(2)} className="flex items-center gap-2 min-h-11 btn-primary">
                                Continue
                            </button>
                        </div>
                    </div>
                ) : (
                    <form onSubmit={onSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-semibold mb-3">Select Goal</label>

                            <div className="px-2">
                                <input
                                    type="range"
                                    min={0}
                                    max={goalLabels.length - 1}
                                    step={1}
                                    value={selectedIndex}
                                    onChange={(e) => setSelectedIndex(Number(e.target.value))}
                                    className="w-full"
                                />

                                <div className="flex items-center justify-between mt-3 text-sm select-none">
                                    {goalLabels.map((label, idx) => (
                                        <button
                                            key={label}
                                            type="button"
                                            onClick={() => setSelectedIndex(idx)}
                                            onMouseEnter={() => setHoverIndex(idx)}
                                            onMouseLeave={() => setHoverIndex(null)}
                                            className={`text-center w-1/4 py-1 ${selectedIndex === idx ? 'font-semibold' : 'text-gray-500 dark:text-gray-400'}`}
                                        >
                                            {label === 'esports' ? 'CyberSport' : label.charAt(0).toUpperCase() + label.slice(1)}
                                        </button>
                                    ))}
                                </div>

                                <div className="mt-3 text-sm text-gray-800 dark:text-gray-200 min-h-[3rem]">
                                    {hoverIndex !== null ? descriptions[goalLabels[hoverIndex]] : descriptions[goalLabels[selectedIndex]]}
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-3 justify-end">
                            <button type="button" onClick={() => setStep(1)} className="min-h-11 btn-secondary">Back</button>
                            <button type="submit" disabled={creating} className="flex items-center gap-2 min-h-11 btn-primary disabled:opacity-60">
                                {creating ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Creating...
                                    </>
                                ) : (
                                    <>
                                        <Plus className="w-4 h-4" /> Create Build
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
