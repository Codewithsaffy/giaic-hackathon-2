import { authClient } from './auth-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface Task {
    id: string;
    title: string;
    description?: string;
    completed: boolean;
    created_at: string;
    updated_at: string;
    owner_id: string;
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
    };

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

export const api = {
    getTasks: () =>
        apiClient<Task[]>(userId => `/api/${userId}/tasks`),

    getTaskById: (id: string) =>
        apiClient<Task>(userId => `/api/${userId}/tasks/${id}`),

    createTask: (task: { title: string; description?: string }) =>
        apiClient<Task>(userId => `/api/${userId}/tasks`, {
            method: 'POST',
            body: JSON.stringify(task),
        }),

    updateTask: (id: string, task: { title?: string; description?: string; completed?: boolean }) =>
        apiClient<Task>(userId => `/api/${userId}/tasks/${id}`, {
            method: 'PUT',
            body: JSON.stringify(task),
        }),

    toggleTaskComplete: (id: string) =>
        apiClient<Task>(userId => `/api/${userId}/tasks/${id}/complete`, {
            method: 'PATCH',
        }),

    deleteTask: (id: string) =>
        apiClient<void>(userId => `/api/${userId}/tasks/${id}`, {
            method: 'DELETE',
        }),
};
