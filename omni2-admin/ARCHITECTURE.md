# Omni2 Admin Dashboard - Architecture Specification

**Version**: 1.0  
**Date**: January 6, 2026  
**Status**: 🏗️ Architecture Phase

---

## 🏛️ System Architecture

### High-Level Overview

```
┌─────────────┐          ┌──────────────────┐          ┌─────────────┐
│   Browser   │◄────────►│  Admin Dashboard │◄────────►│   Omni2     │
│  (Next.js)  │ HTTPS    │    (FastAPI)     │  HTTP    │   Bridge    │
│             │ WS       │                  │          │             │
└─────────────┘          └──────────────────┘          └─────────────┘
                                   │                           │
                                   └───────────┬───────────────┘
                                               │
                                               ▼
                                     ┌──────────────────┐
                                     │   PostgreSQL     │
                                     │ (Shared Omni2 DB)│
                                     │  - Omni2 tables  │
                                     │  - Admin tables  │
                                     │  - Audit logs    │
                                     └──────────────────┘
```

**Key Architecture Decision**: Admin Dashboard and Omni2 **share the same PostgreSQL database**
- Omni2 tables: `users`, `audit_logs`, `mcp_servers`, `mcp_tools`
- Admin tables: `admin_users`, `admin_sessions`, `config_snapshots`, etc.
- Real-time sync via PostgreSQL LISTEN/NOTIFY
- Single source of truth for all data

### Technology Stack

**Frontend**
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **UI Library**: React 18
- **Styling**: Tailwind CSS 3.4
- **Components**: shadcn/ui (Radix UI primitives)
- **Charts**: Recharts 2.x
- **State Management**: Zustand (lightweight)
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation
- **WebSocket**: socket.io-client
- **Icons**: Lucide React

**Backend**
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12+
- **Database ORM**: SQLAlchemy 2.0 (async)
- **Database Driver**: asyncpg (PostgreSQL)
- **Authentication**: JWT (PyJWT)
- **WebSocket**: FastAPI WebSocket + python-socketio
- **Validation**: Pydantic 2.0
- **HTTP Client**: httpx (async)
- **Logging**: structlog
- **Testing**: pytest + httpx

**Database**
- **Primary**: PostgreSQL 16
- **Connection Pool**: asyncpg pool (5-20 connections)
- **Migrations**: Alembic
- **Schema**: Extends Omni2 schema with admin-specific tables

**Infrastructure**
- **Containers**: Docker + Docker Compose
- **Database**: PostgreSQL 16 (shared with Omni2 - `omni2-postgres` container)
- **Network**: Uses existing `omni2-network` from Omni2 stack
- **Environment**: .env files
- **Package Manager (FE)**: pnpm
- **Package Manager (BE)**: uv (Astral)

---

## 🗄️ Database Schema

### New Admin Tables

