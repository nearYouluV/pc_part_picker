import axios from 'axios';
import type { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import type { Product } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
        const response = await apiClient.post('/api/ai/build', {
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
        const response = await apiClient.post('/api/ai/chat', {
            build_id: buildId,
        });
        return response.data;
    },

    async sendMessage(chatId: string, message: string, promptSource: string = 'chat') {
        const response = await apiClient.post('/api/ai/chat/message', {
            chat_id: chatId,
            message,
            prompt_source: promptSource,
        });
        return response.data;
    },

    async getHistory(chatId: string) {
        const response = await apiClient.get(`/api/ai/chat/history/${chatId}`);
        return response.data;
    },
};

// AI Task Methods
export const aiTaskAPI = {
    async getTaskStatus(taskId: string) {
        const response = await apiClient.get(`/api/ai/task/${taskId}`);
        return response.data;
    },
};

export default apiClient;
