# Omni2 Admin Dashboard - Design Specification

**Version**: 1.0  
**Date**: January 6, 2026  
**Status**: 🎨 Design Phase

---

## 🎯 Design Philosophy

**Goal**: Create a **stunning, modern, enterprise-grade** admin dashboard that feels **responsive, intuitive, and powerful**.

### Core Principles
1. **Wow Factor** - Visual impact with smooth animations and transitions
2. **Data-Dense** - Maximum information, minimal clutter
3. **Real-Time** - Live updates via WebSocket connections
4. **Responsive** - Perfect on desktop, tablet, and mobile
5. **Professional** - Enterprise-ready aesthetics
6. **Accessible** - WCAG 2.1 AA compliant

---

## 🎨 Visual Design

### Color Palette

**Dark Theme (Primary)**
```
Background:     #0A0E1A (Deep Navy)
Surface:        #151B2E (Card Background)
Surface Light:  #1E2842 (Hover State)
Border:         #2D3856 (Dividers)

Primary:        #3B82F6 (Blue 500) - Actions
Success:        #10B981 (Green 500) - Healthy
Warning:        #F59E0B (Amber 500) - Degraded
Error:          #EF4444 (Red 500) - Down
Info:           #06B6D4 (Cyan 500) - Info

Text Primary:   #F9FAFB (Gray 50)
Text Secondary: #9CA3AF (Gray 400)
Text Tertiary:  #6B7280 (Gray 500)
```

**Light Theme (Secondary)**
```
Background:     #F9FAFB (Gray 50)
Surface:        #FFFFFF (White)
Surface Dark:   #F3F4F6 (Gray 100)
Border:         #E5E7EB (Gray 200)

[Colors remain same as dark theme]

Text Primary:   #111827 (Gray 900)
Text Secondary: #6B7280 (Gray 500)
Text Tertiary:  #9CA3AF (Gray 400)
```

### Typography

**Font Family**: Inter (sans-serif) - Modern, readable  
**Fallback**: system-ui, -apple-system, sans-serif

**Scale**:
- Display: 48px / 3rem (Dashboard titles)
- H1: 32px / 2rem (Page headers)
- H2: 24px / 1.5rem (Section headers)
- H3: 20px / 1.25rem (Card headers)
- Body: 16px / 1rem (Content)
- Small: 14px / 0.875rem (Labels)
- Tiny: 12px / 0.75rem (Captions)

**Weights**:
- Light: 300 (Subtle text)
- Regular: 400 (Body)
- Medium: 500 (Labels)
- Semibold: 600 (Headers)
- Bold: 700 (Emphasis)

### Spacing System

8px base unit:
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

### Border Radius
- sm: 4px (Small elements)
- md: 8px (Cards, buttons)
- lg: 12px (Large cards)
- xl: 16px (Modals)
- full: 9999px (Pills, badges)

---

## 🖼️ Layout Structure

### Dashboard Layout (Desktop)

```
┌─────────────────────────────────────────────────────────────┐
│  🔷 Logo          OMNI2 Admin                    👤 User ⚙️ │ ← Top Bar (64px)
├──────┬──────────────────────────────────────────────────────┤
│      │                                                       │
│  📊  │  ┌────────────────────────────────────────────────┐ │
│  🔌  │  │  Dashboard Overview                             │ │
│  👥  │  │  [Stats Cards] [Charts] [Activity Feed]        │ │
│  ⚙️  │  │                                                │ │
│  📈  │  └────────────────────────────────────────────────┘ │
│  🔒  │                                                       │
│      │  Main Content Area                                  │
│ Nav  │  (Scrollable)                                       │
│ 240px│                                                       │
│      │                                                       │
└──────┴───────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────┐
│ ☰  OMNI2     👤 ⚙️ │ ← Top Bar
├─────────────────────┤
│                     │
│   Content Area      │
│   (Full Width)      │
│                     │
│   [Stack Layout]    │
│                     │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  📊 Dashboard       │ ← Bottom Nav
│  🔌 MCPs            │
│  👥 Users           │
│  📈 Analytics       │
└─────────────────────┘
```

