---
name: nextjs16-fullstack-pattern
description: |
  This skill should be used when building Next.js 16 App Router pages that fetch data from external APIs. It enforces patterns including centralized API clients, server-first components, and avoiding useEffect for data fetching.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Next.js 16 Fullstack Pattern Guide

This skill enforces the correct patterns for building Next.js 16 App Router pages that fetch data from external APIs, ensuring consistent architecture and best practices.

## Skill Purpose

This skill acts as a **Guide/Standard-Enforcer** that provides a checklist before writing any frontend code to ensure adherence to the following constraints:
- **Strict Separation:** UI components must NOT fetch directly. They must use a centralized `@/lib/api.ts` client.
- **Server First:** Default to Server Components (`async function`). Only use `'use client'` for interactivity.
- **No useEffect:** Strictly forbid `useEffect` for initial data fetching.

## Before Implementation Checklist

Before writing any frontend code, verify the following:

### 1. API Client Setup ✅
- [ ] Centralized API client exists at `@/lib/api.ts`
- [ ] API client handles all external API communication
- [ ] API client includes proper error handling and authentication
- [ ] API client uses appropriate HTTP methods and headers

### 2. Component Architecture ✅
- [ ] Component is defined as an async function (Server Component) by default
- [ ] Only add `'use client'` directive if interactivity is required
- [ ] No `useEffect` hooks used for initial data fetching
- [ ] Data fetching happens at the server level before rendering

### 3. Data Fetching Strategy ✅
- [ ] Server Component fetches data using native `fetch()` with appropriate caching options
- [ ] Use `cache: 'no-store'` for dynamic data that should not be cached
- [ ] Use `next: { revalidate: N }` for incremental static regeneration
- [ ] Use `cache: 'force-cache'` for static data that should be cached
- [ ] Data is passed as props to child components

### 4. Component Separation ✅
- [ ] Server Components handle data fetching and pass data as props
- [ ] Client Components receive data as props and handle interactivity
- [ ] Clear separation between data fetching and UI rendering

## Implementation Patterns

### ✅ CORRECT: Server Component with Data Fetching

```typescript
// app/users/page.tsx
import UserList from '@/components/user-list'

export default async function UsersPage() {
  // Data fetching happens on the server
  const res = await fetch('https://api.example.com/users', {
    cache: 'no-store', // Dynamic data - no caching
    next: { revalidate: 0 } // Ensure fresh data on every request
  })

  if (!res.ok) {
    throw new Error('Failed to fetch users')
  }

  const users = await res.json()

  // Pass data as props to client component
  return <UserList users={users} />
}
```

```typescript
// components/user-list.tsx
'use client' // Only use 'use client' for interactivity

import { useState } from 'react'

interface User {
  id: string
  name: string
  email: string
}

export default function UserList({ users }: { users: User[] }) {
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  return (
    <div>
      <ul>
        {users.map(user => (
          <li key={user.id} onClick={() => setSelectedUser(user)}>
            {user.name}
          </li>
        ))}
      </ul>
      {selectedUser && (
        <div>
          <h3>{selectedUser.name}</h3>
          <p>{selectedUser.email}</p>
        </div>
      )}
    </div>
  )
}
```

### ✅ CORRECT: Centralized API Client

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.example.com'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers?: Record<string, string>
  body?: any
  cache?: RequestCache
  next?: {
    revalidate?: number
  }
}

export async function apiClient<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const config: RequestInit = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    cache: options.cache,
    next: options.next,
    ...(options.body && { body: JSON.stringify(options.body) })
  }

  try {
    const response = await fetch(url, config)

    if (!response.ok) {
      const errorData = await response.text()
      throw new Error(`API request failed: ${response.status} - ${errorData}`)
    }

    return response.json()
  } catch (error) {
    console.error(`API request error for ${url}:`, error)
    throw error
  }
}

// Specific API functions
export const usersApi = {
  getAll: () => apiClient<User[]>('/users'),
  getById: (id: string) => apiClient<User>(`/users/${id}`),
  create: (userData: Omit<User, 'id'>) =>
    apiClient<User>('/users', { method: 'POST', body: userData }),
  update: (id: string, userData: Partial<User>) =>
    apiClient<User>(`/users/${id}`, { method: 'PUT', body: userData }),
  delete: (id: string) =>
    apiClient<void>(`/users/${id}`, { method: 'DELETE' })
}

