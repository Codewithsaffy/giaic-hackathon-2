import { authClient } from './auth-client';

// Resolve the API Base URL.
// Priority:
// 1. INTERNAL_API_URL (Server-side Docker/K8s networking)
// 2. NEXT_PUBLIC_API_URL (Client-side browser access)
// 3. Fallback to localhost
const internalUrl = process.env.INTERNAL_API_URL;
const publicUrl = process.env.NEXT_PUBLIC_API_URL;

const API_BASE_URL = (typeof window === 'undefined' && internalUrl)
    ? internalUrl
    : (publicUrl || 'http://localhost:8000');

export interface Task {
    id: number;
    title: string;
    description?: string;
    completed: boolean;
    created_at: string;
    updated_at: string;
    user_id: string;
    // New fields
    priority?: number;
    tags?: string;
    due_date?: string;
    remind_at?: string;
    recurring_interval?: string;
}

// JWT token storage (in-memory for security)
let cachedJWT: string | null = null;

/**
 * Get JWT token from Better Auth
 * Caches token to avoid repeated requests
 */
async function getJWTToken(): Promise<string> {
    // Return cached token if available
    if (cachedJWT) {
        return cachedJWT;
    }

    // Get token from Better Auth
    const { data, error } = await authClient.token();

    if (error || !data?.token) {
        throw new Error('Failed to get JWT token: ' + (error?.message || 'No token returned'));
    }

    // Cache the token
    cachedJWT = data.token;
    return cachedJWT;
}

/**
 * Clear cached JWT (call on sign out)
 */
export function clearJWTCache() {
    cachedJWT = null;
}

/**
 * Get current session and user ID
 */
async function getUserId(): Promise<string> {
    const { data } = await authClient.getSession();

    if (!data?.user?.id) {
        throw new Error('Unauthorized: No active session');
    }

    return data.user.id;
}

/**
 * Generic API client with JWT authentication
 */
async function apiClient<T>(
    endpoint: string | ((userId: string) => string),
    options: RequestInit = {}
): Promise<T> {
    const userId = await getUserId();
    const jwt = await getJWTToken();

    // Resolve endpoint
    const urlPath = typeof endpoint === 'function' ? endpoint(userId) : endpoint;

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwt}`,
        ...options.headers,
    } as Record<string, string>;

    const response = await fetch(`${API_BASE_URL}${urlPath}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({
            detail: 'Unknown error occurred'
        }));
        throw new Error(errorData.detail || `API Error: ${response.statusText}`);
    }

    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

export interface GetTasksParams {
    offset?: number;
    limit?: number;
    completed?: boolean;
    priority?: number;
    tag?: string;
    search?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
}

export const api = {
    getTasks: (params: GetTasksParams = {}) => {
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined) queryParams.append(key, value.toString());
        });
        const queryString = queryParams.toString();
        const suffix = queryString ? `?${queryString}` : '';

        return apiClient<Task[]>(userId => `/api/${userId}/tasks${suffix}`);
    },

    getTaskById: (id: number) =>
        apiClient<Task>(userId => `/api/${userId}/tasks/${id}`),

    createTask: (task: {
        title: string;
        description?: string;
        priority?: number;
        tags?: string;
        due_date?: string;
        remind_at?: string;
        recurring_interval?: string;
    }) =>
        apiClient<Task>(userId => `/api/${userId}/tasks`, {
            method: 'POST',
            body: JSON.stringify(task),
        }),

    updateTask: (id: number, task: {
        title?: string;
        description?: string;
        completed?: boolean;
        priority?: number;
        tags?: string;
        due_date?: string;
        remind_at?: string;
        recurring_interval?: string;
    }) =>
        apiClient<Task>(userId => `/api/${userId}/tasks/${id}`, {
            method: 'PUT',
            body: JSON.stringify(task),
        }),

    toggleTaskComplete: (id: number) =>
        apiClient<Task>(userId => `/api/${userId}/tasks/${id}/complete`, {
            method: 'PATCH',
        }),

    deleteTask: (id: number) =>
        apiClient<void>(userId => `/api/${userId}/tasks/${id}`, {
            method: 'DELETE',
        }),
};
