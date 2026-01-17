# Quickstart Guide: Todo App

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL-compatible database (Neon recommended)
- Git

## Setup Instructions

### 1. Clone and Initialize Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi[all] sqlmodel sqlalchemy[asyncio] asyncpg python-multipart better-auth[jose] python-jose[cryptography] httpx

# Set environment variables
cp .env.example .env
# Edit .env with your database URL and auth secrets
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install next@latest react react-dom typescript @types/react @types/node better-auth @better-auth/next-js
# or
yarn add next react react-dom typescript @types/react @types/node better-auth @better-auth/next-js

# Set environment variables
cp .env.example .env
# Edit .env with your API URLs and auth configuration
```

### 4. Environment Configuration

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Auth
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_ISSUER=https://your-app.com
BETTER_AUTH_AUDIENCE=https://your-app.com

# API
API_URL=http://localhost:8000
```

#### Frontend (.env)
```bash
# Frontend
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth
BETTER_AUTH_URL=http://localhost:3000/api/auth
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

### 5. Run Development Servers

#### Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
# Frontend will be available at http://localhost:3000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Tasks
- `GET /api/todos` - Get current user's tasks
- `POST /api/todos` - Create new task
- `PUT /api/todos/{id}` - Update task
- `DELETE /api/todos/{id}` - Delete task

## Key Integration Points

### 1. JWT Token Flow
- User authenticates through Better Auth on frontend
- JWT token is issued and stored in browser
- Token is sent in Authorization header to backend API
- Backend validates JWT using same secret as Better Auth

### 2. Data Isolation
- Backend extracts user ID from JWT token
- All database queries filtered by user ID
- Users can only access their own tasks

### 3. Session Management
- Frontend uses Better Auth client for session management
- Sessions automatically refresh when needed
- Inactive sessions redirect to login page

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Deployment

### Backend (Example: Railway)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy backend
railway up
```

### Frontend (Example: Vercel)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
vercel --prod
```