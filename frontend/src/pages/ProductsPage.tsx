import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Loader2, Search, SlidersHorizontal, Sparkles } from 'lucide-react';
import Layout from '../components/Layout';
import { productAPI } from '../lib/apiClient';

const CATEGORY_QUICK_TERM: Record<string, string> = {
    cpu: 'Ryzen',
    gpu: 'RTX',
    ram: 'DDR5',
    motherboard: 'AM5',
    storage: 'SSD',
    psu: '650W',
    cooler: 'Cooler',
};

const SAMPLE_SEARCHES = [
    { key: 'cpu', label: 'CPU', query: 'Ryzen' },
    { key: 'gpu', label: 'GPU', query: 'RTX' },
    { key: 'ram', label: 'RAM', query: 'DDR5' },
    { key: 'motherboard', label: 'Motherboard', query: 'AM5' },
    { key: 'storage', label: 'Storage', query: 'SSD' },
    { key: 'psu', label: 'PSU', query: '650W' },
    { key: 'cooler', label: 'Cooling', query: 'Cooler' },
];

function getProductId(product: any) {
    return product.product_id ?? product.id ?? product.productId;
}

export default function ProductsPage() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [category, setCategory] = useState<string | null>(null);
    const [minPrice, setMinPrice] = useState('');
    const [maxPrice, setMaxPrice] = useState('');
    const [pageHint, setPageHint] = useState('Featured products by component category');

    useEffect(() => {
        let mounted = true;

        const loadSamples = async () => {
            setLoading(true);
            try {
                const batches = await Promise.all(
                    SAMPLE_SEARCHES.map(async ({ query: sampleQuery, label }) => {
                        try {
                            const data = await productAPI.search(sampleQuery);
                            const list = Array.isArray(data) ? data : (data.products || []);
                            return { label, items: list.slice(0, 3) };
                        } catch {
                            return { label, items: [] };
                        }
                    })
                );

                if (!mounted) return;

                const merged = batches.flatMap((batch) => batch.items);
                const unique = Array.from(
                    new Map(merged.map((item: any) => [getProductId(item), item])).values()
                );
                setResults(unique);
                setPageHint('Featured products across CPU, GPU, RAM, motherboard, storage, PSU and cooling');
            } finally {
                if (mounted) setLoading(false);
            }
        };

        if (!query.trim() && !category) {
            void loadSamples();
        }

        return () => {
            mounted = false;
        };
    }, []);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            const fetchProducts = async () => {
                const q = query.trim() || (category ? CATEGORY_QUICK_TERM[category] ?? '' : '');

                if (!q) {
                    return;
                }

                setLoading(true);
                try {
                    const data = await productAPI.search(q);
                    const list = Array.isArray(data) ? data : (data.products || []);
                    setResults(list);
                    setPageHint(category ? `${category.toUpperCase()} products` : `Search results for "${q}"`);
                } catch {
                    setResults([]);
                } finally {
                    setLoading(false);
                }
            };

            void fetchProducts();
        }, 250);

        return () => window.clearTimeout(timeoutId);
    }, [query, category]);

    const filtered = useMemo(() => {
        return results.filter((product) => {
            const price = Number(product.price || 0);
            if (minPrice && !Number.isNaN(Number(minPrice)) && price < Number(minPrice)) return false;
            if (maxPrice && !Number.isNaN(Number(maxPrice)) && price > Number(maxPrice)) return false;

            if (!category) return true;

            const categoryText = String(product.subcategory || '').toLowerCase();
            const nameText = String(product.name || '').toLowerCase();
            const specs = product.specs || {};

            if (category === 'storage') {
                return /ssd|hdd|storage/i.test(nameText + ' ' + categoryText) || specs.capacity !== undefined;
            }
            if (category === 'gpu') {
                return /radeon|nvidia|geforce|rtx|gtx/i.test(nameText + ' ' + categoryText) || specs.vram !== undefined;
            }
            if (category === 'cpu') {
                return /intel|ryzen|core|athlon/i.test(nameText + ' ' + categoryText) || specs.socket !== undefined;
            }
            if (category === 'ram') {
                return /ddr/i.test(nameText + ' ' + categoryText) || specs.capacity !== undefined;
            }
            if (category === 'motherboard') {
                return /motherboard|board|am4|am5|lga/i.test(nameText + ' ' + categoryText) || specs.socket !== undefined;
            }
            if (category === 'psu') {
                return /psu|power supply|watt/i.test(nameText + ' ' + categoryText) || specs.power !== undefined;
            }
            if (category === 'cooler') {
                return /cooler|cooling|fan|aio/i.test(nameText + ' ' + categoryText);
            }

            return categoryText.includes(category);
        });
    }, [results, minPrice, maxPrice, category]);

    const categories = ['cpu', 'gpu', 'ram', 'motherboard', 'storage', 'psu', 'cooler'];

    const clearFilters = () => {
        setQuery('');
        setCategory(null);
        setMinPrice('');
        setMaxPrice('');
    };

    return (
        <Layout>
            <div className="min-h-[calc(100vh-4rem)] py-6">
                <div className="max-w-6xl mx-auto px-4">
                    <div className="soft-card border border-[var(--border-strong)] p-5 md:p-6 mb-5 bg-[linear-gradient(135deg,var(--surface)_0%,var(--surface-soft)_100%)]">
                        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                            <div className="max-w-2xl">
                                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border-soft)] bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[color:var(--text-soft)]">
                                    <Sparkles className="w-3.5 h-3.5" />
                                    {pageHint}
                                </div>
                                <h2 className="mt-3 text-3xl font-bold">Products</h2>
                                <p className="mt-2 text-sm text-[color:var(--text-soft)] max-w-xl">
                                    Browse a starter set of components, then narrow the list by category, price, or free-text search.
                                </p>
                            </div>

                            <div className="w-full lg:w-[22rem] relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[color:var(--text-soft)]" />
                                <input
                                    className="input-premium w-full pl-10"
                                    placeholder="Search by name, brand or model"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="mt-4 flex flex-wrap items-center gap-2">
                            {categories.map((item) => (
                                <button
                                    key={item}
                                    onClick={() => setCategory((current) => (current === item ? null : item))}
                                    className={`px-3.5 py-2 rounded-full border text-sm font-semibold transition-all duration-150 ${category === item ? 'bg-[var(--primary)] border-[var(--primary)] text-white shadow-md' : 'bg-[var(--surface)] border-[var(--border-soft)] text-[color:var(--text-main)] hover:border-[var(--border-strong)]'}`}
                                >
                                    {item.toUpperCase()}
                                </button>
                            ))}

                            <button
                                type="button"
                                onClick={clearFilters}
                                className="ml-auto inline-flex items-center gap-2 px-3.5 py-2 rounded-full border border-[var(--border-soft)] bg-[var(--surface)] text-sm font-semibold text-[color:var(--text-main)] hover:border-[var(--border-strong)]"
                            >
                                <SlidersHorizontal className="w-4 h-4" />
                                Reset
                            </button>
                        </div>

                        <div className="mt-4 flex flex-wrap items-center gap-2">
                            <input value={minPrice} onChange={(e) => setMinPrice(e.target.value)} placeholder="Min price" className="input-premium w-32" />
                            <input value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} placeholder="Max price" className="input-premium w-32" />
                            <div className="text-xs text-[color:var(--text-soft)]">
                                Pick a category to quick-search a starter set, then refine it with text and price.
                            </div>
                        </div>
                    </div>

                    {loading ? (
                        <div className="py-12 flex items-center justify-center">
                            <Loader2 className="w-6 h-6 animate-spin text-[color:var(--text-soft)]" />
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                            {filtered.length === 0 ? (
                                <div className="text-center text-[color:var(--text-soft)] py-10 col-span-full">
                                    No products found. Try a different search or choose a category.
                                </div>
                            ) : (
                                filtered.map((product: any) => {
                                    const productId = getProductId(product);
                                    const imageSrc = product.image || product.image_small || '';
                                    const specEntries = Object.entries(product.specs || {}).slice(0, 2);
                                    const displayCategory = String(product.subcategory || product.category || 'Component').toUpperCase();

                                    return (
                                        <Link
                                            to={`/product/${productId}`}
                                            state={{ from: '/products' }}
                                            key={productId}
                                            className="group soft-card overflow-hidden rounded-3xl border border-[var(--border-soft)] bg-[linear-gradient(180deg,var(--surface)_0%,var(--surface-soft)_100%)] transition-all duration-200 hover:-translate-y-1 hover:shadow-[var(--shadow-elevated)]"
                                        >
                                            <div className="aspect-square bg-[var(--surface-muted)] relative overflow-hidden border-b border-[var(--border-soft)] flex items-center justify-center">
                                                {imageSrc ? (
                                                    <img
                                                        src={imageSrc}
                                                        alt={product.name}
                                                        className="max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
                                                    />
                                                ) : (
                                                    <div className="flex items-center justify-center text-sm text-[color:var(--text-soft)]">
                                                        No image
                                                    </div>
                                                )}
                                                <div className="absolute top-3 left-3 inline-flex items-center rounded-full bg-black/60 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur-sm">
                                                    {displayCategory}
                                                </div>
                                            </div>

                                            <div className="p-4">
                                                <div className="flex items-start justify-between gap-3">
                                                    <div className="min-w-0">
                                                        <div className="text-[0.75rem] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-soft)]">
                                                            {product.brand || 'Unknown brand'}
                                                        </div>
                                                        <div className="mt-1 text-lg font-semibold leading-snug line-clamp-2">
                                                            {product.name}
                                                        </div>
                                                    </div>
                                                    <div className="shrink-0 text-right">
                                                        <div className="text-xl font-bold text-[color:var(--text-main)]">
                                                            ₴{product.price}
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="mt-3 flex flex-wrap gap-2">
                                                    <span className="tag-chip bg-[var(--surface)] border-[var(--border-soft)] text-[color:var(--text-main)]">
                                                        View details
                                                    </span>
                                                    {product.compatible !== false && (
                                                        <span className="tag-chip bg-emerald-50 border-emerald-200 text-emerald-800">
                                                            Ready to compare
                                                        </span>
                                                    )}
                                                </div>

                                                <div className="mt-3 text-sm text-[color:var(--text-soft)] line-clamp-2 min-h-[2.5rem]">
                                                    {specEntries.length > 0
                                                        ? specEntries.map(([key, value]) => `${key}: ${String(value)}`).join(' • ')
                                                        : 'Open this card to see the full product details and specs.'}
                                                </div>
                                            </div>
                                        </Link>
                                    );
                                })
                            )}
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
}
