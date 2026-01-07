# Omni2 Admin Dashboard - Backend

FastAPI-based backend for the Omni2 Admin Dashboard.

## Features

- 🔐 JWT-based authentication
- 👥 User management (CRUD)
- 🔌 MCP management (CRUD)
- ⚙️ Configuration management (YAML ↔ DB sync)
- 📊 Analytics and cost visualization
- 📜 Audit log viewing
- 🔴 Real-time updates via WebSocket
- 🗄️ PostgreSQL database (shared with Omni2)

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: PyJWT
- **Validation**: Pydantic 2.0
- **WebSocket**: FastAPI WebSocket
- **Testing**: pytest

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16
- uv (Astral package manager) or pip

### Installation

```bash
# Install dependencies
uv pip install -r requirements.txt
# or
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Seed admin user
python scripts/seed_admin.py

# Start server
uvicorn app.main:app --reload --port 8500
```

### Access

- API: http://localhost:8500
- Docs: http://localhost:8500/docs
- ReDoc: http://localhost:8500/redoc

### Default Admin Credentials

After running `seed_admin.py`:
- Email: admin@omni2.local
- Password: admin123 (change immediately!)

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Settings (from .env)
│   ├── database.py       # DB connection & session
│   ├── dependencies.py   # Dependency injection
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── dashboard.py  # Dashboard stats
│   │   │   ├── mcps.py       # MCP management
│   │   │   ├── users.py      # User management
│   │   │   ├── config.py     # Config management
│   │   │   ├── analytics.py  # Analytics
│   │   │   └── audit.py      # Audit logs
│   │   └── websocket.py      # WebSocket handler
│   │
│   ├── models/           # SQLAlchemy models
│   │   ├── admin_user.py
│   │   ├── admin_session.py
│   │   ├── config_snapshot.py
│   │   └── ...
│   │
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py
│   │   ├── mcp.py
│   │   ├── user.py
│   │   └── ...
│   │
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── mcp_service.py
│   │   ├── config_service.py
│   │   └── analytics_service.py
│   │
│   ├── utils/
│   │   ├── security.py   # Password hashing, JWT
│   │   ├── logger.py     # Structured logging
│   │   └── validators.py
│   │
│   └── middleware/
│       ├── auth.py       # JWT validation
│       ├── rate_limit.py # Rate limiting
│       └── logging.py    # Request logging
│
├── scripts/
│   └── seed_admin.py     # Seed initial admin user
│
├── tests/
│   ├── test_api/
│   └── test_services/
│
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

### Authentication

```
POST   /api/v1/auth/login    # Login
POST   /api/v1/auth/logout   # Logout
POST   /api/v1/auth/refresh  # Refresh token
GET    /api/v1/auth/me       # Get current user
```

### Dashboard

```
GET    /api/v1/dashboard/stats     # Hero stats
GET    /api/v1/dashboard/activity  # Activity feed
GET    /api/v1/dashboard/charts    # Chart data
```

### MCP Management

```
GET    /api/v1/mcps          # List all MCPs
GET    /api/v1/mcps/{id}     # Get MCP details
POST   /api/v1/mcps          # Create MCP
PUT    /api/v1/mcps/{id}     # Update MCP
DELETE /api/v1/mcps/{id}     # Delete MCP
POST   /api/v1/mcps/{id}/health  # Trigger health check
```

### User Management

```
GET    /api/v1/users         # List all users
GET    /api/v1/users/{id}    # Get user details
POST   /api/v1/users         # Create user
PUT    /api/v1/users/{id}    # Update user
DELETE /api/v1/users/{id}    # Delete user
```

### Configuration

```
GET    /api/v1/config/source     # Get current source (yaml/db)
POST   /api/v1/config/import     # Import YAML → DB
POST   /api/v1/config/export     # Export DB → YAML
GET    /api/v1/config/diff       # Compare YAML vs DB
```

### Analytics

```
GET    /api/v1/analytics/overview     # Overall analytics
GET    /api/v1/analytics/cost         # Cost breakdown
GET    /api/v1/analytics/performance  # Performance metrics
```

### WebSocket

```
WS     /ws                   # WebSocket connection
```

## Environment Variables

See [.env.example](.env.example) for all available options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `JWT_EXPIRY_MINUTES`: Token expiry time (default: 15)
- `OMNI2_API_URL`: Omni2 API URL (for health checks)
- `CORS_ORIGINS`: Allowed CORS origins

## Development

### Run with auto-reload

```bash
uvicorn app.main:app --reload --port 8500
```

### Run tests

```bash
pytest
```

### Create new migration

```bash
alembic revision --autogenerate -m "Add new table"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## Docker

```bash
# Build
docker build -t omni2-admin-api .

# Run
docker run -p 8500:8000 \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET=your-secret \
  omni2-admin-api
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_auth.py

# Run specific test
pytest tests/test_api/test_auth.py::test_login_success
```

## Deployment

See [ROADMAP.md](../ROADMAP.md) Phase 10 for deployment instructions.

## Contributing

1. Create feature branch from `main`
2. Follow code style (black, isort, pylint)
3. Write tests (>80% coverage)
4. Update documentation
5. Submit PR

## License

Internal project - Shift4

---

**Status**: 🏗️ In Development  
**Version**: 0.1.0  
**Last Updated**: January 6, 2026
