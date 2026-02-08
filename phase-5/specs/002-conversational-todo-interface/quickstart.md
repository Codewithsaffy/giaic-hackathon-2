# Quickstart Guide: Conversational Todo Interface

## Overview
This guide explains how to set up and run the conversational todo interface that allows users to manage todos using natural language.

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (Neon Serverless)
- OpenAI API key
- Better Auth configured

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@host:port/database
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET=your_jwt_secret_here
```

### 3. Run Database Migrations
```bash
python -m src.models.migrate
```

### 4. Start the Backend Server
```bash
uvicorn src.main:app --reload --port 8000
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Set Environment Variables
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_API_KEY=your_chatkit_api_key
```

### 3. Start the Frontend
```bash
npm run dev
```

## MCP Server Setup

### 1. Configure MCP Tools
The MCP server will be available at `http://localhost:8001/mcp` and exposes the following tools:
- `add_task`: Create a new task
- `list_tasks`: Get user's tasks
- `update_task`: Modify an existing task
- `complete_task`: Mark a task as completed
- `delete_task`: Remove a task

### 2. Start MCP Server
```bash
python -m src.tools.mcp_server
```

## Using the Chat Interface

1. Navigate to `http://localhost:3000/chat`
2. Authenticate using existing login
3. Start chatting with the AI assistant using natural language:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Complete the meeting prep task"
   - "Delete the old task"

## API Endpoints

### Chat Endpoint
`POST /api/{user_id}/chat`
Send messages to the AI assistant and receive responses.

### Conversations Endpoints
- `GET /api/{user_id}/conversations` - List user's conversations
- `GET /api/{user_id}/conversations/{conversation_id}` - Get specific conversation

## Testing

### Backend Tests
```bash
pytest tests/
```

### Frontend Tests
```bash
npm test
```

## Development

### Adding New MCP Tools
1. Define the tool in `src/tools/task_tools.py`
2. Register it in `src/tools/mcp_tool_registration.py`
3. Update the OpenAPI contract if needed

### Modifying Data Models
1. Update the model in `src/models/`
2. Run migrations: `alembic revision --autogenerate -m "description"`
3. Apply migrations: `alembic upgrade head`

## Troubleshooting

- If the chat interface doesn't load, ensure the backend is running and accessible
- If authentication fails, verify JWT configuration
- If AI responses are slow, check OpenAI API key and rate limits