```sql
-- Admin users (separate from Omni2 users)
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL, -- 'admin' or 'viewer'
    
    is_active BOOLEAN DEFAULT true,
    is_super_admin BOOLEAN DEFAULT false,
    
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    preferences JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES admin_users(id),
    
    INDEX idx_admin_users_email (email),
    INDEX idx_admin_users_role (role),
    INDEX idx_admin_users_active (is_active)
);

-- Admin sessions
CREATE TABLE admin_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    ip_address INET,
    user_agent TEXT,
    
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_admin_sessions_user (admin_user_id),
    INDEX idx_admin_sessions_token (token_hash),
    INDEX idx_admin_sessions_expires (expires_at)
);

-- Configuration snapshots (YAML ↔ DB sync)
CREATE TABLE config_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_type VARCHAR(50) NOT NULL, -- 'mcps', 'users', 'global'
    
    source VARCHAR(50) NOT NULL, -- 'yaml_import', 'db_export', 'manual_edit'
    config_data JSONB NOT NULL,
    
    created_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- For rollback
    previous_snapshot_id INTEGER REFERENCES config_snapshots(id),
    
    INDEX idx_config_snapshots_type (snapshot_type),
    INDEX idx_config_snapshots_created (created_at DESC)
);

-- MCP health check history
CREATE TABLE mcp_health_history (
    id BIGSERIAL PRIMARY KEY,
    mcp_server_id INTEGER NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
    
    is_healthy BOOLEAN NOT NULL,
    response_time_ms INTEGER,
    tools_count INTEGER,
    
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_mcp_health_mcp (mcp_server_id),
    INDEX idx_mcp_health_checked (checked_at DESC),
    INDEX idx_mcp_health_status (is_healthy)
);

-- Admin activity audit (separate from Omni2 audit_logs)
CREATE TABLE admin_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES admin_users(id),
    
    action VARCHAR(100) NOT NULL, -- 'mcp.create', 'user.edit', 'config.import'
    resource_type VARCHAR(50), -- 'mcp', 'user', 'config'
    resource_id INTEGER,
    
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_admin_audit_user (admin_user_id),
    INDEX idx_admin_audit_action (action),
    INDEX idx_admin_audit_created (created_at DESC)
);

-- Dashboard widgets/preferences
CREATE TABLE dashboard_widgets (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    
    widget_type VARCHAR(50) NOT NULL, -- 'stats', 'chart', 'activity_feed'
    position INTEGER NOT NULL,
    size VARCHAR(20), -- 'small', 'medium', 'large', 'full'
    
    config JSONB DEFAULT '{}',
    is_visible BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_dashboard_widgets_user (admin_user_id)
);

-- Alert rules (for future phase)
CREATE TABLE alert_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    rule_type VARCHAR(50) NOT NULL, -- 'cost_threshold', 'error_rate', 'mcp_down'
    conditions JSONB NOT NULL,
    
    notification_channels JSONB, -- ['email', 'slack']
    notification_recipients JSONB,
    
    is_enabled BOOLEAN DEFAULT true,
    
    last_triggered TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    
    created_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_alert_rules_enabled (is_enabled),
    INDEX idx_alert_rules_type (rule_type)
);
```

### Views for Analytics

```sql
-- Real-time dashboard stats
CREATE VIEW v_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM mcp_servers WHERE is_enabled = true) as active_mcps,
    (SELECT COUNT(*) FROM mcp_servers WHERE is_healthy = false) as unhealthy_mcps,
    (SELECT COUNT(*) FROM users WHERE is_active = true) as active_users,
    (SELECT COUNT(*) FROM audit_logs WHERE created_at >= NOW() - INTERVAL '1 hour') as queries_last_hour,
    (SELECT COALESCE(SUM(cost_estimate), 0) FROM audit_logs WHERE created_at >= CURRENT_DATE) as cost_today,
    (SELECT ROUND(AVG(duration_ms)) FROM audit_logs WHERE created_at >= NOW() - INTERVAL '1 hour') as avg_duration_ms,
    (SELECT COUNT(*) FILTER (WHERE success = false) * 100.0 / NULLIF(COUNT(*), 0) 
     FROM audit_logs WHERE created_at >= NOW() - INTERVAL '1 hour') as error_rate_pct;

-- MCP performance summary
CREATE VIEW v_mcp_performance AS
SELECT 
    ms.id,
    ms.name,
    ms.is_healthy,
    ms.is_enabled,
    COUNT(DISTINCT al.id) as total_calls,
    COUNT(DISTINCT al.id) FILTER (WHERE al.success = false) as failed_calls,
    ROUND(AVG(al.duration_ms)) as avg_duration_ms,
    COALESCE(SUM(al.cost_estimate), 0) as total_cost,
    MAX(al.created_at) as last_used_at
FROM mcp_servers ms
LEFT JOIN audit_logs al ON al.mcp_target = ms.name
WHERE al.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY ms.id, ms.name, ms.is_healthy, ms.is_enabled;

-- Cost breakdown by MCP
CREATE VIEW v_cost_by_mcp AS
SELECT 
    mcp_target as mcp_name,
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as request_count,
    SUM(tokens_input) as total_tokens_input,
    SUM(tokens_output) as total_tokens_output,
    SUM(tokens_cached) as total_tokens_cached,
    SUM(cost_estimate) as total_cost
FROM audit_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY mcp_target, DATE_TRUNC('day', created_at);
```

