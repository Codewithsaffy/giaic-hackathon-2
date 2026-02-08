# Research Summary: Todo App Implementation

## Technology Decisions

### Backend Framework: FastAPI
**Decision**: Use FastAPI for the backend REST API
**Rationale**: FastAPI provides excellent performance, automatic API documentation, type validation with Pydantic, and async support which is perfect for the requirements. It integrates well with SQLModel and supports the async patterns needed for Neon PostgreSQL.
**Alternatives considered**:
- Flask: Less performant and requires more manual setup
- Django: Overkill for this simple API-focused application
- Express.js: Would create inconsistency with Python-based data layer

### Database: Neon PostgreSQL with SQLModel
**Decision**: Use Neon PostgreSQL as the database with SQLModel as the ORM
**Rationale**: Neon provides serverless PostgreSQL with excellent scalability and the team already has a validated skill (`fastapi-neon-bridge`) for this combination. SQLModel provides the perfect bridge between SQLAlchemy and Pydantic with type hints.
**Alternatives considered**:
- SQLite: Less scalable for multi-user application
- MongoDB: Would require different skill set and doesn't match the SQLModel requirement
- PostgreSQL with SQLAlchemy only: Missing the Pydantic integration benefits

### Authentication: Better Auth with JWT
**Decision**: Use Better Auth for authentication with JWT tokens
**Rationale**: Better Auth provides a complete authentication solution with JWT support, social login capabilities, and excellent TypeScript/JavaScript integration. The team has a validated skill (`better-auth-expert`) for this technology.
**Alternatives considered**:
- Auth.js/NextAuth: Would only work for Next.js and not backend validation
- Custom JWT implementation: More complex and error-prone
- Firebase Auth: Would create vendor lock-in and doesn't fit the self-hosted requirement

### Frontend Framework: Next.js 16 with App Router
**Decision**: Use Next.js 16 with App Router for the frontend
**Rationale**: Next.js provides excellent developer experience, server-side rendering, and the App Router enables the server-first architecture pattern. The team has a validated skill (`nextjs16-fullstack-pattern`) for this approach.
**Alternatives considered**:
- React with Create React App: Missing server-side rendering benefits
- Vue.js: Would require learning new framework and doesn't have validated skill
- SvelteKit: Doesn't have the same ecosystem and validated skill support

### UI Framework: Tailwind CSS
**Decision**: Use Tailwind CSS for styling
**Rationale**: Tailwind provides utility-first CSS that works well with Next.js, enables responsive design easily, and is widely adopted. It pairs well with the `frontend-design` skill for creating responsive layouts.
**Alternatives considered**:
- CSS Modules: More verbose and harder to maintain consistency
- Styled Components: React-specific and adds runtime overhead
- Bootstrap: Less customizable and heavier

## Integration Patterns

### JWT Token Flow
**Decision**: Use JWT tokens issued by Better Auth and validated by both frontend and backend
**Rationale**: This enables stateless authentication as required by the specification, with tokens validated on both frontend (for UI decisions) and backend (for API access). The token contains user identity that can be verified without database lookups.
**Implementation**:
- Frontend: Uses Better Auth client to manage sessions and tokens
- Backend: Validates JWT tokens using the same secret/key as Better Auth
- API: All endpoints require valid JWT tokens in Authorization header

### API Contract Design
**Decision**: RESTful API with standard HTTP methods and status codes
**Rationale**: REST APIs are well-understood, easily documented, and work well with the constraints. The API will follow standard patterns for CRUD operations.
**Endpoints planned**:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/todos` - Get user's todos
- `POST /api/todos` - Create new todo
- `PUT /api/todos/{id}` - Update todo
- `DELETE /api/todos/{id}` - Delete todo

### Data Isolation Strategy
**Decision**: User ID scoping in all database queries and API endpoints
**Rationale**: To ensure users can only access their own data, all queries will be filtered by the authenticated user's ID extracted from the JWT token.
**Implementation**:
- Backend: All CRUD operations will include user ID filter
- Database: Foreign key relationships will enforce user ownership
- API: Endpoints will validate that requested resources belong to authenticated user

## Architecture Patterns

### Monorepo Structure
**Decision**: Separate backend and frontend directories in a single repository
**Rationale**: This satisfies the monorepo constraint while maintaining clear separation between services. It allows for coordinated deployment while keeping services independently deployable.
**Benefits**:
- Shared configuration and tooling
- Coordinated versioning
- Clear boundaries between services
- Independent scaling capabilities

### Deployment Strategy
**Decision**: Separate deployments for frontend and backend services
**Rationale**: Maintains service independence while allowing different scaling and update strategies for each service.
**Implementation**:
- Backend: Deployed to Python-compatible platform (e.g., Render, Railway)
- Frontend: Deployed to Next.js-compatible platform (e.g., Vercel, Netlify)
- Database: Neon PostgreSQL (managed service)