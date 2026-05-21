import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Loader2, PencilLine, Send, Star } from 'lucide-react';
import Layout from '../components/Layout';
import { communityAPI, productAPI } from '../lib/apiClient';
import { getUser } from '../lib/auth';
import type { Build, BuildSuggestion, Product } from '../types';
import { toast } from 'sonner';

function RatingInput({ value, onChange }: { value: number; onChange: (rating: number) => void }) {
    return (
        <div className="flex items-center gap-1">
            {Array.from({ length: 5 }).map((_, index) => {
                const rating = index + 1;
                const active = rating <= value;

                return (
                    <button
                        key={rating}
                        type="button"
                        onClick={() => onChange(rating)}
                        className="p-1"
                        aria-label={`Rate ${rating} star${rating === 1 ? '' : 's'}`}
                    >
                        <Star className={`w-6 h-6 ${active ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}`} />
                    </button>
                );
            })}
        </div>
    );
}

function matchesCategory(product: Product, category: string) {
    const normalizedCategory = category.toLowerCase();
    const text = `${product.name} ${product.brand || ''} ${product.subcategory || ''}`.toLowerCase();
    const specs = product.specs || {};

    if (normalizedCategory === 'storage') {
        return /ssd|hdd|storage/i.test(text) || specs.capacity !== undefined;
    }
    if (normalizedCategory === 'gpu') {
        return /radeon|nvidia|geforce|rtx|gtx/i.test(text) || specs.vram !== undefined;
    }
    if (normalizedCategory === 'cpu') {
        return /intel|ryzen|core|athlon/i.test(text) || specs.socket !== undefined;
    }
    if (normalizedCategory === 'ram') {
        return /ddr/i.test(text) || specs.capacity !== undefined;
    }
    if (normalizedCategory === 'motherboard') {
        return /motherboard|board|am4|am5|lga/i.test(text) || specs.socket !== undefined;
    }
    if (normalizedCategory === 'psu') {
        return /psu|power supply|watt/i.test(text) || specs.power !== undefined;
    }
    if (normalizedCategory === 'cooler') {
        return /cooler|cooling|fan|aio/i.test(text);
    }

    return true;
}

