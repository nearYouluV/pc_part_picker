import type { Build } from '../types';
import { Trash2, Edit2, Cpu } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface BuildCardProps {
    build: Build;
    onOpen: (build: Build) => void;
    onDelete: (buildId: number) => void;
}

export default function BuildCard({ build, onOpen, onDelete }: BuildCardProps) {
    const componentCount = Object.keys(build.selected_components).length;
    const createdDate = new Date(build.created_at);
    const timeAgo = formatDistanceToNow(createdDate, { addSuffix: true });

    const goalColor = (goal: string) => {
        switch (goal) {
            case 'gaming':
                return 'bg-rose-100 text-rose-800 border border-rose-200';
            case 'workstation':
                return 'bg-amber-100 text-amber-800 border border-amber-200';
            default:
                return 'bg-emerald-100 text-emerald-800 border border-emerald-200';
        }
    };

    return (
        <div className="soft-card p-6 transition-all duration-200 hover:-translate-y-[2px] hover:shadow-[var(--shadow-elevated)]">
            <div className="flex items-start justify-between mb-4 gap-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                        <Cpu className="w-5 h-5 text-[color:var(--primary)]" />
                        <h3 className="text-xl font-semibold truncate">{build.name}</h3>
                        <span className={`ml-3 text-xs font-semibold tag-chip ${goalColor(build.goal)}`}>
                            {build.goal?.charAt(0).toUpperCase() + build.goal?.slice(1)}
                        </span>
                    </div>
                    <p className="text-sm text-[color:var(--text-soft)] mt-2">{timeAgo}</p>
                </div>
                <div className="text-right">
                    <p className="text-2xl font-bold text-[color:var(--text-main)]">₴{build.total_price}</p>
                    {build.budget && (
                        <p className="text-sm text-[color:var(--text-soft)]">Budget: ₴{build.budget}</p>
                    )}
                </div>
            </div>

            <div className="mb-4">
                <p className="text-sm text-[color:var(--text-soft)] mb-3">{componentCount} components selected</p>
                <div className="flex flex-wrap gap-2">
                    {Object.entries(build.selected_components).map(([category, comp]) => (
                        <div key={category} className="px-3 py-1 bg-[var(--surface-muted)] border border-[var(--border-soft)] text-[color:var(--text-main)] rounded-lg text-sm truncate max-w-xs" title={comp.name}>
                            <span className="font-semibold capitalize mr-2 text-sm">{category}:</span>
                            <span className="text-sm truncate">{comp.name}</span>
                        </div>
                    ))}
                </div>
            </div>

            {build.compatibility_warnings.length > 0 && (
                <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-lg">
                    <p className="text-xs text-rose-700 font-semibold mb-1">Warnings ({build.compatibility_warnings.length})</p>
                    <ul className="text-xs text-rose-700/90 space-y-1">
                        {build.compatibility_warnings.slice(0, 2).map((warning, idx) => (
                            <li key={idx}>• {warning}</li>
                        ))}
                        {build.compatibility_warnings.length > 2 && (
                            <li>• +{build.compatibility_warnings.length - 2} more</li>
                        )}
                    </ul>
                </div>
            )}

            <div className="flex gap-3">
                <button onClick={() => onOpen(build)} className="flex-1 flex items-center justify-center gap-2 min-h-11 btn-primary transition-all duration-150">
                    <Edit2 className="w-4 h-4" />
                    Open
                </button>

                <button
                    onClick={() => onDelete(build.id)}
                    className="flex items-center justify-center gap-2 min-h-11 px-3 icon-btn-danger transition-all duration-150 hover:scale-105"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
