# Omni2 Admin Dashboard

Modern, responsive admin dashboard for Omni2 MCP Hub with real-time updates and "wow factor" UI/UX.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Version](https://img.shields.io/badge/version-0.1.0-blue)

---

## 🎯 Overview

Omni2 Admin Dashboard is a standalone web application that provides a beautiful, intuitive interface for managing the Omni2 MCP Hub. It features real-time monitoring, comprehensive analytics, and powerful management tools for MCPs, users, and configurations.

### Key Features

- 🔐 **Secure Authentication**: JWT-based auth with role-based access control
- 📊 **Real-Time Dashboard**: Live stats, activity feed, and health monitoring
- 🔌 **MCP Management**: Full CRUD operations for Model Context Protocol servers
- 👥 **User Management**: Manage Omni2 users and permissions
- ⚙️ **Config Management**: Bidirectional YAML ↔ PostgreSQL sync
- 📈 **Analytics**: Rich data visualization with cost tracking
- 🔴 **Live Updates**: WebSocket-powered real-time notifications
- 🎨 **Beautiful UI**: Dark/light themes, glassmorphism, smooth animations
- 📱 **Responsive**: Works perfectly on mobile, tablet, and desktop
- ♿ **Accessible**: WCAG 2.1 AA compliant

---

## 📚 Documentation

- [DESIGN.md](./DESIGN.md) - Visual design and UX specifications
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical architecture and database schema
- [ROADMAP.md](./ROADMAP.md) - Development roadmap and progress tracking
- [ENHANCEMENTS.md](./ENHANCEMENTS.md) - Future enhancement proposals
- [backend/README.md](./backend/README.md) - Backend documentation
- [frontend/README.md](./frontend/README.md) - Frontend documentation (coming soon)

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Omni2 stack running** (provides PostgreSQL database)
- **Python 3.12+** (for backend development)
- **Node.js 18+** (for frontend development)

### Option 1: Docker Compose (Recommended)

**Important**: The admin dashboard uses the existing Omni2 PostgreSQL database. Start Omni2 stack first!

```bash
# 1. Start Omni2 stack (if not already running)
cd ../omni2
docker-compose up -d

# 2. Start admin dashboard
cd ../omni2-admin

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit .env files if needed (defaults should work)

# Start admin dashboard (connects to existing omni2-postgres)
docker-compose up --build

# In another terminal, seed admin user
docker-compose exec admin-api python scripts/seed_admin.py
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8500
- **API Docs**: http://localhost:8500/docs

### Option 2: Manual Setup

**Prerequisites**: Omni2 PostgreSQL must be running (port 5433 on host)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# DATABASE_URL is already set to connect to Omni2 PostgreSQL (localhost:5433)

# Run migrations
alembic upgrade head

# Seed admin user
python scripts/seed_admin.py

# Start server
uvicorn app.main:app --reload --port 8500
```

#### Frontend

```bash
cd frontend

# Install dependencies
pnpm install  # or npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local

# Start dev server
pnpm dev  # or npm run dev
```

### Default Login

After seeding:
- **Email**: admin@omni2.local
- **Password**: admin123

⚠️ **Change this password immediately after first login!**

---

## 🏗️ Project Structure

```
omni2-admin/
├── DESIGN.md                # Visual design specification
├── ARCHITECTURE.md          # Technical architecture
├── ROADMAP.md              # Development roadmap
├── ENHANCEMENTS.md         # Enhancement proposals
├── docker-compose.yml      # Docker orchestration
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── utils/         # Utilities
│   │   └── middleware/    # Middleware
│   ├── alembic/           # Database migrations
│   ├── scripts/           # Utility scripts
│   ├── tests/             # Tests
│   └── requirements.txt
│
└── frontend/              # Next.js frontend (coming soon)
    ├── app/               # Next.js 14 App Router
    ├── components/        # React components
    ├── lib/               # Utilities
    ├── hooks/             # Custom hooks
    ├── stores/            # State management
    └── public/            # Static assets
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12+
- **Database**: PostgreSQL 16 + asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: PyJWT
- **Validation**: Pydantic 2.0

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.4
- **Components**: shadcn/ui (Radix UI)
- **Charts**: Recharts 2.x
- **State**: Zustand
- **Data Fetching**: TanStack Query
- **Forms**: React Hook Form + Zod

### Infrastructure
- **Containers**: Docker + Docker Compose
- **Database**: PostgreSQL 16
- **WebSocket**: FastAPI WebSocket + Socket.IO

---

## 📊 Current Progress

**Overall**: 15% complete (Phase 1 in progress)

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Foundation | 🏗️ In Progress | 40% |
| Phase 2: Auth | ⏳ Not Started | 0% |
| Phase 3: Dashboard | ⏳ Not Started | 0% |
| Phase 4: MCP Management | ⏳ Not Started | 0% |
| Phase 5: User Management | ⏳ Not Started | 0% |
| Phase 6: Config Management | ⏳ Not Started | 0% |
| Phase 7: Analytics | ⏳ Not Started | 0% |
| Phase 8: Real-Time | ⏳ Not Started | 0% |
| Phase 9: Polish | ⏳ Not Started | 0% |
| Phase 10: Deploy | ⏳ Not Started | 0% |

See [ROADMAP.md](./ROADMAP.md) for detailed progress tracking.

---

## 🎨 Design Philosophy

### Visual Design
- **Primary Theme**: Dark mode with deep purples and blues
- **Typography**: Inter font family for modern, clean look
- **Spacing**: Consistent 8px grid system
- **Effects**: Glassmorphism, subtle shadows, smooth animations
- **Colors**: High contrast for accessibility

### UX Principles
- **Speed**: <1 second page loads, instant feedback
- **Clarity**: Clear hierarchy, intuitive navigation
- **Responsiveness**: Mobile-first, works on all devices
- **Accessibility**: Keyboard navigation, ARIA labels, WCAG 2.1 AA
- **Delight**: Smooth animations, micro-interactions, wow factor

---

## 🔐 Security

- **Authentication**: JWT tokens with 15-minute expiry
- **Authorization**: Role-based access control (admin/viewer)
- **Password Hashing**: bcrypt with strong defaults
- **Rate Limiting**: Prevents brute force attacks
- **CORS**: Configured for specific origins
- **SQL Injection**: Protection via SQLAlchemy ORM
- **XSS**: Protection via React and CSP headers

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest
pytest --cov=app --cov-report=html

# Frontend tests (coming soon)
cd frontend
pnpm test
pnpm test:coverage
```

---

## 📈 Performance Goals

- API response time: <100ms (p95)
- Page load time: <1 second
- Real-time latency: <100ms
- Lighthouse score: >90
- Bundle size: <500KB (gzipped)

---

## 🤝 Contributing

1. Create feature branch from `main`
2. Follow code style (black, prettier, eslint)
3. Write tests (>80% coverage)
4. Update documentation
5. Submit PR with detailed description

---

## 📄 License

Internal project - Shift4 Corporation

---

## 👥 Team

**Developer**: Engineering Team  
**Project Start**: January 6, 2026  
**Timeline**: 4-6 weeks

---

## 📞 Support

- **Issues**: Use GitHub Issues
- **Questions**: Ask in Slack #omni2-admin
- **Docs**: See docs/ folder

---

## 🗺️ Roadmap Highlights

**Phase 1 (Week 1)**: Foundation + Documentation ✅ 40%  
**Phase 2 (Week 2)**: Authentication & Authorization  
**Phase 3 (Week 2-3)**: Dashboard Core  
**Phase 4 (Week 3)**: MCP Management  
**Phase 5 (Week 4)**: User Management  
**Phase 6 (Week 4)**: Configuration Management  
**Phase 7 (Week 5)**: Analytics  
**Phase 8 (Week 5-6)**: Real-Time Updates  
**Phase 9 (Week 6)**: Polish & Enhancement  
**Phase 10 (Week 6)**: Documentation & Deployment  

See [ROADMAP.md](./ROADMAP.md) for full details.

---

**Last Updated**: January 6, 2026  
**Status**: 🏗️ Active Development  
**Version**: 0.1.0
