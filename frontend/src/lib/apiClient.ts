import axios from 'axios';
import type { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import type { Product } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to include JWT token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error: AxiosError) => Promise.reject(error)
);

// Add response interceptor for token refresh or error handling
apiClient.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// AI Build Methods
export const aiBuildAPI = {
    async generateBuild(buildId: number, budget: number, goal: string, candidates: Record<string, Array<Product>>, selectedComponents?: Record<string, number>) {
        const response = await apiClient.post('/ai/build', {
            build_id: buildId,
            user_config: { budget, goal },
            candidates: candidates,
            selected_components: selectedComponents,
        });
        return response.data;
    },
};

// AI Chat Methods
export const aiChatAPI = {
    async createChat(buildId: number) {
        const response = await apiClient.post('/ai/chat', {
            build_id: buildId,
        });
        return response.data;
    },

    async sendMessage(chatId: string, message: string, promptSource: string = 'chat') {
        const response = await apiClient.post('/ai/chat/message', {
            chat_id: chatId,
            message,
            prompt_source: promptSource,
        });
        return response.data;
    },

    async getHistory(chatId: string) {
        const response = await apiClient.get(`/ai/chat/history/${chatId}`);
        return response.data;
    },
};

// AI Task Methods
export const aiTaskAPI = {
    async getTaskStatus(taskId: string) {
        const response = await apiClient.get(`/ai/task/${taskId}`);
        return response.data;
    },
};

// Product Methods
export const productAPI = {
    async getProduct(productId: number) {
        const response = await apiClient.get(`/product/${productId}`);
        return response.data;
    },
    async search(query: string) {
        const response = await apiClient.get(`/product/search`, { params: { query } });
        return response.data;
    },
};

// Builder Methods
export const builderAPI = {
    async getBuilds() {
        const response = await apiClient.get(`/builder/builds`);
        return response.data;
    },
    async addComponent(buildId: number, category: string, productId: number, quantity: number | null = null, append: boolean = false) {
        const response = await apiClient.post(`/builder/${buildId}/add`, {
            category,
            product_id: productId,
            quantity,
            append,
        });
        return response.data;
    },
};

export const communityAPI = {
    async getPublicBuilds() {
        const response = await apiClient.get('/builder/public-builds');
        return response.data;
    },
    async getPublicBuild(buildId: number) {
        const response = await apiClient.get(`/builder/public-builds/${buildId}`);
        return response.data;
    },
    async getReviews(buildId: number) {
        const response = await apiClient.get(`/builder/public-builds/${buildId}/reviews`);
        return response.data;
    },
    async submitReview(buildId: number, rating: number, comment?: string | null) {
        const response = await apiClient.post(`/builder/public-builds/${buildId}/reviews`, {
            rating,
            comment,
        });
        return response.data;
    },
    async getSuggestions(buildId: number) {
        const response = await apiClient.get(`/builder/public-builds/${buildId}/suggestions`);
        return response.data;
    },
    async submitSuggestion(buildId: number, payload: { category: string; suggested_product_id: number; quantity: number; comment?: string | null; }) {
        const response = await apiClient.post(`/builder/public-builds/${buildId}/suggestions`, payload);
        return response.data;
    },
    async applySuggestion(buildId: number, suggestionId: number) {
        const response = await apiClient.post(`/builder/public-builds/${buildId}/suggestions/${suggestionId}/apply`);
        return response.data;
    },
    async rejectSuggestion(buildId: number, suggestionId: number) {
        const response = await apiClient.post(`/builder/public-builds/${buildId}/suggestions/${suggestionId}/reject`);
        return response.data;
    },
    async setVisibility(buildId: number, isPublic: boolean) {
        const response = await apiClient.put(`/builder/${buildId}`, {
            is_public: isPublic,
        });
        return response.data;
    },
};

export default apiClient;
