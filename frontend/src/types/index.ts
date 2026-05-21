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
    source?: string;
    quantity?: number;
    score?: number;
    compatible?: boolean;
    compatibility_details?: string[];
}

export interface ComponentRecommendation extends Product {
    score: number;
    compatible: boolean;
    compatibility_details: string[];
}

export interface AIRecommendedProduct {
    id: number;
    external_id: number | null;
    name: string;
    price: number;
    category: string;
    image_small?: string | null;
    image?: string | null;
    brand?: string | null;
    subcategory?: string | null;
    specs: Record<string, string | number | boolean | null | undefined>;
    score: number;
    compatible: boolean;
    compatibility_details: string[];
    in_budget?: boolean;
}

export interface AIChatComponentSnapshot {
    product_id?: number | null;
    name?: string | null;
    price?: number | null;
    image_small?: string | null;
}

export interface AIChatChange {
    category: string;
    product_id: number;
    from_name?: string | null;
    to_name?: string | null;
    reason?: string | null;
    from_component?: AIChatComponentSnapshot | null;
    to_component?: AIChatComponentSnapshot | null;
}

export interface AIBuildTaskResult {
    build: Record<string, number | { product_id: number; quantity?: number; append?: boolean } | Array<{ product_id: number; quantity?: number; append?: boolean }>>;
    summary: string;
    recommendations?: Record<string, AIRecommendedProduct[]>;
    recommendation_constraints?: Record<string, unknown>;
    status?: string;
}

export interface BuildReview {
    id: number;
    build_id: number;
    user_id: number;
    username: string;
    rating: number;
    comment?: string | null;
    created_at: string;
    updated_at: string;
}

export interface BuildSuggestion {
    id: number;
    build_id: number;
    user_id: number;
    username: string;
    category: string;
    suggested_product_id: number;
    suggested_product_name: string;
    suggested_product_price: number;
    quantity: number;
    comment?: string | null;
    status: string;
    applied_by_user_id?: number | null;
    applied_by_username?: string | null;
    applied_at?: string | null;
    created_at: string;
    updated_at: string;
}

export interface Build {
    id: number;
    user_id: number;
    name: string;
    budget: number | null;
    goal: string;
    selected_components: Record<string, Product>;
    storage_components?: Product[];
    total_price: number;
    compatibility_warnings: string[];
    is_public?: boolean;
    owner_username?: string | null;
    average_rating?: number | null;
    review_count?: number;
    reviews?: BuildReview[];
    suggestions?: BuildSuggestion[];
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
