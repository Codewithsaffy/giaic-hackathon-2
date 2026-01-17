---
name: nextjs16-fullstack-pattern
description: Expert in Next.js 16 fullstack applications with App Router, TypeScript, and integrated API patterns. Handles client-server communication, authentication integration, and modern React patterns.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Next.js 16 Fullstack Pattern

This skill should be used when implementing Next.js 16 applications with the App Router, TypeScript, and integrated backend services.

## Core Capabilities

### 1. App Router Structure

#### Root Layout with Authentication
```typescript
import './globals.css';
import { ThemeProvider } from '@/components/theme-provider';
import { AuthProvider } from '@/components/auth-provider';
import { Toaster } from '@/components/ui/sonner';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### 2. Client-Side Authentication Provider

#### Auth Context Provider
```typescript
'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useSession } from '@/lib/auth-client';

interface AuthContextType {
  user: any | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending } = useSession();

  const [authState, setAuthState] = useState<AuthContextType>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  useEffect(() => {
    setAuthState({
      user: session?.user || null,
      isLoading: isPending,
      isAuthenticated: !!session?.user,
    });
  }, [session, isPending]);

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 3. API Client Integration

#### Client-Side API Client with JWT
```typescript
import { authClient } from './auth-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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
```

### 4. Server-Side API Client

#### Server Components API Integration
```typescript
import { cookies } from 'next/headers';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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
  getAll: (userId: string) =>
    apiClientServer<Task[]>(`/api/${userId}/tasks`),

  getById: (userId: string, id: string) =>
    apiClientServer<Task>(`/api/${userId}/tasks/${id}`),

  create: (userId: string, taskData: { title: string; description?: string }) =>
    apiClientServer<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: taskData
    }),

  update: (userId: string, id: string, taskData: Partial<Task>) =>
    apiClientServer<Task>(`/api/${userId}/tasks/${id}`, {
      method: 'PUT',
      body: taskData
    }),

  delete: (userId: string, id: string) =>
    apiClientServer<void>(`/api/${userId}/tasks/${id}`, {
      method: 'DELETE'
    })
};
```

### 5. Component Patterns

#### Protected Route Component
```typescript
'use client';

import { useAuth } from '@/contexts/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { toast } from 'sonner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ children, fallback = null }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      toast.error('Please sign in to access this page');
      router.push('/auth/sign-in');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return fallback;
  }

  return <>{children}</>;
}
```

#### Data Fetching Component with Error Boundary
```typescript
'use client';

import { useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

interface DataFetcherProps<T> {
  fetchFunction: () => Promise<T>;
  children: (data: T, isLoading: boolean) => ReactNode;
  onError?: (error: Error) => void;
}

export function DataFetcher<T>({
  fetchFunction,
  children,
  onError
}: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const result = await fetchFunction();
        setData(result);
        setError(null);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        if (onError) {
          onError(error);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return <div className="text-red-500">Error: {error.message}</div>;
  }

  return <>{children(data as T, isLoading)}</>;
}
```

### 6. Form Handling with React Hook Form

#### Form Component Pattern
```typescript
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { toast } from 'sonner';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  onSuccess?: () => void;
  initialData?: TaskFormData;
}

export function TaskForm({ onSuccess, initialData }: TaskFormProps) {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: initialData || {
      title: '',
      description: '',
    },
  });

  const onSubmit = async (data: TaskFormData) => {
    try {
      if (initialData) {
        // Update existing task
        await api.updateTask(initialData.id, data);
        toast.success('Task updated successfully');
      } else {
        // Create new task
        await api.createTask(data);
        toast.success('Task created successfully');
      }

      if (onSuccess) {
        onSuccess();
      }
      form.reset();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      toast.error(`Failed to save task: ${errorMessage}`);
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input
          {...form.register('title')}
          placeholder="Task title"
          className={form.formState.errors.title ? 'border-red-500' : ''}
        />
        {form.formState.errors.title && (
          <p className="text-red-500 text-sm mt-1">{form.formState.errors.title.message}</p>
        )}
      </div>

      <div>
        <Input
          {...form.register('description')}
          placeholder="Description (optional)"
        />
      </div>

      <Button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? 'Saving...' : initialData ? 'Update' : 'Create'}
      </Button>
    </form>
  );
}
```

### 7. Environment Configuration

#### Frontend (.env)
```bash
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

### 8. Component Composition Pattern

#### Page Layout with Sidebar
```typescript
import { Sidebar } from '@/components/sidebar';
import { ReactNode } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  );
}
```

## Best Practices

1. **Type Safety**: Use TypeScript interfaces for all API responses and props
2. **Error Boundaries**: Implement error boundaries for graceful error handling
3. **Loading States**: Always handle loading and error states in components
4. **Authentication Flow**: Implement consistent authentication patterns across components
5. **API Client Consistency**: Use centralized API clients with proper error handling
6. **Component Composition**: Favor composition over inheritance for reusable UI
7. **Accessibility**: Ensure all components are accessible with proper ARIA attributes
8. **Performance**: Use React.memo and useCallback for performance optimization
9. **Security**: Sanitize user input and validate data before sending to API
10. **User Experience**: Provide feedback for all user interactions

## Modern React Patterns

1. **Server Components**: Leverage server components for data fetching
2. **Streaming**: Use React streaming for improved loading experiences
3. **Suspense**: Implement Suspense boundaries for async components
4. **Actions**: Use React Actions for server-side mutations
5. **Caching**: Implement proper caching strategies with `cache` and `fetch`
6. **Parallel Routes**: Use parallel routes for complex layouts
7. **Intercepting Routes**: Use intercepting routes for modal overlays

## Troubleshooting

### Common Issues
- Hydration errors: Ensure client and server render consistently
- Loading states: Handle async operations with proper loading indicators
- Authentication: Verify JWT token handling between client and server
- Data fetching: Use proper error handling and caching strategies
- Form validation: Implement consistent validation across forms