---

## 🔌 API Architecture

### Backend API Structure

```
api/
├── v1/
│   ├── auth.py          # Login, logout, refresh token
│   ├── dashboard.py     # Dashboard stats and widgets
│   ├── mcps.py          # MCP management (CRUD)
│   ├── users.py         # User management (CRUD)
│   ├── config.py        # Config import/export, YAML ↔ DB
│   ├── analytics.py     # Analytics queries
│   ├── audit.py         # Audit log viewing
│   └── health.py        # Health checks
└── websocket.py         # WebSocket connections
```

### REST API Endpoints

**Authentication**
```
POST   /api/v1/auth/login          # Login with email/password
POST   /api/v1/auth/logout         # Logout (invalidate session)
POST   /api/v1/auth/refresh        # Refresh JWT token
GET    /api/v1/auth/me             # Get current user info
```

**Dashboard**
```
GET    /api/v1/dashboard/stats     # Hero stats (MCPs, queries, cost, uptime)
GET    /api/v1/dashboard/activity  # Recent activity feed (last 50)
GET    /api/v1/dashboard/charts    # Chart data (queries/time, cost/mcp)
GET    /api/v1/dashboard/alerts    # Active alerts
```

**MCP Management**
```
GET    /api/v1/mcps                # List all MCPs
GET    /api/v1/mcps/{id}           # Get MCP details
POST   /api/v1/mcps                # Create new MCP
PUT    /api/v1/mcps/{id}           # Update MCP config
DELETE /api/v1/mcps/{id}           # Delete MCP
POST   /api/v1/mcps/{id}/health    # Trigger health check
GET    /api/v1/mcps/{id}/tools     # List MCP tools
GET    /api/v1/mcps/{id}/analytics # MCP-specific analytics
POST   /api/v1/mcps/{id}/enable    # Enable MCP
POST   /api/v1/mcps/{id}/disable   # Disable MCP
```

**User Management**
```
GET    /api/v1/users               # List all Omni2 users
GET    /api/v1/users/{id}          # Get user details
POST   /api/v1/users               # Create new user
PUT    /api/v1/users/{id}          # Update user
DELETE /api/v1/users/{id}          # Delete user
GET    /api/v1/users/{id}/activity # User activity logs
PUT    /api/v1/users/{id}/permissions # Update user permissions
POST   /api/v1/users/{id}/enable   # Enable user
POST   /api/v1/users/{id}/disable  # Disable user
```

**Configuration Management**
```
GET    /api/v1/config/source       # Get current source (yaml/db)
POST   /api/v1/config/import       # Import YAML → DB
POST   /api/v1/config/export       # Export DB → YAML
GET    /api/v1/config/diff         # Compare YAML vs DB
GET    /api/v1/config/snapshots    # List config snapshots
POST   /api/v1/config/rollback     # Rollback to snapshot
GET    /api/v1/config/mcps         # Get MCPs config
PUT    /api/v1/config/mcps         # Update MCPs config
GET    /api/v1/config/users        # Get users config
PUT    /api/v1/config/users        # Update users config
```

**Analytics**
```
GET    /api/v1/analytics/overview      # Overall analytics
GET    /api/v1/analytics/cost          # Cost breakdown
GET    /api/v1/analytics/performance   # Performance metrics
GET    /api/v1/analytics/errors        # Error summary
GET    /api/v1/analytics/users         # User activity
GET    /api/v1/analytics/tools         # Tool popularity
GET    /api/v1/analytics/trends        # Trends over time
POST   /api/v1/analytics/export        # Export to CSV
```

