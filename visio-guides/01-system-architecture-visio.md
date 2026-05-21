# Visio: System Architecture Diagram

## Canvas Size: 1400px × 900px

## LAYER STRUCTURE

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1 (Y: 80px)     - CLIENT LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 2 (Y: 200px)    - API GATEWAY LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 3 (Y: 320px)    - SERVICES LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 4 (Y: 470px)    - QUEUE & PROCESSING LAYER               │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 5 (Y: 620px)    - STORAGE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 6 (Y: 750px)    - EXTERNAL SERVICES LAYER                │
└─────────────────────────────────────────────────────────────────┘
```

## COMPONENTS & POSITIONING

### LAYER 1: CLIENT LAYER (Y: 80px)
| Component | X Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| React/TypeScript Vite SPA | 150 | Rectangle | 280×60 | Browser Container |
| Pages | 500 | Rectangle | 280×60 | Login, Dashboard, Builder, AI Chat, Products, Scraping |
| Hooks | 850 | Rectangle | 280×60 | useAIBuild, useAIChat |

### LAYER 2: API GATEWAY (Y: 200px)
| Component | X Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| FastAPI Server | 400 | Rectangle | 300×60 | Port 8000 |
| Auth Router | 100 | Oval | 80×60 | Auth |
| Builder Router | 200 | Oval | 80×60 | Builder |
| Chat Router | 300 | Oval | 80×60 | Chat |
| Product Router | 400 | Oval | 80×60 | Product |
| Scraping Router | 500 | Oval | 80×60 | Scraping |

### LAYER 3: SERVICES LAYER (Y: 320px)
| Component | X Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| Auth Service | 80 | Rectangle | 120×60 | JWT + Rate Limit |
| Builder Service | 250 | Rectangle | 120×60 | Component Mgmt |
| Database Service | 420 | Rectangle | 120×60 | ORM & Queries |
| Feature Extractor | 590 | Rectangle | 120×60 | ML Pipeline |
| Scoring Engine | 760 | Rectangle | 120×60 | Compatibility |
| Mapper | 930 | Rectangle | 120×60 | Transform Data |

### LAYER 4: QUEUE & PROCESSING (Y: 470px)
| Component | X Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| Redis | 200 | Cylinder | 100×80 | Broker & Cache |
| Celery Worker | 450 | Rectangle | 150×60 | Background Jobs |
| Celery Beat | 750 | Rectangle | 150×60 | Scheduled Tasks |
| AI Tasks | 1000 | Rectangle | 120×60 | LLM Interactions |
| Scraping Tasks | 1100 | Rectangle | 120×60 | Web Crawling |

### LAYER 5: STORAGE (Y: 620px)
| Component | X Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| PostgreSQL | 450 | Cylinder | 120×80 | Main Database |
| Tables | 700 | Rectangle | 280×60 | Users, Builds, Products, Chats, Components |

### LAYER 6: EXTERNAL SERVICES (Y: 750px)
| Component | X Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| Venice AI | 250 | Cloud | 120×60 | LLM API |
| Telemart | 500 | Cloud | 120×60 | Scraper |
| Other Sources | 750 | Cloud | 120×60 | Product Sources |

## CONNECTIONS

### Format: [From Component] → [To Component] | Label | Style

```
CLIENT → API:
  React SPA → FastAPI | HTTP/WS | Solid line, blue
  Pages → React SPA | API Calls | Solid line, blue
  Hooks → Pages | State Mgmt | Solid line, blue

API ROUTING:
  FastAPI → Auth Router | Route | Solid line, black
  FastAPI → Builder Router | Route | Solid line, black
  FastAPI → Chat Router | Route | Solid line, black
  FastAPI → Product Router | Route | Solid line, black
  FastAPI → Scraping Router | Route | Solid line, black

API → SERVICES:
  Auth Router → Auth Service | Connect | Solid line, black
  Builder Router → Builder Service | Connect | Solid line, black
  Chat Router → Builder Service | Connect | Solid line, black
  Product Router → Database Service | Connect | Solid line, black
  Scraping Router → Database Service | Connect | Solid line, black

SERVICES INTERNAL:
  Builder Service → Feature Extractor | Call | Solid line, gray
  Builder Service → Scoring Engine | Call | Solid line, gray
  Builder Service → Mapper | Call | Solid line, gray

SERVICES → STORAGE:
  Database Service → PostgreSQL | Query | Solid line, green
  PostgreSQL → Tables | Contains | Solid line, gray

API → QUEUE:
  FastAPI → Redis | Enqueue | Solid line, orange

QUEUE DISTRIBUTION:
  Redis → Celery Worker | Deliver | Solid line, orange
  Redis → Celery Beat | Deliver | Solid line, orange

WORKERS → TASKS:
  Celery Worker → AI Tasks | Spawn | Solid line, black
  Celery Worker → Scraping Tasks | Spawn | Solid line, black
  Celery Beat → Scraping Tasks | Trigger | Dashed line, orange

TASKS → DATABASE:
  AI Tasks → PostgreSQL | Query/Insert | Solid line, green
  Scraping Tasks → PostgreSQL | Query/Insert | Solid line, green

TASKS → EXTERNAL:
  AI Tasks → Venice AI | API Call | Solid line, purple
  Scraping Tasks → Telemart | Crawl | Solid line, purple
  Scraping Tasks → Other Sources | Crawl | Solid line, purple

CACHE FEEDBACK:
  Celery Worker → Redis | Cache Update | Dashed line, orange
  Redis → FastAPI | Cache Hit | Dashed line, orange
```

## CONNECTION STYLES

- **Solid Blue**: Frontend-Backend communication
- **Solid Black**: Routing and control flow
- **Solid Green**: Database operations
- **Solid Orange**: Queue operations
- **Solid Purple**: External service calls
- **Solid Gray**: Internal service composition
- **Dashed**: Async/Trigger operations

## POSITIONING GUIDELINES

1. Keep components within their layer horizontally distributed
2. Use vertical alignment for data flow
3. Route connections around components
4. Group related services (Feature Extractor, Scoring Engine, Mapper) closely
5. Separate async path (Redis, Celery, Workers) visually
