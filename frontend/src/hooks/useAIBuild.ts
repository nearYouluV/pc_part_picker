import { useState } from 'react';
import { aiBuildAPI } from '../lib/apiClient';
import { toast } from 'sonner';
import type { Product } from '../types';
import { aiTaskAPI } from '../lib/apiClient';

interface UseAIBuildReturn {
    loading: boolean;
    error: string | null;
    generateBuild: (
        buildId: number,
        budget: number,
        goal: string,
        candidates: Record<string, Product[]>,
        selectedComponents?: Record<string, number>
    ) => Promise<{ build: Record<string, number>; summary: string } | null>;
}

export function useAIBuild(): UseAIBuildReturn {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Poll for task completion
    const pollTaskStatus = async (
        taskId: string,
        maxAttempts: number = 300, // 5 minutes with 1 second intervals
        interval: number = 1000
    ) => {
        let attempts = 0;

        while (attempts < maxAttempts) {
            try {
                const taskStatus = await aiTaskAPI.getTaskStatus(taskId);

                if (taskStatus.status === 'completed') {
                    return taskStatus.result;
                } else if (taskStatus.status === 'failed') {
                    throw new Error(taskStatus.error || 'Task failed');
                } else if (taskStatus.status === 'pending' || taskStatus.status === 'processing') {
                    // Still processing, wait and retry
                    await new Promise(resolve => setTimeout(resolve, interval));
                    attempts++;
                } else {
                    await new Promise(resolve => setTimeout(resolve, interval));
                    attempts++;
                }
            } catch (err) {
                throw err;
            }
        }

        throw new Error('Task polling timeout');
    };

    const generateBuild = async (
        buildId: number,
        budget: number,
        goal: string,
        candidates: Record<string, Product[]>,
        selectedComponents?: Record<string, number>
    ) => {
        setLoading(true);
        setError(null);

        try {
            const result = await aiBuildAPI.generateBuild(
                buildId,
                budget,
                goal,
                candidates,
                selectedComponents
            );

            // Task dispatched, now poll for result
            toast.loading('Generating build with AI...');
            const taskResult = await pollTaskStatus(result.task_id);
            toast.dismiss();

            toast.success('PC build generated with AI!');
            return taskResult;
        } catch (err: any) {
            const errorMessage = err?.response?.data?.detail || 'Failed to generate build with AI';
            setError(errorMessage);
            toast.error(errorMessage);
            return null;
        } finally {
            setLoading(false);
        }
    };

    return {
        loading,
        error,
        generateBuild,
    };
}