**Audit Logs**
```
GET    /api/v1/audit/logs          # Query audit logs
GET    /api/v1/audit/logs/{id}     # Get log details
GET    /api/v1/audit/stats         # Audit statistics
POST   /api/v1/audit/search        # Advanced search
```

**Health & Monitoring**
```
GET    /api/v1/health              # API health check
GET    /api/v1/health/db           # Database health
GET    /api/v1/health/omni2        # Omni2 connection health
GET    /api/v1/version             # API version info
```

### WebSocket Events

**Client → Server**
```javascript
// Subscribe to updates
socket.emit('subscribe', { channel: 'dashboard' })
socket.emit('subscribe', { channel: 'mcp:database_mcp' })
socket.emit('subscribe', { channel: 'audit_logs' })

// Unsubscribe
socket.emit('unsubscribe', { channel: 'dashboard' })
```

**Server → Client**
```javascript
// Dashboard updates
socket.on('dashboard:stats', (data) => {
  // { active_mcps: 12, queries_last_hour: 2847, ... }
})

// New activity
socket.on('activity:new', (event) => {
  // { user: 'John', mcp: 'database_mcp', tool: 'analyze_query', ... }
})

// MCP status change
socket.on('mcp:status_change', (data) => {
  // { mcp_id: 5, name: 'database_mcp', status: 'unhealthy', ... }
})

// Cost alert
socket.on('alert:cost', (data) => {
  // { threshold: 100, current: 125, period: 'today' }
})

// Audit log entry
socket.on('audit:new', (log) => {
  // { user: 'John', action: 'mcp.edit', ... }
})
```

---

## 🔐 Security Architecture

### Authentication Flow

```
1. User submits email + password
2. Backend validates credentials
3. Generate JWT token (15 min expiry)
4. Generate refresh token (7 days expiry)
5. Store session in admin_sessions table
6. Return tokens to client
7. Client stores tokens (httpOnly cookies or localStorage)
8. Client includes JWT in Authorization header for API calls
9. Backend validates JWT on each request
10. Token refresh before expiry using refresh token
```

### Authorization

**Roles**:
- `admin` - Full access to all features
- `viewer` - Read-only access (no create/update/delete)

**Permission Check**:
```python
@require_role("admin")
async def create_mcp(request: Request, mcp_data: MCPCreate):
    # Only admins can create MCPs
    pass

@require_authenticated
async def get_dashboard(request: Request):
    # Any authenticated user can view dashboard
    pass
```

### Security Headers

```python
# CORS
origins = ["http://localhost:3000", "https://admin.omni2.local"]

# Security headers
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}
```

### Rate Limiting

```python
# Per user
rate_limits = {
    "admin": "1000/hour",
    "viewer": "500/hour",
}

# Per endpoint
endpoint_limits = {
    "/api/v1/auth/login": "5/minute",  # Prevent brute force
    "/api/v1/analytics/*": "100/minute",
    "/api/v1/mcps/*": "200/minute",
}
```

---

## 📡 Real-Time Communication

### WebSocket Architecture

```
┌──────────┐          ┌──────────────┐          ┌─────────────┐
│ Client 1 │◄────────►│   WebSocket  │◄────────►│  PostgreSQL │
│ (React)  │  WS      │   Server     │          │  (LISTEN/   │
└──────────┘          │  (FastAPI)   │          │   NOTIFY)   │
                      └──────────────┘          └─────────────┘
┌──────────┐                 ▲
│ Client 2 │◄────────────────┘
└──────────┘
```

### PostgreSQL LISTEN/NOTIFY

```sql
-- Trigger on audit_logs insert
CREATE OR REPLACE FUNCTION notify_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('audit_log_new', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_notify
AFTER INSERT ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION notify_audit_log();

-- Similarly for mcp_servers, users, etc.
```

