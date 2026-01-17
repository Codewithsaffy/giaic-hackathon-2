---
name: chatkit-nextjs-integration
description: "Expert knowledge of OpenAI ChatKit React component for building chat interfaces in Next.js apps (2025 version). Use for: creating self-hosted chat UIs connected to custom FastAPI backends, configuring ChatKit with custom API endpoints, domain allowlist setup, theming, start screens, streaming responses, error handling. Covers ChatKit setup, Next.js 14+ App Router integration, environment configuration, and deployment patterns."
author: "AI Todo Chatbot Project"
version: "1.0"
date: "2025-01-11"
---

## Overview

**ChatKit** is OpenAI's pre-built React chat component that provides a production-ready chat UI with zero custom code. It's part of OpenAI's AgentKit suite.

**Key Benefits**:
- **Zero UI code needed**: Complete chat interface out of the box
- **Streaming built-in**: Automatic streaming response animations
- **File uploads**: Support for attachments
- **Mobile responsive**: Works on all devices
- **Dark mode**: Automatic theme detection
- **Accessibility**: Screen reader support

**Two Usage Modes**:
1. **Managed**: ChatKit → OpenAI Agent Builder (easiest, less control)
2. **Self-Hosted**: ChatKit → YOUR FastAPI backend (full control) ← **YOUR PROJECT**

## Important: Prerequisites

### 1. OpenAI Domain Allowlist (CRITICAL!)

**ChatKit will NOT work until you configure this:**

1. Deploy your frontend first (get production URL)
   - Vercel: `https://your-app.vercel.app`
   - GitHub Pages: `https://username.github.io/repo`
   - Custom: `https://yourdomain.com`

2. Add domain to OpenAI allowlist:
   - Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter: `https://your-app.vercel.app` (no trailing slash)
   - Save

3. For local development:
   - Add: `http://localhost:3000`
   - This typically works without manual configuration

**If you skip this step, ChatKit shows blank screen or authentication errors!**

### 2. Backend API Endpoint

ChatKit needs a backend endpoint to send messages to. For your project:
- **Endpoint**: `http://localhost:8000/api/chat` (dev)
- **Endpoint**: `https://your-api.railway.app/api/chat` (prod)

## Installation

```bash
# Create Next.js project
npx create-next-app@latest todo-chatbot
cd todo-chatbot

# Install ChatKit
npm install @openai/chatkit-react

# Install dependencies (if not already included)
npm install react react-dom
```

## Project Structure

```
/todo-chatbot/
  /app/
    page.tsx           # Home page with ChatKit
    layout.tsx         # Root layout
    /api/              # Optional: proxy endpoints
  /components/
    ChatInterface.tsx  # ChatKit wrapper component
  /lib/
    config.ts          # Configuration
  .env.local           # Environment variables
  next.config.js       # Next.js config
```

## Basic ChatKit Setup (Self-Hosted)

### 1. Environment Variables

```bash
# .env.local

# Your FastAPI backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
# OR for production:
# NEXT_PUBLIC_API_URL=https://your-api.railway.app

# User ID (simple auth for now)
NEXT_PUBLIC_USER_ID=user_123
```

### 2. ChatKit Component

