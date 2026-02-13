import { cookies } from 'next/headers';

// Resolve the API Base URL. 
// Priority:
// 1. INTERNAL_API_URL (Server-side Docker/K8s networking)
// 2. NEXT_PUBLIC_API_URL (Client-side browser access)
// 3. Fallback to localhost
const internalUrl = process.env.INTERNAL_API_URL;
const publicUrl = process.env.NEXT_PUBLIC_API_URL;

const API_BASE_URL = internalUrl || (publicUrl || 'http://localhost:8000');

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  cache?: RequestCache;
  next?: {
    revalidate?: number;
  };
}

/**
 * Server-side API client that handles all external API communication
 * Attaches JWT token from cookies to requests when available
 */
export async function apiClientServer<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Get the JWT token from cookies
  const cookieStore = await cookies();
  const token = cookieStore.get('better-auth.session_token')?.value;

  const config: RequestInit = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    cache: options.cache,
    next: options.next,
    ...(options.body && { body: JSON.stringify(options.body) })
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`API request failed: ${response.status} - ${errorData}`);
    }

    return response.json();
  } catch (error) {
    console.error(`API request error for ${url}:`, error);
    throw error;
  }
}

// Specific API functions for tasks (server-side)
export const tasksApiServer = {
  getAll: (userId: string, params: Record<string, any> = {}) => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) queryParams.append(key, value.toString());
    });
    const queryString = queryParams.toString();
    const suffix = queryString ? `?${queryString}` : '';
    return apiClientServer<Task[]>(`/api/${userId}/tasks${suffix}`);
  },

  getById: (userId: string, id: number) =>
    apiClientServer<Task>(`/api/${userId}/tasks/${id}`),

  create: (userId: string, taskData: {
    title: string;
    description?: string;
    priority?: number;
    tags?: string;
    due_date?: string;
    remind_at?: string;
    recurring_interval?: string;
  }) =>
    apiClientServer<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: taskData
    }),

  update: (userId: string, id: number, taskData: Partial<Task>) =>
    apiClientServer<Task>(`/api/${userId}/tasks/${id}`, {
      method: 'PUT',
      body: taskData
    }),

  delete: (userId: string, id: number) =>
    apiClientServer<void>(`/api/${userId}/tasks/${id}`, {
      method: 'DELETE'
    })
};

// Type definitions
export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
  priority?: number;
  tags?: string;
  due_date?: string;
  remind_at?: string;
  recurring_interval?: string;
}