export default function PublicBuildPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const currentUser = getUser();
    const currentUserId = currentUser?.id;

    const [build, setBuild] = useState<Build | null>(null);
    const [loading, setLoading] = useState(true);
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [suggestionCategory, setSuggestionCategory] = useState('cpu');
    const [suggestionQuery, setSuggestionQuery] = useState('');
    const [suggestionResults, setSuggestionResults] = useState<Product[]>([]);
    const [selectedSuggestionProduct, setSelectedSuggestionProduct] = useState<Product | null>(null);
    const [suggestionQuantity, setSuggestionQuantity] = useState(1);
    const [suggestionComment, setSuggestionComment] = useState('');
    const [suggestionSubmitting, setSuggestionSubmitting] = useState(false);
    const [ownerActionLoading, setOwnerActionLoading] = useState<number | null>(null);

    const isOwner = build && currentUserId === build.user_id;

    const loadBuild = async () => {
        if (!id) return;

        setLoading(true);
        try {
            const data = await communityAPI.getPublicBuild(Number(id));
            setBuild(data);
        } catch {
            setBuild(null);
            toast.error('Build not found or is not public');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!id) return;

        let active = true;

        const fetchBuild = async () => {
            setLoading(true);
            try {
                const data = await communityAPI.getPublicBuild(Number(id));
                if (!active) return;
                setBuild(data);
            } catch {
                if (active) {
                    setBuild(null);
                    toast.error('Build not found or is not public');
                }
            } finally {
                if (active) setLoading(false);
            }
        };

        void fetchBuild();

        return () => {
            active = false;
        };
    }, [id]);

    useEffect(() => {
        if (!build || !currentUserId) return;

        const mine = build.reviews?.find((review) => review.user_id === currentUserId);
        if (mine) {
            setRating(mine.rating);
            setComment(mine.comment || '');
        } else {
            setRating(5);
            setComment('');
        }
    }, [build, currentUserId]);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            const fetchProducts = async () => {
                if (!suggestionQuery.trim()) {
                    setSuggestionResults([]);
                    return;
                }

                try {
                    const data = await productAPI.search(suggestionQuery.trim());
                    const list = Array.isArray(data) ? data : (data.products || []);
                    setSuggestionResults(list.filter((product: Product) => matchesCategory(product, suggestionCategory)));
                } catch {
                    setSuggestionResults([]);
                }
            };

            void fetchProducts();
        }, 250);

        return () => window.clearTimeout(timeoutId);
    }, [suggestionCategory, suggestionQuery]);

    const reviews = build?.reviews || [];
    const derivedAverageRating = reviews.length > 0
        ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length
        : 0;
    const averageRating = build?.average_rating ?? derivedAverageRating;
    const reviewCount = build?.review_count ?? reviews.length;
    const ownerSuggestions = useMemo(() => build?.suggestions || [], [build]);

    const selectComponentForSuggestion = (category: string, componentName: string) => {
        setSuggestionCategory(category);
        setSuggestionQuery(componentName);
        setSelectedSuggestionProduct(null);
        setSuggestionComment(`Suggest a better alternative for ${componentName}`);
    };

    const handleSubmitReview = async () => {
        if (!build) return;

        setSubmitting(true);
        try {
            const review = await communityAPI.submitReview(build.id, rating, comment.trim() || null);
            const refreshed = await communityAPI.getPublicBuild(build.id);
            setBuild(refreshed);
            setRating(review.rating);
            setComment(review.comment || '');
            toast.success('Review saved');
        } catch {
            toast.error('Failed to save review');
        } finally {
            setSubmitting(false);
        }
    };

    const handleSubmitSuggestion = async () => {
        if (!build || !selectedSuggestionProduct) return;

        setSuggestionSubmitting(true);
        try {
            await communityAPI.submitSuggestion(build.id, {
                category: suggestionCategory,
                suggested_product_id: selectedSuggestionProduct.product_id,
                quantity: suggestionQuantity,
                comment: suggestionComment.trim() || null,
            });
            toast.success('Change suggestion sent');
            setSuggestionQuery('');
            setSuggestionResults([]);
            setSelectedSuggestionProduct(null);
            setSuggestionQuantity(1);
            setSuggestionComment('');
        } catch (error: any) {
            const message = error?.response?.data?.detail || 'Failed to send suggestion';
            toast.error(message);
        } finally {
            setSuggestionSubmitting(false);
        }
    };

    const handleOwnerSuggestionAction = async (suggestion: BuildSuggestion, action: 'apply' | 'reject') => {
        if (!build) return;

        setOwnerActionLoading(suggestion.id);
        try {
            if (action === 'apply') {
                await communityAPI.applySuggestion(build.id, suggestion.id);
            } else {
                await communityAPI.rejectSuggestion(build.id, suggestion.id);
            }
            await loadBuild();
            toast.success(action === 'apply' ? 'Suggestion applied' : 'Suggestion rejected');
        } catch (error: any) {
            const message = error?.response?.data?.detail || 'Failed to process suggestion';
            toast.error(message);
        } finally {
            setOwnerActionLoading(null);
        }
    };

    if (loading) {
        return (
            <Layout>
                <div className="soft-card p-8 animate-pulse">
                    <div className="skeleton-line w-44 mb-4" />
                    <div className="skeleton-line w-80 mb-2" />
                    <div className="skeleton-line w-full h-[24rem]" />
                </div>
            </Layout>
        );
    }

    if (!build) {
        return (
            <Layout>
                <div className="soft-card p-10 text-center">
                    <h1 className="text-3xl font-bold mb-3">Build not available</h1>
                    <p className="text-[color:var(--text-soft)] mb-6">
                        The build may have been removed or is still private.
                    </p>
                    <button onClick={() => navigate('/dashboard')} className="inline-flex items-center gap-2 min-h-11 btn-primary">
                        <ArrowLeft className="w-4 h-4" />
                        Back to feed
                    </button>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="space-y-6">
                <div className="flex items-center justify-between gap-4">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--border-soft)] bg-[var(--surface)] hover:bg-[var(--surface-soft)] transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to feed
                    </button>
                    <button
                        onClick={() => navigate('/builder')}
                        className="inline-flex items-center gap-2 min-h-11 btn-primary"
                    >
                        Open Builder
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-[1.7fr_1fr] gap-6">
                    <section className="space-y-6">
                        <div className="soft-card p-6 md:p-7">
                            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-5">
                                <div>
                                    <div className="inline-flex items-center rounded-full border border-[var(--border-soft)] bg-[var(--surface-soft)] px-3 py-1 text-xs font-semibold text-[color:var(--text-soft)]">
                                        Public build
                                    </div>
                                    <h1 className="mt-3 text-4xl font-bold">{build.name}</h1>
                                    <p className="mt-2 text-sm text-[color:var(--text-soft)]">
                                        Created by {build.owner_username || 'community member'}
                                    </p>
                                </div>

                                <div className="text-right">
                                    <p className="text-3xl font-bold">₴{build.total_price}</p>
                                    {build.budget ? (
                                        <p className="text-sm text-[color:var(--text-soft)]">Budget: ₴{build.budget}</p>
                                    ) : (
                                        <p className="text-sm text-[color:var(--text-soft)]">No budget limit</p>
                                    )}
                                    <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-[var(--surface-muted)] px-3 py-1.5 text-sm font-semibold">
                                        <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                                        {reviewCount > 0 ? `${averageRating.toFixed(1)} / 5 from ${reviewCount} reviews` : 'No ratings yet'}
                                    </div>
                                </div>
                            </div>

                            <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {Object.entries(build.selected_components).map(([category, component]) => (
                                    <div key={category} className="rounded-2xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-4">
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="text-xs uppercase tracking-[0.16em] text-[color:var(--text-soft)] font-semibold">{category}</p>
                                                <p className="mt-1 font-semibold leading-snug">{component.name}</p>
                                                <p className="text-sm text-[color:var(--text-soft)] mt-1">₴{(component.price || 0) * (component.quantity || 1)}</p>
                                            </div>
                                            {!isOwner && (
                                                <button
                                                    type="button"
                                                    onClick={() => selectComponentForSuggestion(category, component.name)}
                                                    className="inline-flex items-center gap-2 rounded-xl border border-[var(--border-soft)] bg-[var(--surface)] px-3 py-2 text-xs font-semibold hover:border-[var(--border-strong)]"
                                                >
                                                    <PencilLine className="w-3.5 h-3.5" />
                                                    Suggest change
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {build.compatibility_warnings.length > 0 && (
                                <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4">
                                    <h3 className="font-semibold text-amber-900 mb-2">Compatibility notes</h3>
                                    <ul className="space-y-1 text-sm text-amber-900/90">
                                        {build.compatibility_warnings.map((warning, index) => (
                                            <li key={index}>• {warning}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        <div className="soft-card p-6 md:p-7">
                            <div className="flex items-center justify-between gap-4 mb-5">
                                <div>
                                    <h2 className="text-2xl font-semibold">Reviews</h2>
                                    <p className="text-sm text-[color:var(--text-soft)] mt-1">Share your own experience with this build.</p>
                                </div>
                                <div className="inline-flex items-center gap-2 rounded-full bg-[var(--surface-muted)] px-3 py-1.5 text-sm font-semibold">
                                    <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                                    {reviewCount}
                                </div>
                            </div>

                            {reviews.length === 0 ? (
                                <p className="text-sm text-[color:var(--text-soft)]">No reviews yet. Be the first to leave feedback.</p>
                            ) : (
                                <div className="space-y-4">
                                    {reviews.map((review) => (
                                        <article key={review.id} className="rounded-2xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-4">
                                            <div className="flex items-start justify-between gap-3">
                                                <div>
                                                    <p className="font-semibold">
                                                        {review.username}
                                                        {currentUser?.id === review.user_id && (
                                                            <span className="ml-2 text-xs rounded-full bg-[var(--primary)] text-white px-2 py-0.5">Your review</span>
                                                        )}
                                                    </p>
                                                    <p className="text-xs text-[color:var(--text-soft)] mt-1">
                                                        {new Date(review.created_at).toLocaleString()}
                                                    </p>
                                                </div>
                                                <div className="inline-flex items-center gap-1">
                                                    {Array.from({ length: 5 }).map((_, index) => (
                                                        <Star
                                                            key={index}
                                                            className={`w-4 h-4 ${index < review.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}`}
                                                        />
                                                    ))}
                                                </div>
                                            </div>
                                            {review.comment && (
                                                <p className="mt-3 text-sm text-[color:var(--text-main)] whitespace-pre-wrap">{review.comment}</p>
                                            )}
                                        </article>
                                    ))}
                                </div>
                            )}
                        </div>
                    </section>

                    <aside className="space-y-6">
                        {!isOwner && (
                            <div className="soft-card p-6 md:p-7 sticky top-24">
                                <h2 className="text-2xl font-semibold mb-3">Suggest a change</h2>
                                <p className="text-sm text-[color:var(--text-soft)] mb-5">
                                    Propose a replacement component for this build. The owner can review and apply it.
                                </p>

                                <div className="space-y-4">
                                    <div>
                                        <p className="text-sm font-semibold mb-2">Category</p>
                                        <select
                                            value={suggestionCategory}
                                            onChange={(e) => setSuggestionCategory(e.target.value)}
                                            className="select-premium"
                                        >
                                            {Object.keys(build.selected_components).map((category) => (
                                                <option key={category} value={category}>
                                                    {category.toUpperCase()}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="relative">
                                        <label className="block">
                                            <span className="text-sm font-semibold mb-2 block">Search product</span>
                                            <input
                                                value={suggestionQuery}
                                                onChange={(e) => setSuggestionQuery(e.target.value)}
                                                className="input-premium w-full"
                                                placeholder="Type a product name or brand"
                                            />
                                        </label>

                                        {suggestionResults.length > 0 && (
                                            <div className="absolute left-0 right-0 top-full z-30 mt-2 max-h-56 overflow-auto space-y-2 rounded-2xl border border-[#22344a] bg-[#0d1624] p-2 text-[color:var(--text-main)] shadow-[var(--shadow-elevated)]">
                                                {suggestionResults.slice(0, 8).map((product) => (
                                                    <button
                                                        key={product.product_id}
                                                        type="button"
                                                        onClick={() => {
                                                            setSelectedSuggestionProduct(product);
                                                            setSuggestionQuery(product.name);
                                                            setSuggestionResults([]);
                                                        }}
                                                        className={`w-full rounded-xl border px-3 py-2 text-left transition-colors ${selectedSuggestionProduct?.product_id === product.product_id
                                                            ? 'border-[var(--primary)] bg-[#132235]'
                                                            : 'border-transparent hover:bg-[#132235]'
                                                            }`}
                                                    >
                                                        <div className="flex items-start justify-between gap-3">
                                                            <div className="min-w-0">
                                                                <p className="font-semibold truncate">{product.name}</p>
                                                                <p className="text-xs text-[color:var(--text-soft)] truncate">{product.brand || product.subcategory || 'Unknown brand'}</p>
                                                            </div>
                                                            <p className="text-sm font-semibold shrink-0">₴{product.price}</p>
                                                        </div>
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    <div className="grid grid-cols-2 gap-3">
                                        <label className="block">
                                            <span className="text-sm font-semibold mb-2 block">Quantity</span>
                                            <input
                                                type="number"
                                                min={1}
                                                max={8}
                                                value={suggestionQuantity}
                                                onChange={(e) => setSuggestionQuantity(Number.parseInt(e.target.value || '1', 10) || 1)}
                                                className="input-premium w-full"
                                            />
                                        </label>
                                        <div className="flex items-end">
                                            <button
                                                type="button"
                                                onClick={handleSubmitSuggestion}
                                                disabled={suggestionSubmitting || !selectedSuggestionProduct}
                                                className="w-full min-h-11 btn-primary inline-flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                                            >
                                                {suggestionSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                                Send
                                            </button>
                                        </div>
                                    </div>

                                    <label className="block">
                                        <span className="text-sm font-semibold mb-2 block">Reason</span>
                                        <textarea
                                            value={suggestionComment}
                                            onChange={(e) => setSuggestionComment(e.target.value)}
                                            rows={4}
                                            className="input-premium w-full resize-none"
                                            placeholder="Explain why this component would improve the build."
                                        />
                                    </label>
                                </div>
                            </div>
                        )}

                        {isOwner && (
                            <div className="soft-card p-6 md:p-7 sticky top-24">
                                <h2 className="text-2xl font-semibold mb-3">Suggestion inbox</h2>
                                <p className="text-sm text-[color:var(--text-soft)] mb-5">
                                    Review proposed changes from other users and apply them directly to your build.
                                </p>

                                {ownerSuggestions.length === 0 ? (
                                    <p className="text-sm text-[color:var(--text-soft)]">No suggestions yet.</p>
                                ) : (
                                    <div className="space-y-3 max-h-[36rem] overflow-auto pr-1">
                                        {ownerSuggestions.map((suggestion) => (
                                            <div key={suggestion.id} className="rounded-2xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-4">
                                                <div className="flex items-center justify-between gap-3">
                                                    <div>
                                                        <p className="font-semibold capitalize">{suggestion.category}</p>
                                                        <p className="text-xs text-[color:var(--text-soft)] mt-1">by {suggestion.username}</p>
                                                    </div>
                                                    <span className="text-xs rounded-full border border-[var(--border-soft)] px-2.5 py-1 uppercase tracking-[0.12em] text-[color:var(--text-soft)]">
                                                        {suggestion.status}
                                                    </span>
                                                </div>
                                                <p className="mt-3 text-sm font-semibold">{suggestion.suggested_product_name}</p>
                                                <p className="text-sm text-[color:var(--text-soft)]">₴{suggestion.suggested_product_price} • Qty {suggestion.quantity}</p>
                                                {suggestion.comment && (
                                                    <p className="mt-2 text-sm text-[color:var(--text-main)] whitespace-pre-wrap">{suggestion.comment}</p>
                                                )}

                                                {suggestion.status === 'pending' && (
                                                    <div className="mt-4 flex gap-2">
                                                        <button
                                                            type="button"
                                                            onClick={() => handleOwnerSuggestionAction(suggestion, 'apply')}
                                                            disabled={ownerActionLoading === suggestion.id}
                                                            className="flex-1 min-h-10 btn-primary"
                                                        >
                                                            Apply
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={() => handleOwnerSuggestionAction(suggestion, 'reject')}
                                                            disabled={ownerActionLoading === suggestion.id}
                                                            className="flex-1 min-h-10 btn-secondary"
                                                        >
                                                            Reject
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="soft-card p-6 md:p-7 sticky top-24">
                            <h2 className="text-2xl font-semibold mb-3">Leave a review</h2>
                            <p className="text-sm text-[color:var(--text-soft)] mb-5">
                                Rate the build from 1 to 5 stars and add a short comment.
                            </p>

                            <div className="space-y-4">
                                <div>
                                    <p className="text-sm font-semibold mb-2">Your rating</p>
                                    <RatingInput value={rating} onChange={setRating} />
                                </div>

                                <label className="block">
                                    <span className="text-sm font-semibold mb-2 block">Comment</span>
                                    <textarea
                                        value={comment}
                                        onChange={(e) => setComment(e.target.value)}
                                        rows={8}
                                        className="input-premium w-full resize-none"
                                        placeholder="What worked well, what could be improved, and who this build suits best."
                                    />
                                </label>

                                <button
                                    type="button"
                                    onClick={handleSubmitReview}
                                    disabled={submitting || rating < 1}
                                    className="w-full min-h-11 btn-primary inline-flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                                >
                                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                    Save review
                                </button>
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </Layout>
    );
}