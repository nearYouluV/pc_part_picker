import { useEffect, useState } from 'react';
import type { ComponentRecommendation, Product } from '../types';
import apiClient from '../lib/apiClient';
import { Loader2, Search, SlidersHorizontal, X } from 'lucide-react';
import { toast } from 'sonner';
import FilterPanel from './FilterPanel.tsx';

interface ComponentSelectorProps {
    buildId: number;
    category: string;
    onSelect: (product: Product, quantity: number, append: boolean) => void;
    selectedProduct?: Product | null;
    onClose: () => void;
    buildGoal: string;
    buildBudget: number | null;
    hasExistingStorage?: boolean;
}

type FilterState = Record<string, string | boolean | number | null | undefined>;

export default function ComponentSelector({
    buildId,
    category,
    onSelect,
    selectedProduct,
    onClose,
    buildGoal,
    buildBudget,
    hasExistingStorage = false,
}: ComponentSelectorProps) {
    const categoryLabel = category === 'cooler' ? 'Cooling' : category;
    const [products, setProducts] = useState<ComponentRecommendation[]>([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState('recommended');
    const [showFilters, setShowFilters] = useState(false);
    const [showSort, setShowSort] = useState(false);
    const [appendStorage, setAppendStorage] = useState<boolean>(hasExistingStorage && category === 'storage');
    const [filters, setFilters] = useState<FilterState>({
        compatible_only: true,
        min_price: '',
        max_price: '',
    });

    useEffect(() => {
        if (category === 'storage') {
            setAppendStorage(hasExistingStorage);
        } else {
            setAppendStorage(false);
        }
    }, [category, hasExistingStorage]);

    useEffect(() => {
        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => {
            const fetchProducts = async () => {
                setLoading(true);
                try {
                    const params = new URLSearchParams();
                    params.set('build_id', String(buildId));
                    params.set('sort_by', sortBy);

                    if (search.trim()) {
                        params.set('search', search.trim());
                    }

                    Object.entries(filters).forEach(([key, value]) => {
                        if (value === '' || value === null || value === undefined) {
                            return;
                        }

                        params.set(key, String(value));
                    });

                    const response = await apiClient.get(`/builder/category/${category}?${params.toString()}`, {
                        signal: controller.signal,
                    });
                    setProducts(response.data);
                } catch (error: any) {
                    if (error.name !== 'CanceledError' && error.name !== 'AbortError') {
                        toast.error(`Failed to fetch ${category} products`);
                    }
                } finally {
                    setLoading(false);
                }
            };

            if (category && buildId) {
                fetchProducts();
            }
        }, 220);

        return () => {
            window.clearTimeout(timeoutId);
            controller.abort();
        };
    }, [buildId, category, filters, search, sortBy]);

    return (
        <div className="soft-card border border-[var(--border-strong)] p-4 md:p-5 shadow-[var(--shadow-elevated)] animate-page-fade">
            <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                    <h2 className="text-xl font-semibold capitalize">Select {categoryLabel}</h2>
                    <p className="text-sm text-[color:var(--text-soft)] mt-1">
                        Ranked for your {buildGoal} build{buildBudget ? ` and budget of ₴${buildBudget}` : ''}.
                    </p>
                </div>
                <button onClick={onClose} className="btn-secondary h-9 w-9 inline-flex items-center justify-center !p-0 transition-all duration-150" aria-label="Close selector">
                    <X className="w-5 h-5" />
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_auto] gap-3 mb-4">
                <label className="relative block">
                    <span className="sr-only">Search products</span>
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[color:var(--text-soft)]" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search name, brand, or model"
                        className="input-premium pl-10"
                    />
                </label>

                <div className="flex items-center gap-2 justify-end">
                    <button
                        type="button"
                        onClick={() => setShowFilters((value) => !value)}
                        className="min-h-11 px-4 rounded-xl border text-sm font-semibold inline-flex items-center gap-2 bg-[var(--surface)] border-[var(--border-strong)] text-[color:var(--text-main)]"
                    >
                        <SlidersHorizontal className="w-4 h-4" />
                        Filters
                    </button>

                    <div className="relative">
                        <button
                            type="button"
                            onClick={() => setShowSort((value) => !value)}
                            className="min-h-11 px-4 rounded-xl border text-sm font-semibold inline-flex items-center gap-2 bg-[var(--surface)] border-[var(--border-strong)] text-[color:var(--text-main)]"
                        >
                            Sort
                        </button>

                        {showSort && (
                            <div className="absolute right-0 mt-2 w-56 rounded-2xl border border-[var(--border-strong)] bg-[var(--surface)] shadow-lg p-2 z-10">
                                <button type="button" onClick={() => { setSortBy('recommended'); setShowSort(false); }} className="w-full text-left px-3 py-2 rounded-xl hover:bg-[var(--surface-soft)]">
                                    Recommended
                                </button>
                                <button type="button" onClick={() => { setSortBy('price_low'); setShowSort(false); }} className="w-full text-left px-3 py-2 rounded-xl hover:bg-[var(--surface-soft)]">
                                    Price: low to high
                                </button>
                                <button type="button" onClick={() => { setSortBy('price_high'); setShowSort(false); }} className="w-full text-left px-3 py-2 rounded-xl hover:bg-[var(--surface-soft)]">
                                    Price: high to low
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {showFilters && (
                <div className="mb-4">
                    <FilterPanel
                        category={category}
                        filters={filters}
                        setFilters={setFilters}
                        onClose={() => setShowFilters(false)}
                    />
                </div>
            )}

            {category === 'storage' && (
                <div className="mb-4 rounded-xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-3">
                    <label className="flex items-center gap-2 text-sm text-[color:var(--text-soft)]">
                        <input
                            type="checkbox"
                            checked={appendStorage}
                            onChange={(e) => setAppendStorage(e.target.checked)}
                        />
                        Add as extra storage (keep existing drive)
                    </label>
                </div>
            )}

            {loading ? (
                <div className="flex items-center justify-center py-10">
                    <Loader2 className="w-6 h-6 animate-spin text-[color:var(--text-soft)]" />
                </div>
            ) : products.length === 0 ? (
                <p className="text-center text-[color:var(--text-soft)] py-10">No products available for {categoryLabel} with the current filters.</p>
            ) : (
                <div className="space-y-3 max-h-[34rem] overflow-auto pr-1">
                    {products.map((product) => {
                        const isSelected = selectedProduct?.product_id === product.product_id;
                        const imageSrc = product.image_small || product.image || '';
                        const psuCertificationRaw = category === 'psu' ? String(product.specs?.certification ?? '').trim() : '';
                        const psuCertification = psuCertificationRaw.replace(/^80\+\s*/i, '');
                        const psuModularity = category === 'psu' ? product.specs?.modularity : undefined;
                        const psuPower = category === 'psu' ? product.specs?.power : undefined;
                        const modularityLabel =
                            psuModularity === true
                                ? 'Fully/Semi Modular'
                                : psuModularity === false
                                    ? 'Non-modular'
                                    : null;

                        return (
                            <button
                                key={product.product_id}
                                onClick={() => {
                                    onSelect(product, 1, category === 'storage' ? appendStorage : false);
                                    onClose();
                                }}
                                className={`w-full rounded-2xl border transition-all duration-200 text-left p-3 md:p-4 flex items-start gap-4 ${isSelected
                                    ? 'border-[var(--primary)] bg-[var(--surface-muted)] shadow-sm'
                                    : 'border-[var(--border-soft)] hover:shadow-md hover:-translate-y-[1px] hover:border-[var(--border-strong)] bg-[var(--surface)]'
                                    }`}
                            >
                                <div className="h-[100px] w-[100px] flex-shrink-0 rounded-xl border border-[var(--border-soft)] bg-[var(--surface-soft)] overflow-hidden flex items-center justify-center">
                                    {imageSrc ? (
                                        <img src={imageSrc} alt={product.name} className="h-full w-full object-cover" loading="lazy" />
                                    ) : (
                                        <div className="text-xs text-[color:var(--text-soft)] text-center px-2">No image</div>
                                    )}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="min-w-0">
                                            <p className="font-semibold truncate text-[color:var(--text-main)]">{product.name}</p>
                                            <p className="text-sm text-[color:var(--text-main)] mt-1 truncate">
                                                {product.brand || product.subcategory || `ID: ${product.external_id ?? product.product_id}`}
                                            </p>
                                        </div>

                                        <div className="text-right flex-shrink-0">
                                            <p className="text-lg font-bold">₴{product.price}</p>
                                            <div className="mt-1 inline-flex items-center rounded-full border border-[var(--border-soft)] px-2.5 py-1 text-xs font-semibold text-[color:var(--text-soft)] bg-[var(--surface-soft)]">
                                                Rank {Math.round(product.score ?? 0)}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="mt-3 flex flex-wrap gap-2">
                                        <span className={`tag-chip ${product.compatible ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-amber-50 border-amber-200 text-amber-800'}`}>
                                            {product.compatible ? 'Compatible' : 'Needs review'}
                                        </span>
                                        {category === 'psu' && psuPower !== undefined && psuPower !== null && (
                                            <span className="tag-chip bg-[var(--surface-soft)] border-[var(--border-soft)] text-[color:var(--text-main)]">
                                                {psuPower}W
                                            </span>
                                        )}
                                        {category === 'psu' && psuCertification && (
                                            <span className="tag-chip bg-[var(--surface-soft)] border-[var(--border-soft)] text-[color:var(--text-main)]">
                                                80+ {psuCertification}
                                            </span>
                                        )}
                                        {category === 'psu' && modularityLabel && (
                                            <span className="tag-chip bg-[var(--surface-soft)] border-[var(--border-soft)] text-[color:var(--text-main)]">
                                                {modularityLabel}
                                            </span>
                                        )}
                                        {product.compatibility_details?.slice(0, 2).map((detail) => (
                                            <span key={detail} className="tag-chip bg-[var(--surface-soft)] border-[var(--border-soft)] text-[color:var(--text-main)]">
                                                {detail}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