```tsx
// components/ChatInterface.tsx
'use client'

import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { useState } from 'react'

interface ChatInterfaceProps {
  userId: string
  apiUrl: string
}

export default function ChatInterface({ userId, apiUrl }: ChatInterfaceProps) {
  const [conversationId, setConversationId] = useState<number | null>(null)

  // Configure ChatKit
  const chatkit = useChatKit({
    // IMPORTANT: Tell ChatKit where to send messages
    api: {
      url: `${apiUrl}/api/chat`,  // Your FastAPI endpoint
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // Transform request to match your backend format
      transformRequest: (message) => ({
        user_id: userId,
        conversation_id: conversationId,
        message: message,
      }),
      // Transform response from your backend
      transformResponse: (data) => {
        // Save conversation ID from first response
        if (data.conversation_id && !conversationId) {
          setConversationId(data.conversation_id)
        }
        
        return {
          message: data.response,
          // Optional: show which tools were called
          metadata: data.tool_calls || [],
        }
      },
    },

    // Customize appearance
    theme: {
      colorScheme: 'light', // or 'dark' or 'auto'
      color: {
        primary: {
          hue: 200,        // Blue
          saturation: 80,
          lightness: 50,
        },
      },
      borderRadius: 12,
    },

    // Start screen configuration
    startScreen: {
      greeting: "👋 Hi! I'm your AI todo assistant. How can I help you today?",
      prompts: [
        {
          label: "➕ Add a task",
          prompt: "Add a task to buy groceries",
          icon: "plus",
        },
        {
          label: "📋 Show tasks",
          prompt: "Show me all my pending tasks",
          icon: "list",
        },
        {
          label: "✅ Complete task",
          prompt: "Mark my first task as complete",
          icon: "check",
        },
        {
          label: "🗑️ Delete task",
          prompt: "Delete the task about groceries",
          icon: "trash",
        },
      ],
    },

    // Error handling
    onError: (error) => {
      console.error('ChatKit error:', error)
      // Show user-friendly error message
    },

    // Response completed
    onResponseEnd: () => {
      console.log('Response completed')
      // Optional: trigger analytics, etc.
    },

    // Message sent
    onMessageSent: (message) => {
      console.log('Message sent:', message)
    },
  })

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
      <div className="w-full max-w-2xl">
        <ChatKit 
          control={chatkit.control}
          className="h-[700px] rounded-xl shadow-2xl border border-gray-200"
        />
      </div>
    </div>
  )
}
```

### 3. Main Page

```tsx
// app/page.tsx
import ChatInterface from '@/components/ChatInterface'

export default function Home() {
  const userId = process.env.NEXT_PUBLIC_USER_ID || 'default_user'
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  return (
    <main>
      <ChatInterface 
        userId={userId}
        apiUrl={apiUrl}
      />
    </main>
  )
}
```

## Advanced Configuration

### Custom Styling

```tsx
const chatkit = useChatKit({
  theme: {
    colorScheme: 'auto', // Follows system preference
    
    color: {
      primary: {
        hue: 200,
        saturation: 80,
        lightness: 50,
      },
      // Can also customize other colors
      background: {
        hue: 0,
        saturation: 0,
        lightness: 98,
      },
    },
    
    borderRadius: 16, // Roundness of UI elements
    
    fontFamily: {
      base: 'system-ui, sans-serif',
      mono: 'monospace',
    },
    
    spacing: 'comfortable', // or 'compact'
  },
  
  // Custom CSS
  className: "my-custom-chatkit",
})
```

### Handle Streaming Responses

If your backend supports streaming (recommended):

```tsx
const chatkit = useChatKit({
  api: {
    url: `${apiUrl}/api/chat/stream`,
    method: 'POST',
    stream: true, // Enable streaming
    
    transformRequest: (message) => ({
      user_id: userId,
      message: message,
    }),
    
    // Handle streaming events
    onStream: (chunk) => {
      console.log('Received chunk:', chunk)
    },
  },
})
```

FastAPI streaming endpoint:

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        # Stream agent response
        result = Runner.run_streamed(agent, request.message)
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                yield f"data: {json.dumps({'content': event.item})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### File Upload Support

ChatKit supports file uploads out of the box:

```tsx
const chatkit = useChatKit({
  api: {
    url: `${apiUrl}/api/chat`,
    method: 'POST',
    
    transformRequest: (message, files) => {
      const formData = new FormData()
      formData.append('user_id', userId)
      formData.append('message', message)
      
      // Add uploaded files
      if (files && files.length > 0) {
        files.forEach((file, index) => {
          formData.append(`file_${index}`, file)
        })
      }
      
      return formData
    },
  },
  
  // Configure file upload settings
  fileUpload: {
    enabled: true,
    maxFileSize: 10 * 1024 * 1024, // 10MB
    acceptedFileTypes: ['.pdf', '.txt', '.md'],
  },
})
```

