import { useEffect, useState } from 'react';
import ProductDetail from './ProductDetail';
import { productAPI } from '../lib/apiClient';
import type { Product } from '../types';

interface Props {
    productId?: number | null;
    product?: Product | null;
    open: boolean;
    onClose: () => void;
}

export default function ProductModal({ productId, product: productProp, open, onClose }: Props) {
    const [product, setProduct] = useState<Product | null>(productProp || null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setProduct(productProp || null);
    }, [productProp]);

    useEffect(() => {
        let mounted = true;
        if (!open) return;
        if (productProp) return; // already have data
        if (!productId) return;

        (async () => {
            setLoading(true);
            try {
                const data = await productAPI.getProduct(Number(productId));
                if (!mounted) return;
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
                // ignore
            } finally {
                if (mounted) setLoading(false);
            }
        })();

        return () => { mounted = false; };
    }, [open, productId, productProp]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-20">
            <div className="absolute inset-0 bg-black/60" onClick={onClose} />
            <div className="relative w-full max-w-4xl p-4">
                <div className="bg-[#071126] rounded-xl shadow-lg max-h-[80vh] w-full overflow-auto">
                    {loading ? (
                        <div className="p-6 text-center">Loading...</div>
                    ) : (
                        <ProductDetail product={product} />
                    )}
                    <div className="p-4 flex justify-end">
                        <button onClick={onClose} className="px-4 py-2 rounded-md bg-[#22344a]">Close</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