---

## 📱 Pages & Components

### 1. Dashboard (Home)

**Hero Stats Cards** (4 across)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  12 MCPs    │  2,847      │  $142.50    │  98.7%      │
│  Connected  │  Queries/hr │  Daily Cost │  Uptime     │
│  ↑ 2 today  │  ↑ 12%      │  ↓ 5%       │  ✓ Healthy  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```
- Animated count-up on load
- Trend indicators (↑↓) with color coding
- Sparkline mini-charts
- Click to drill down

**Live Activity Feed** (Right sidebar, 30% width)
```
┌──────────────────────────────┐
│  🔴 Live Activity            │
│  ────────────────────────── │
│  ○ John used database_mcp    │ ← Pulse animation
│     analyze_query (2s ago)   │
│  ○ Sarah accessed github_mcp │
│     list_repos (5s ago)      │
│  ○ Cost alert: High usage    │
│     detected (1m ago)        │
└──────────────────────────────┘
```
- Real-time WebSocket updates
- Pulse animation for new items
- Auto-scroll, pin to top option
- Color-coded by event type

**Charts** (2 columns, 50% each)
```
┌────────────────────────┬────────────────────────┐
│  Queries Over Time     │  Cost Breakdown        │
│  [Line Chart]          │  [Donut Chart]         │
│  Last 24 Hours         │  By MCP                │
└────────────────────────┴────────────────────────┘
┌────────────────────────┬────────────────────────┐
│  MCP Health Status     │  Top Active Users      │
│  [Status Grid]         │  [Bar Chart]           │
│  12 Online, 0 Down     │  Last 7 Days           │
└────────────────────────┴────────────────────────┘
```

**Quick Actions** (Bottom)
- "Add New MCP" button (prominent, blue)
- "Trigger Health Check" button
- "Export Analytics" button

---

### 2. MCP Management

**MCP Grid View** (Cards, 3 across)
```
┌─────────────────────────────────────────────────┐
│  🔌 database_mcp               ● Online         │
│  Database Performance Analysis                  │
│  ─────────────────────────────────────────────  │
│  📍 http://oracle_mcp:8300                      │
│  🔧 24 Tools  │  ⏱️ 145ms Avg  │  ✓ Healthy     │
│  📊 1,234 calls today  │  $45.20 cost           │
│                                                  │
│  [View Tools] [Edit Config] [Health Check]      │
└─────────────────────────────────────────────────┘
```

**Features**:
- Status badge (Online/Degraded/Offline) with pulsing dot
- Health check button with loading spinner
- Click card for detailed view
- Drag-to-reorder (priority)

**MCP Detail Modal**
```
┌────────────────────────────────────────────────────┐
│  🔌 database_mcp Details              [×] Close    │
├────────────────────────────────────────────────────┤
│  Tabs: [Overview] [Tools] [Config] [Analytics]    │
│                                                     │
│  Overview:                                         │
│  • Status: ● Online (Last check: 2 min ago)       │
│  • Latency: 145ms avg (99th: 450ms)               │
│  • Success Rate: 98.5% (1,215/1,234 calls)        │
│  • Cost: $45.20 today, $312.40 this week          │
│                                                     │
│  Tools (24):                                       │
│  ┌──────────────────────────────────────┐         │
│  │ ✓ analyze_query        1,012 calls   │         │
│  │ ✓ compare_plans          145 calls   │         │
│  │ ✓ check_oracle_access     77 calls   │         │
│  └──────────────────────────────────────┘         │
│                                                     │
│  [Edit Configuration] [Disable MCP] [Delete]      │
└────────────────────────────────────────────────────┘
```

**Add/Edit MCP Form**
- Step-by-step wizard (3 steps)
- Live validation
- Test connection button
- Tool discovery preview

---

### 3. Users & Permissions

**User Table** (Sortable, Filterable)
```
┌────────────────────────────────────────────────────────────┐
│  Filter: [All Roles ▼] [Search...] [Active Only ☑]  +Add  │
├────────────────────────────────────────────────────────────┤
│  Name              Email              Role      Status      │
│  ─────────────────────────────────────────────────────────│
│  👤 Avi Cohen     avi@shift4.com     admin     ● Active   │
│  👤 John Smith    john@shift4.com    dba       ● Active   │
│  👤 Sarah Lee     sarah@shift4.com   viewer    ○ Inactive │
└────────────────────────────────────────────────────────────┘
```

**User Detail Panel** (Slide-out from right)
```
┌────────────────────────────────┐
│  👤 Avi Cohen        [×] Close │
│  ────────────────────────────  │
│  Email: avi@shift4.com         │
│  Role: admin 🔑                │
│  Slack: @avicohen              │
│  Status: ● Active              │
│                                 │
│  MCP Access (12):              │
│  ✓ database_mcp (all tools)    │
│  ✓ github_mcp (all tools)      │
│  ✓ analytics_mcp (all tools)   │
│                                 │
│  Recent Activity:              │
│  • 47 queries today            │
│  • $12.30 cost today           │
│  • Last active: 5 min ago      │
│                                 │
│  [Edit Permissions] [Disable]  │
└────────────────────────────────┘
```

---

### 4. Configuration Management

**Source of Truth Toggle** (Top of page)
```
┌───────────────────────────────────────────────────┐
│  📋 Configuration Source                          │
│  ○ YAML Files (Legacy)  ● PostgreSQL (Active)    │
│                                                    │
│  [Import YAML → DB] [Export DB → YAML]           │
└───────────────────────────────────────────────────┘
```

**Configuration Editor** (Split view)
```
┌──────────────────┬────────────────────────────────┐
│  MCPs            │  database_mcp Configuration    │
│  • database_mcp  │  ────────────────────────────  │
│  • github_mcp    │  Name: database_mcp            │
│  • analytics_mcp │  URL: http://...               │
│                  │  Enabled: [ON/OFF]             │
│  Users           │  Timeout: [30] seconds         │
│  • Admins (2)    │                                 │
│  • DBAs (3)      │  Tool Policy:                  │
│  • Viewers (5)   │  ○ Allow All                   │
│                  │  ● Allow All Except            │
│  Global          │  ○ Allow Only                  │
│  • Blocked Tools │                                 │
│  • Rate Limits   │  Blocked: [delete_*, drop_*]   │
└──────────────────┴────────────────────────────────┘
```

**Import/Export Wizard**
- Diff view (what will change)
- Backup before import
- Rollback capability
- Validation errors highlighted

---

### 5. Analytics & Cost

**Time Period Selector** (Top)
```
[Last Hour] [Today] [Last 7 Days] [Last 30 Days] [Custom ▼]
```

**Key Metrics Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│  Cost Breakdown (Last 7 Days)                    $1,247.50  │
│  ───────────────────────────────────────────────────────── │
│  [Stacked Area Chart showing Input/Output/Cached tokens]   │
│                                                              │
│  By MCP:                                                    │
│  database_mcp  ████████████████████  68% ($847.50)         │
│  github_mcp    ████████              22% ($274.25)         │
│  analytics_mcp ███                   10% ($125.75)         │
└─────────────────────────────────────────────────────────────┘

┌────────────────────┬────────────────────┬────────────────────┐
│  Top Expensive     │  Slow Queries      │  Most Active Users │
│  Queries           │  (>5s)             │  (7 days)          │
│  [Table]           │  [Table]           │  [Bar Chart]       │
└────────────────────┴────────────────────┴────────────────────┘
```

