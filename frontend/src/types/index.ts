export interface Product {
    product_id: number;
    external_id: number | null;
    name: string;
    price: number;
    category: string;
    image_small?: string | null;
    image?: string | null;
    brand?: string | null;
    subcategory?: string | null;
    specs?: Record<string, string | number | boolean | null | undefined>;
    score?: number;
    compatible?: boolean;
    compatibility_details?: string[];
}

export interface ComponentRecommendation extends Product {
    score: number;
    compatible: boolean;
    compatibility_details: string[];
}

export interface Build {
    id: number;
    user_id: number;
    name: string;
    budget: number | null;
    goal: string;
    selected_components: Record<string, Product>;
    total_price: number;
    compatibility_warnings: string[];
    created_at: string;
    updated_at: string;
}

export interface BuildCreatePayload {
    user_id: number;
    name: string;
    budget: number | null;
    goal: string;
}

export interface ScrapingResponse {
    task_id: string;
    category: string;
    status: string;
}

export const COMPONENT_CATEGORIES = [
    'cpu',
    'motherboard',
    'ram',
    'gpu',
    'psu',
    'storage',
    'cooler',
];

export const BUILD_GOALS = ['esports', 'aaa', 'office', 'balanced'];

export const SCRAPING_CATEGORIES = [
    'cpu',
    'gpu',
    'ram',
    'ssd',
    'hdd',
    'motherboard',
    'psu',
    'air_cooling',
    'liquid_cooling',
];
