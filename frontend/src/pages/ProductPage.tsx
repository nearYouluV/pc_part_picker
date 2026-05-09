import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import Layout from '../components/Layout';
import ProductDetail from '../components/ProductDetail';
import { productAPI, builderAPI } from '../lib/apiClient';
import type { Product } from '../types';

export default function ProductPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    const [product, setProduct] = useState<Product | null>(null);
    const [builds, setBuilds] = useState<Array<any>>([]);
    const [selectedBuild, setSelectedBuild] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    const handleGoBack = () => {
        // If came from products page, go back there; otherwise navigate to products
        if (location.state?.from === '/products') {
            navigate(-1);
        } else {
            navigate('/products');
        }
    };

    useEffect(() => {
        if (!id) return;
        (async () => {
            try {
                const data = await productAPI.getProduct(Number(id));
                setProduct({
                    product_id: data.product_id,
                    external_id: data.external_id,
                    name: data.name,
                    price: data.price,
                    category: '',
                    image_small: data.image_small,
                    image: data.image,
                    brand: data.brand,
                    subcategory: data.subcategory,
                    specs: data.specs || {},
                });
            } catch (err) {
                console.error(err);
            }
        })();

        (async () => {
            try {
                const b = await builderAPI.getBuilds();
                setBuilds(b || []);
                if (b && b.length) setSelectedBuild(b[0].id);
            } catch (err) {
                console.error(err);
            }
        })();
    }, [id]);

    const handleAddToBuild = async () => {
        if (!selectedBuild || !product) return;
        setLoading(true);
        try {
            await builderAPI.addComponent(selectedBuild, product.category || 'storage', product.product_id, 1, false);
            // Navigate to builder
            navigate('/builder');
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="min-h-[calc(100vh-4rem)] py-6">
                <div className="max-w-5xl mx-auto px-4">
                    <div className="flex items-center justify-between gap-4 mb-6">
                        <button
                            onClick={handleGoBack}
                            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--surface)] border border-[var(--border-soft)] hover:bg-[var(--surface-soft)] transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back to Products
                        </button>

                        <div className="flex items-center gap-3 ml-auto">
                            <select
                                value={selectedBuild ?? ''}
                                onChange={(e) => setSelectedBuild(Number(e.target.value))}
                                className="input-premium"
                            >
                                {builds.map((b: any) => (
                                    <option key={b.id} value={b.id}>{b.name}</option>
                                ))}
                            </select>
                            <button onClick={handleAddToBuild} disabled={loading || !selectedBuild} className="btn-primary">
                                {loading ? 'Adding...' : 'Add to build'}
                            </button>
                        </div>
                    </div>

                    <ProductDetail product={product} />
                </div>
            </div>
        </Layout>
    );
}