**Interactive Charts**:
- Hover tooltips with detailed breakdown
- Click to filter
- Zoom/pan on time series
- Export to CSV/PNG

---

### 6. Settings

**Tabs**: [General] [Security] [Notifications] [Integrations]

**General**
- Dashboard refresh rate
- Theme preference (Dark/Light/Auto)
- Date/time format
- Timezone

**Security**
- Session timeout
- 2FA settings (future)
- API key management
- Audit log retention

**Notifications**
- Email alerts for:
  - MCP down
  - Cost threshold exceeded
  - High error rate
  - Unusual activity

**Integrations**
- Slack webhook
- Email SMTP
- Monitoring tools (future)

---

## 🎬 Animations & Interactions

### Micro-interactions

**Loading States**
- Skeleton loaders for cards
- Shimmer effect on data loading
- Progress bars for operations

**Transitions**
- Page transitions: 200ms ease-out slide
- Modal: 150ms fade + scale
- Hover states: 100ms ease
- Charts: 300ms ease-in-out

**Feedback**
- Success toast (green, 3s auto-dismiss)
- Error toast (red, 5s with manual dismiss)
- Confirmation dialogs for destructive actions
- Progress indicators for long operations

### Real-Time Updates

**Live Elements**
- Activity feed: New items fade in from top
- Status badges: Pulse on state change
- Charts: Smooth data point addition
- Counters: Animated count-up