### Backend WebSocket Handler

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to PostgreSQL notifications
    async with db_pool.acquire() as conn:
        await conn.add_listener('audit_log_new', lambda msg: 
            websocket.send_json({'event': 'audit:new', 'data': msg})
        )
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_json()
                # Handle client messages (subscribe/unsubscribe)
            except WebSocketDisconnect:
                break
```

---

## 🔄 Data Flow

### User Action Flow

```
User clicks "Create MCP"
  ↓
Frontend validation (React Hook Form + Zod)
  ↓
POST /api/v1/mcps with JWT token
  ↓
Backend validates JWT & permissions
  ↓
Backend validates request body (Pydantic)
  ↓
Insert into mcp_servers table
  ↓
Log admin action in admin_audit_logs
  ↓
Trigger health check
  ↓
PostgreSQL NOTIFY event
  ↓
WebSocket broadcasts to all connected clients
  ↓
Frontend updates MCP list (React Query cache invalidation)
  ↓
Show success toast
```

### Real-Time Update Flow

```
New Omni2 query executed
  ↓
Insert into audit_logs table
  ↓
PostgreSQL trigger fires → NOTIFY 'audit_log_new'
  ↓
Admin Dashboard backend listens for notification
  ↓
WebSocket server broadcasts to subscribed clients
  ↓
Frontend receives 'activity:new' event
  ↓
Update activity feed (Zustand store)
  ↓
Update dashboard stats (React Query refetch)
  ↓
Animate new item in UI
```

---

## 📦 Project Structure

### Backend (FastAPI)

```
backend/
├── alembic/                  # Database migrations
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Settings (from .env)
│   ├── database.py           # DB connection & session
│   ├── dependencies.py       # Dependency injection
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── mcps.py
│   │   │   ├── users.py
│   │   │   ├── config.py
│   │   │   ├── analytics.py
│   │   │   └── audit.py
│   │   └── websocket.py
│   │
│   ├── models/               # SQLAlchemy models
│   │   ├── admin_user.py
│   │   ├── config_snapshot.py
│   │   └── ...
│   │
│   ├── schemas/              # Pydantic schemas
│   │   ├── auth.py
│   │   ├── mcp.py
│   │   ├── user.py
│   │   └── ...
│   │
│   ├── services/             # Business logic
│   │   ├── auth_service.py
│   │   ├── mcp_service.py
│   │   ├── config_service.py
│   │   ├── analytics_service.py
│   │   └── omni2_client.py  # HTTP client for Omni2
│   │
│   ├── utils/
│   │   ├── security.py       # Password hashing, JWT
│   │   ├── logger.py         # Structured logging
│   │   └── validators.py     # Custom validators
│   │
│   └── middleware/
│       ├── auth.py           # JWT validation
│       ├── rate_limit.py     # Rate limiting
│       └── logging.py        # Request logging
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

### Frontend (Next.js)