Backend file handling:

```python
from fastapi import File, UploadFile

@router.post("/chat")
async def chat_with_files(
    user_id: str,
    message: str,
    file_0: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    # Handle file if present
    if file_0:
        contents = await file_0.read()
        # Process file...
    
    # Process message...
    return {"response": "..."}
```

### Conversation History

ChatKit can load previous messages:

```tsx
const [messages, setMessages] = useState([])

const chatkit = useChatKit({
  // Load previous messages
  initialMessages: messages,
  
  api: {
    url: `${apiUrl}/api/chat`,
    transformRequest: (message) => ({
      user_id: userId,
      conversation_id: conversationId,
      message: message,
    }),
    transformResponse: (data) => {
      // Add new message to state
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
      }])
      
      return { message: data.response }
    },
  },
})

// Load history on mount
useEffect(() => {
  async function loadHistory() {
    const response = await fetch(`${apiUrl}/api/conversations/${conversationId}`)
    const data = await response.json()
    setMessages(data.messages)
  }
  
  if (conversationId) {
    loadHistory()
  }
}, [conversationId])
```

## Error Handling

```tsx
const chatkit = useChatKit({
  onError: (error) => {
    console.error('ChatKit error:', error)
    
    // Show toast notification
    toast.error('Failed to send message. Please try again.')
    
    // Log to error tracking
    Sentry.captureException(error)
  },
  
  // Retry configuration
  retry: {
    enabled: true,
    maxAttempts: 3,
    delay: 1000, // ms
  },
})
```

## Production Deployment

### 1. Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# - NEXT_PUBLIC_API_URL
# - NEXT_PUBLIC_USER_ID (optional)
```

### 2. Environment Variables

```bash
# Production .env.local
NEXT_PUBLIC_API_URL=https://your-api.railway.app
NEXT_PUBLIC_USER_ID=user_production
```

### 3. Update CORS in FastAPI

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Dev
        "https://your-app.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Add Domain to OpenAI Allowlist

After deploying to Vercel:
1. Get your URL: `https://your-app.vercel.app`
2. Add to OpenAI allowlist (see Prerequisites)
3. Wait a few minutes for propagation

## Testing

```tsx
// __tests__/ChatInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import ChatInterface from '@/components/ChatInterface'

test('renders chat interface', () => {
  render(<ChatInterface userId="test" apiUrl="http://localhost:8000" />)
  
  const input = screen.getByPlaceholderText(/type a message/i)
  expect(input).toBeInTheDocument()
})

test('sends message', async () => {
  render(<ChatInterface userId="test" apiUrl="http://localhost:8000" />)
  
  const input = screen.getByPlaceholderText(/type a message/i)
  fireEvent.change(input, { target: { value: 'Add task' } })
  
  const sendButton = screen.getByRole('button', { name: /send/i })
  fireEvent.click(sendButton)
  
  // Assert message sent
  expect(input.value).toBe('')
})
```

## Common Issues & Solutions

### Issue 1: Blank ChatKit Screen

**Causes**:
- Domain not in OpenAI allowlist
- Incorrect API URL
- CORS errors

**Solutions**:
1. Check browser console for errors
2. Verify domain in allowlist
3. Check CORS configuration
4. Verify API endpoint is accessible

### Issue 2: Messages Not Sending

**Causes**:
- Backend not responding
- Incorrect request format
- Network issues

**Solutions**:
1. Check Network tab in DevTools
2. Verify `transformRequest` format matches backend
3. Test backend endpoint with curl/Postman
4. Check backend logs

### Issue 3: Streaming Not Working

**Causes**:
- Backend doesn't support SSE
- Incorrect stream configuration

**Solutions**:
1. Implement streaming endpoint (see above)
2. Set `stream: true` in config
3. Use `StreamingResponse` in FastAPI

## Best Practices

### 1. Environment Variables