**WebSocket Events**
- New query logged → Activity feed update
- MCP status change → Status badge update
- Cost update → Dashboard stats refresh
- User action → Activity notification

---

## 📐 Responsive Breakpoints

```
Mobile:   < 640px   (1 column, bottom nav)
Tablet:   640-1024px (2 columns, side nav)
Desktop:  1024-1536px (3 columns, full nav)
Wide:     > 1536px  (4 columns, expanded)
```

**Mobile Optimizations**:
- Hamburger menu for navigation
- Stacked cards (1 column)
- Simplified charts
- Swipe gestures
- Bottom sheet modals

---

## ♿ Accessibility

**Requirements**:
- Keyboard navigation (Tab, Enter, Esc)
- ARIA labels for all interactive elements
- Focus indicators (2px outline)
- Screen reader support
- Color contrast ratio ≥ 4.5:1
- No content flashing >3/sec

**Keyboard Shortcuts**:
- `/` - Focus search
- `Ctrl+K` - Command palette
- `Esc` - Close modal/panel
- `?` - Help overlay

---

## 🎨 Component Library

**Using**: shadcn/ui + Tailwind CSS

**Core Components**:
- Button (primary, secondary, ghost, danger)
- Card (elevated, flat, bordered)
- Modal/Dialog
- Drawer (slide-out panel)
- Table (sortable, filterable, paginated)
- Form (inputs, selects, checkboxes, switches)
- Toast (notification system)
- Badge (status, count)
- Avatar (user, system)
- Tabs
- Dropdown Menu
- Tooltip
- Progress (bar, spinner, skeleton)

**Custom Components**:
- StatusBadge (with pulse animation)
- MetricCard (stat display with trend)
- ActivityFeed (real-time list)
- MCPCard (MCP display card)
- ToolsList (expandable tool list)
- ChartWrapper (responsive chart container)
- CommandPalette (quick actions)

---

## 🎯 "Wow Factor" Features

1. **Real-Time Everything** - WebSocket-powered live updates across all pages
2. **Glassmorphism Effects** - Subtle blur backgrounds on modals/panels
3. **Smooth Animations** - 60fps transitions, no jank
4. **Dark Mode** - Beautiful default dark theme with light option
5. **Data Visualization** - Rich, interactive charts with hover details
6. **Command Palette** - Ctrl+K for power users
7. **Activity Feed** - Live pulse animation for events
8. **Health Heatmap** - Visual MCP health status grid
9. **Cost Tracking** - Real-time cost accumulation with projections
10. **Smart Search** - Fuzzy search across all entities
11. **Drag & Drop** - Reorder MCPs, rearrange dashboard
12. **Export Anywhere** - CSV/JSON/PDF export for all data

---

## 🔮 Future Enhancements

**Phase 2**:
- Multi-tenancy support
- Advanced RBAC (per-tool permissions)
- Custom dashboards (user-configured)
- Alert rules engine
- Audit log viewer with playback
- Cost budgets & alerts
- Performance profiling
- A/B testing for MCPs

**Phase 3**:
- Mobile app (React Native)
- MCP marketplace
- Automated health checks
- Predictive analytics
- AI-powered insights
- Integration hub (Datadog, PagerDuty)

---

**Status**: Ready for Implementation 🚀
