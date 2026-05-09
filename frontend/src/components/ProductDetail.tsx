import type { Product } from '../types';
import { Info } from 'lucide-react';
import Tooltip from './Tooltip';

interface Props {
    product: Product | null;
}

function formatNumber(v: any, decimals = 1) {
    const n = Number(v);
    if (Number.isNaN(n)) return String(v);
    return n % 1 === 0 ? String(n) : n.toFixed(decimals);
}

export default function ProductDetail({ product }: Props) {
    if (!product) return <div className="p-4">Product not found</div>;

    const specs = product.specs || {};

    const isGPU = (() => {
        const sub = String(product.subcategory || '').toLowerCase();
        const name = String(product.name || '');
        return 'vram' in specs || sub.includes('video') || /radeon|nvidia|geforce|gtx|rtx|vram/i.test(name);
    })();

    const renderSpec = (key: string, value: any) => {
        const k = key.toLowerCase();
        if (k === 'l3_cache' || k.includes('l3')) {
            const num = Number(value);
            if (!Number.isNaN(num)) {
                const mb = Math.round(num / 1024);
                return `${mb} MB`;
            }
        }

        if (k === 'performance' || k === 'perfomance') {
            const tip = isGPU
                ? 'Performance data is based on PassMark testing conducted as part of chipset evaluation.'
                : 'This score comes from PassMark test.';
            return (
                <span className="inline-flex items-center gap-2">
                    <span>{String(value)}</span>
                    <Tooltip content={tip}>
                        <Info className="w-3 h-3 text-[color:var(--text-soft)]" />
                    </Tooltip>
                </span>
            );
        }

        if (k === 'min_memory_frequency' || k === 'max_memory_frequency' || k === 'frequency') {
            const num = Number(value);
            if (!Number.isNaN(num)) return `${formatNumber(num, 0)} MHz`;
        }

        if (k === 'max_ram' || k === 'max_memory' || k === 'max_memory_size') {
            const num = Number(value);
            if (!Number.isNaN(num)) return `${formatNumber(num, 0)} GB`;
        }

        if (k === 'memory_bandwidth') {
            const num = Number(value);
            if (!Number.isNaN(num)) {
                const gbps = num / 10000; // convert per UI spec to GB/s
                return `${formatNumber(gbps, 1)} GB/s`;
            }
        }

        if (k === 'capacity') {
            const num = Number(value);
            if (!Number.isNaN(num)) return `${formatNumber(num, 0)} GB`;
        }

        if (k === 'vram') {
            const num = Number(value);
            if (!Number.isNaN(num)) return `${formatNumber(num, 0)} MB`;
        }

        if (k === 'frequency_gb' || (isGPU && k === 'frequency')) {
            const num = Number(value);
            if (!Number.isNaN(num)) {
                const gbps = num / 1000; // convert to GB/s for GPU frequency-like values
                return `${formatNumber(gbps, 1)} GB/s`;
            }
        }

        if (k === 'recommended_power_supply' || k === 'recommended_power' || k === 'recommended_psu') {
            const num = Number(value);
            if (!Number.isNaN(num)) return `${formatNumber(num, 0)} W`;
        }

        return String(value);
    };

    return (
        <div className="max-w-3xl mx-auto p-6">
            <div className="flex gap-6">
                <div className="w-48 h-48 bg-gray-800 rounded-md flex items-center justify-center overflow-hidden">
                    {product.image ? (
                        <img src={product.image} alt={product.name} className="object-contain w-full h-full" />
                    ) : (
                        <div className="text-sm text-gray-400">No image</div>
                    )}
                </div>
                <div className="flex-1">
                    <h1 className="text-2xl font-semibold">{product.name}</h1>
                    <p className="mt-2 text-lg font-medium">₴{product.price?.toLocaleString?.() ?? product.price}</p>
                    <p className="mt-3 text-sm text-gray-300">{product.brand} • {product.subcategory}</p>
                </div>
            </div>

            <section className="mt-6">
                <h3 className="text-sm font-semibold text-gray-300">Specifications</h3>
                <div className="mt-3 grid grid-cols-2 gap-3">
                    {Object.entries(specs).map(([k, v]) => (
                        <div key={k} className="bg-[#0f1720] p-3 rounded-md">
                            <div className="text-xs text-gray-400 uppercase">{k}</div>
                            <div className="mt-1 text-sm text-white truncate">{renderSpec(k, v)}</div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