```tsx
// lib/config.ts
export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  userId: process.env.NEXT_PUBLIC_USER_ID || 'default_user',
} as const

// Use in components
import { config } from '@/lib/config'
```

### 2. Error Boundaries

```tsx
// components/ErrorBoundary.tsx
'use client'

import React from 'react'

export class ErrorBoundary extends React.Component {
  componentDidCatch(error, info) {
    console.error('ChatKit error:', error, info)
  }

  render() {
    return this.props.children
  }
}

// Use it
<ErrorBoundary>
  <ChatInterface {...props} />
</ErrorBoundary>
```

### 3. Loading States

```tsx
const [isLoading, setIsLoading] = useState(true)

useEffect(() => {
  // Simulate loading
  setTimeout(() => setIsLoading(false), 1000)
}, [])

if (isLoading) {
  return <div>Loading chat...</div>
}

return <ChatKit control={chatkit.control} />
```

### 4. Analytics

```tsx
const chatkit = useChatKit({
  onMessageSent: (message) => {
    // Track with your analytics
    analytics.track('message_sent', {
      length: message.length,
      timestamp: Date.now(),
    })
  },
  
  onResponseEnd: () => {
    analytics.track('response_received')
  },
})
```

## Complete Working Example

```tsx
// app/page.tsx
'use client'

import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { useState, useEffect } from 'react'

export default function Home() {
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const chatkit = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL}/api/chat`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      transformRequest: (message) => {
        setIsLoading(true)
        return {
          user_id: process.env.NEXT_PUBLIC_USER_ID,
          conversation_id: conversationId,
          message: message,
        }
      },
      transformResponse: (data) => {
        setIsLoading(false)
        
        if (data.conversation_id && !conversationId) {
          setConversationId(data.conversation_id)
          localStorage.setItem('conversation_id', data.conversation_id.toString())
        }
        
        return {
          message: data.response,
          metadata: {
            tools: data.tool_calls || [],
          },
        }
      },
    },
    
    theme: {
      colorScheme: 'auto',
      color: {
        primary: { hue: 200, saturation: 80, lightness: 50 },
      },
      borderRadius: 16,
    },
    
    startScreen: {
      greeting: "Hi! I'm your AI todo assistant 🤖",
      prompts: [
        { label: "Add task", prompt: "Add a task to buy groceries", icon: "plus" },
        { label: "Show tasks", prompt: "Show me all my tasks", icon: "list" },
        { label: "Complete", prompt: "Mark first task as done", icon: "check" },
      ],
    },
    
    onError: (error) => {
      console.error('Error:', error)
      setIsLoading(false)
    },
  })

  // Load conversation ID from localStorage
  useEffect(() => {
    const savedId = localStorage.getItem('conversation_id')
    if (savedId) {
      setConversationId(parseInt(savedId))
    }
  }, [])

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-900">
          AI Todo Assistant
        </h1>
        
        <ChatKit 
          control={chatkit.control}
          className="h-[600px] rounded-2xl shadow-2xl border border-gray-200"
        />
        
        {isLoading && (
          <div className="mt-4 text-center text-gray-600">
            Processing...
          </div>
        )}
      </div>
    </main>
  )
}
```

## Key Takeaways

1. **Domain Allowlist is MANDATORY** - Add to OpenAI settings first
2. **Self-hosted = Full control** - ChatKit → Your FastAPI
3. **transformRequest/Response** - Match your backend format
4. **Zero UI code needed** - ChatKit handles everything
5. **Streaming is built-in** - Just configure backend
6. **Mobile responsive** - Works everywhere
7. **Theme customization** - Match your brand
8. **Error handling** - Use onError callback
9. **Conversation state** - Manage with conversationId
10. **Production ready** - Deploy to Vercel/Netlify

## Resources

- ChatKit Docs: https://openai.github.io/chatkit-js/
- Examples: https://github.com/openai/openai-chatkit-advanced-samples
- Next.js Docs: https://nextjs.org/docs
- OpenAI Platform: https://platform.openai.com