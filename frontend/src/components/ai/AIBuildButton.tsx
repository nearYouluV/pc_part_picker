import { Loader2, Wand2 } from 'lucide-react';

interface AIBuildButtonProps {
    onClick: () => void;
    loading?: boolean;
    disabled?: boolean;
    variant?: 'primary' | 'outline' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

export function AIBuildButton({
    onClick,
    loading = false,
    disabled = false,
    variant = 'primary',
    size = 'md',
    className = '',
}: AIBuildButtonProps) {
    const baseClass = 'inline-flex items-center gap-2 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed';

    const variantClass = {
        primary: 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white',
        outline: 'border border-slate-300 text-slate-900 hover:bg-slate-50',
        ghost: 'text-slate-700 hover:bg-slate-100',
    }[variant];

    const sizeClass = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    }[size];

    return (
        <button
            onClick={onClick}
            disabled={disabled || loading}
            className={`${baseClass} ${variantClass} ${sizeClass} ${className}`}
        >
            {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
                <Wand2 className="w-4 h-4" />
            )}
            {loading ? 'Building...' : 'Build PC with AI'}
        </button>
    );
}