```
frontend/
├── app/                      # Next.js 14 App Router
│   ├── (auth)/
│   │   └── login/
│   │       └── page.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx        # Dashboard layout with sidebar
│   │   ├── page.tsx          # Dashboard home
│   │   ├── mcps/
│   │   │   ├── page.tsx      # MCP list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx  # MCP detail
│   │   │   └── new/
│   │   │       └── page.tsx  # Create MCP
│   │   ├── users/
│   │   │   ├── page.tsx      # User list
│   │   │   └── [id]/
│   │   │       └── page.tsx  # User detail
│   │   ├── config/
│   │   │   └── page.tsx      # Config management
│   │   ├── analytics/
│   │   │   └── page.tsx      # Analytics
│   │   └── settings/
│   │       └── page.tsx      # Settings
│   │
│   ├── api/                  # API routes (if needed)
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
│
├── components/
│   ├── ui/                   # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   │
│   ├── dashboard/
│   │   ├── stats-cards.tsx
│   │   ├── activity-feed.tsx
│   │   └── charts.tsx
│   │
│   ├── mcps/
│   │   ├── mcp-card.tsx
│   │   ├── mcp-list.tsx
│   │   └── mcp-form.tsx
│   │
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── footer.tsx
│   │
│   └── shared/
│       ├── loading.tsx
│       ├── error.tsx
│       └── toast.tsx
│
├── lib/
│   ├── api.ts                # API client (axios/fetch)
│   ├── websocket.ts          # WebSocket client
│   ├── auth.ts               # Auth utilities
│   ├── utils.ts              # Utility functions
│   └── constants.ts          # Constants
│
├── hooks/
│   ├── use-auth.ts
│   ├── use-websocket.ts
│   ├── use-mcps.ts
│   └── use-analytics.ts
│
├── stores/
│   ├── auth-store.ts         # Zustand auth store
│   ├── ui-store.ts           # UI state (theme, sidebar)
│   └── activity-store.ts     # Activity feed store
│
├── types/
│   ├── api.ts                # API types
│   ├── models.ts             # Data models
│   └── index.ts
│
├── public/
│   └── assets/
│
├── .env.local
├── Dockerfile
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## 🐳 Docker Architecture

### Docker Compose Structure

```yaml
version: '3.8'

services:
  # Admin Dashboard Backend
  admin-api:
    build: ./backend
    ports:
      - "8500:8000"
    environment:
      # Connect to existing Omni2 PostgreSQL
      - DATABASE_URL=postgresql://postgres:postgres@omni2-postgres:5432/omni
      - OMNI2_API_URL=http://omni2-bridge:8000
      - JWT_SECRET=...
    networks:
      - omni2-network  # Use existing network from Omni2 stack

  # Admin Dashboard Frontend
  admin-web:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8500
    networks:
      - omni2-network

# Use existing omni2-network and omni2-postgres from Omni2 stack
# No need to create separate PostgreSQL container
networks:
  omni2-network:
    external: true
    name: omni2_omni2-network
```

**Important**: Start Omni2 stack first to create the `omni2-postgres` container and `omni2-network`.

---

## 🔄 Integration with Omni2

### Communication Patterns

**1. Database Access (Direct - Shared Database)**
- Admin Dashboard and Omni2 use **same PostgreSQL instance** (`omni2-postgres`)
- Shares tables: `users`, `audit_logs`, `mcp_servers`, `mcp_tools`
- Admin-specific tables: `admin_users`, `admin_sessions`, `config_snapshots`
- Both applications see changes immediately (same database)

**2. API Communication (HTTP - Optional)**
- Admin can call Omni2 API for MCP health checks → `http://omni2-bridge:8000/api/health/{mcp_id}`
- Both services on same Docker network (`omni2-network`)

**3. Real-Time Sync (PostgreSQL LISTEN/NOTIFY)**
- Omni2 logs query → `audit_logs` insert → Admin Dashboard receives notification
- Admin updates config → `config_snapshots` insert → Omni2 can hot-reload
- Single database makes LISTEN/NOTIFY simple and reliable

---

## 🚀 Deployment Strategy

### Development
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Frontend with hot reload
cd frontend && pnpm dev

# Backend with auto-reload
cd backend && uvicorn app.main:app --reload
```

### Production
```bash
# Build optimized images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Or use Kubernetes/Docker Swarm for scale
```

---

## 📊 Performance Considerations

**Backend**:
- Connection pooling (5-20 connections)
- Query optimization with indexes
- Caching (Redis for future phase)
- Async I/O throughout
- Batch operations where possible

**Frontend**:
- Code splitting (Next.js automatic)
- Image optimization (Next.js Image)
- Lazy loading components
- React Query caching
- WebSocket connection management
- Debounced searches
- Virtual scrolling for large lists

**Database**:
- Indexes on frequently queried columns
- Partitioning for audit_logs (by month)
- Archive old data (>90 days)
- Periodic VACUUM/ANALYZE

---

**Status**: Architecture Defined ✅  
**Next**: Implementation