// Generic API functions for reuse
export const api = {
  get: <T = any>(endpoint: string, options?: Omit<RequestOptions, 'method'>) =>
    apiClient<T>(endpoint, { ...options, method: 'GET' }),
  post: <T = any>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiClient<T>(endpoint, { ...options, method: 'POST', body: data }),
  put: <T = any>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiClient<T>(endpoint, { ...options, method: 'PUT', body: data }),
  delete: <T = any>(endpoint: string, options?: Omit<RequestOptions, 'method'>) =>
    apiClient<T>(endpoint, { ...options, method: 'DELETE' })
}
```

### ❌ INCORRECT: Client Component Fetching Data Directly

```typescript
// DON'T DO THIS
'use client'

import { useState, useEffect } from 'react'

export default function UsersPage() {
  const [users, setUsers] = useState([])

  // FORBIDDEN: useEffect for data fetching
  useEffect(() => {
    fetch('https://api.example.com/users')
      .then(res => res.json())
      .then(setUsers)
  }, [])

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

### ❌ INCORRECT: Direct API Call in Component

```typescript
// DON'T DO THIS
export default async function UsersPage() {
  // FORBIDDEN: Direct fetch without using centralized client
  const res = await fetch('https://api.example.com/users')
  const users = await res.json()

  return <UserList users={users} />
}
```

## Server Actions vs API Routes Guidance

### Use Server Actions When:
- Handling form submissions or mutations
- Need to run server-side logic triggered by client interaction
- Want to avoid creating separate API endpoints
- Need to access server-side resources (databases, file systems)

### Use API Routes When:
- Need to expose endpoints for external services
- Creating webhook handlers
- Need fine-grained control over HTTP response headers/status
- Building public API endpoints

### ✅ Server Action Example:
```typescript
// actions/users.ts
'use server'

import { usersApi } from '@/lib/api'

export async function createUser(userData: any) {
  try {
    const user = await usersApi.create(userData)
    return { success: true, user }
  } catch (error) {
    return { success: false, error: error.message }
  }
}
```

```typescript
// components/user-form.tsx
'use client'

import { createUser } from '@/actions/users'

export default function UserForm() {
  const handleSubmit = async (formData: FormData) => {
    const result = await createUser(Object.fromEntries(formData))
    if (result.success) {
      // Handle success
    }
  }

  return (
    <form action={handleSubmit}>
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit">Create User</button>
    </form>
  )
}
```

## Data Fetching Options in Server Components

### Static Data (cached until manually invalidated):
```typescript
const staticData = await fetch('https://api.example.com/data', {
  cache: 'force-cache' // Default behavior
})
```

### Dynamic Data (fetched on every request):
```typescript
const dynamicData = await fetch('https://api.example.com/data', {
  cache: 'no-store'
})
```

### Incrementally Revalidated Data:
```typescript
const revalidatedData = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 } // Revalidate every 60 seconds
})
```

## Error Handling

Always implement proper error boundaries and error handling:

```typescript
// app/error.tsx
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

## Performance Considerations

- Leverage Next.js 16's streaming capabilities for faster loading
- Use appropriate caching strategies based on data volatility
- Implement proper loading states with Suspense boundaries
- Minimize client-side JavaScript by keeping UI logic in Server Components

## Final Verification Checklist

Before finalizing your component, verify:

- [ ] All data fetching happens in Server Components
- [ ] UI components only receive data as props
- [ ] No `useEffect` hooks used for initial data fetching
- [ ] All API calls go through centralized `@/lib/api.ts` client
- [ ] Only client components with interactivity have `'use client'` directive
- [ ] Proper error handling is implemented
- [ ] Appropriate caching strategy is applied
- [ ] Component follows the server-first architecture pattern
- [ ] Error boundaries are implemented for graceful error handling
- [ ] Loading states are handled with Suspense boundaries where appropriate
- [ ] API calls include proper error handling and status code checks
- [ ] Cache strategies are appropriate for the data type (static vs dynamic)