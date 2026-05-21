import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Star, Users, Globe2, Cpu } from 'lucide-react';
import type { Build } from '../types';

interface CommunityBuildCardProps {
    build: Build;
}

function renderStars(rating: number) {
    return Array.from({ length: 5 }).map((_, index) => (
        <Star
            key={index}
            className={`w-4 h-4 ${index < Math.round(rating) ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}`}
        />
    ));
}

export default function CommunityBuildCard({ build }: CommunityBuildCardProps) {
    const createdDate = new Date(build.created_at);
    const timeAgo = formatDistanceToNow(createdDate, { addSuffix: true });
    const reviewCount = build.review_count ?? build.reviews?.length ?? 0;
    const averageRating = build.average_rating ?? 0;
    const componentCount = Object.keys(build.selected_components).length;

    return (
        <article className="soft-card p-5 md:p-6 transition-all duration-200 hover:-translate-y-[2px] hover:shadow-[var(--shadow-elevated)]">
            <div className="flex flex-col gap-4">
                <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border-soft)] bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[color:var(--text-soft)]">
                            <Globe2 className="w-3.5 h-3.5" />
                            Public build
                        </div>
                        <h3 className="mt-3 text-xl font-semibold truncate">{build.name}</h3>
                        <p className="mt-1 text-sm text-[color:var(--text-soft)]">
                            by {build.owner_username || 'Community member'} • {timeAgo}
                        </p>
                    </div>
                    <div className="text-right shrink-0">
                        <p className="text-2xl font-bold">₴{build.total_price}</p>
                        {build.budget ? (
                            <p className="text-xs text-[color:var(--text-soft)]">Budget: ₴{build.budget}</p>
                        ) : (
                            <p className="text-xs text-[color:var(--text-soft)]">No budget limit</p>
                        )}
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-sm">
                    <div className="inline-flex items-center gap-1.5 rounded-full bg-[var(--surface-muted)] px-3 py-1.5 text-[color:var(--text-main)]">
                        <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                        {reviewCount > 0 ? `${averageRating.toFixed(1)} / 5` : 'No ratings yet'}
                    </div>
                    <div className="inline-flex items-center gap-1.5 rounded-full bg-[var(--surface-muted)] px-3 py-1.5 text-[color:var(--text-main)]">
                        <Users className="w-4 h-4 text-[color:var(--primary)]" />
                        {reviewCount} review{reviewCount === 1 ? '' : 's'}
                    </div>
                    <div className="inline-flex items-center gap-1.5 rounded-full bg-[var(--surface-muted)] px-3 py-1.5 text-[color:var(--text-main)]">
                        <Cpu className="w-4 h-4 text-[color:var(--primary)]" />
                        {componentCount} components
                    </div>
                </div>

                <div className="flex flex-wrap gap-2">
                    {Object.entries(build.selected_components).slice(0, 4).map(([category, component]) => (
                        <span key={category} className="tag-chip bg-[var(--surface-soft)] border-[var(--border-soft)] text-[color:var(--text-main)]">
                            <span className="font-semibold capitalize mr-2">{category}</span>
                            {component.name}
                        </span>
                    ))}
                    {componentCount > 4 && (
                        <span className="tag-chip bg-[var(--surface-soft)] border-[var(--border-soft)] text-[color:var(--text-soft)]">
                            +{componentCount - 4} more
                        </span>
                    )}
                </div>

                <div className="flex items-center justify-between gap-4 pt-1">
                    <div className="flex items-center gap-1.5">
                        {renderStars(reviewCount > 0 ? averageRating : 0)}
                    </div>
                    <Link
                        to={`/community/builds/${build.id}`}
                        className="inline-flex items-center justify-center min-h-11 px-4 rounded-xl btn-primary"
                    >
                        Open build
                    </Link>
                </div>
            </div>
        </article>
    );
}