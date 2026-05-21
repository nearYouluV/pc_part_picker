# Visio Recreation Guide: PC Builder System Architecture

---

## 1. SYSTEM ARCHITECTURE DIAGRAM

### Layer Structure (Top to Bottom)

```
LAYER 1 (Top):         Client Layer
LAYER 2:               API Gateway Layer
LAYER 3:               Services Layer
LAYER 4:               Queue & Processing Layer
LAYER 5:               Storage Layer
LAYER 6 (Bottom):      External Services Layer
```

### Components List

#### LAYER 1: Client Layer
| Component | Type | Notes |
|-----------|------|-------|
| React/TypeScript Vite SPA | Box | Browser container |
| Pages Container | Box | Login, Dashboard, Builder, AI Chat, Products, Scraping |
| Hooks Container | Box | useAIBuild, useAIChat |

#### LAYER 2: API Gateway
| Component | Type | Notes |
|-----------|------|-------|
| FastAPI Server | Box | Port 8000, main API entry |
| Auth Router | Oval | Route handler |
| Builder Router | Oval | Route handler |
| Chat Router | Oval | Route handler |
| Product Router | Oval | Route handler |
| Scraping Router | Oval | Route handler |

#### LAYER 3: Backend Services
| Component | Type | Notes |
|-----------|------|-------|
| Auth Service | Box | JWT + Rate Limit |
| Builder Service | Box | Component Management |
| Database Service | Box | ORM & Queries |
| Feature Extractor | Box | ML Pipeline |
| Scoring Engine | Box | Compatibility Check |
| Mapper | Box | Data Transformation |

#### LAYER 4: Queue & Processing
| Component | Type | Notes |
|-----------|------|-------|
| Redis | Cylinder | Broker & Cache |
| Celery Worker | Box | Background Jobs |
| Celery Beat | Box | Scheduled Tasks |
| AI Tasks | Box | LLM Interactions |
| Scraping Tasks | Box | Web Crawling |

#### LAYER 5: Storage
| Component | Type | Notes |
|-----------|------|-------|
| PostgreSQL | Cylinder | Main Database |
| Tables | Box | Users, Builds, Products, Chats, Components |

#### LAYER 6: External Services
| Component | Type | Notes |
|-----------|------|-------|
| Venice AI | Cloud/Service | LLM API |
| Telemart | Cloud/Service | Scraper |
| Other Product Sources | Cloud/Service | Additional scrapers |

### Connections List

```
CLIENT LAYER → API GATEWAY:
  Browser → FastAPI Server (HTTP/WS)
  Pages → Browser (API Calls)
  Hooks → Pages (State Management)

API GATEWAY ROUTING:
  FastAPI → Auth Router
  FastAPI → Builder Router
  FastAPI → Chat Router
  FastAPI → Product Router
  FastAPI → Scraping Router

API → SERVICES:
  Auth Router → Auth Service
  Builder Router → Builder Service
  Chat Router → Builder Service
  Product Router → Database Service
  Scraping Router → Database Service

SERVICES COMPOSITION:
  Builder Service → Feature Extractor
  Builder Service → Scoring Engine
  Builder Service → Mapper

SERVICES → STORAGE:
  Database Service → PostgreSQL
  PostgreSQL → Tables

API → QUEUE:
  FastAPI → Redis

QUEUE WORKERS:
  Redis → Celery Worker
  Redis → Celery Beat

WORKERS → TASKS:
  Celery Worker → AI Tasks
  Celery Worker → Scraping Tasks
  Celery Beat → Scraping Tasks (Trigger)

TASKS → DATABASE:
  AI Tasks → PostgreSQL (Query)
  Scraping Tasks → PostgreSQL (Query)

TASKS → EXTERNAL:
  AI Tasks → Venice AI (API Call)
  Scraping Tasks → Telemart (Crawl)
  Scraping Tasks → Other Sources (Crawl)

CACHE:
  Celery Worker → Redis (Update Cache)
  Redis → FastAPI (Query Cache)
```

---

## 2. DATA FLOW DIAGRAM

### Layer Structure (Left to Right)

```
COLUMN 1:    Request Phase
COLUMN 2:    Processing Phase (with decision)
COLUMN 3:    Async Processing Branch
COLUMN 4:    Response Phase
COLUMN 5:    Feedback Loop
```

### Components List

#### COLUMN 1: Request Phase
| Component | Type |
|-----------|------|
| User | Person/Actor |
| Action | Decision/Text |
| HTTP Request | Arrow/Connector |

#### COLUMN 2: Processing Phase
| Component | Type |
|-----------|------|
| Validate & Authenticate | Process Box |
| Auth OK? | Diamond (Decision) |
| Parse Request Data | Process Box |
| Apply Business Logic | Process Box |
| Query Database | Process Box |

#### COLUMN 3: Async Processing
| Component | Type |
|-----------|------|
| Queue Task to Redis | Process Box |
| Background Worker Process | Process Box |
| Call External API/Scraper | Process Box |
| Process Result | Process Box |
| Store in Database | Process Box |

#### COLUMN 4: Response Phase
| Component | Type |
|-----------|------|
| Prepare Response | Process Box |
| Cache in Redis | Process Box |
| Send HTTP Response | Process Box |
| Update Client State | Process Box |

#### COLUMN 5: Feedback Loop
| Component | Type |
|-----------|------|
| WebSocket Notification | Process Box |
| Real-time Updates | Process Box |

### Connections List

```
REQUEST FLOW:
  User → Action
  Action → HTTP Request
  HTTP Request → Validate & Authenticate

PROCESSING FLOW:
  Validate & Authenticate → Auth OK? (Decision)
  Auth OK? → Parse Request Data (Yes path)
  Auth OK? → Send HTTP Response (No path)
  Parse Request Data → Apply Business Logic
  Apply Business Logic → Query Database
  Query Database → Prepare Response

ASYNC BRANCH:
  Apply Business Logic → Queue Task to Redis (Heavy Task)
  Queue Task to Redis → Background Worker Process
  Background Worker Process → Call External API/Scraper
  Call External API/Scraper → Process Result
  Process Result → Store in Database
  Store in Database → Query Database (Update DB)

RESPONSE FLOW:
  Prepare Response → Cache in Redis
  Cache in Redis → Send HTTP Response
  Send HTTP Response → Update Client State

FEEDBACK:
  Background Worker Process → WebSocket Notification (Notify)
  WebSocket Notification → Real-time Updates
  Real-time Updates → Update Client State
```

---

## 3. AI BUILD SEQUENCE DIAGRAM

### Swim Lanes (Vertical Columns)

```
LANE 1:    User
LANE 2:    Frontend
LANE 3:    FastAPI Backend
LANE 4:    PostgreSQL
LANE 5:    Redis Queue
LANE 6:    Celery Worker
LANE 7:    Venice AI API
```

### Message/Action Sequence (Top to Bottom)

| # | From | To | Message | Type |
|---|------|----|---------|------|
| 1 | User | Frontend | Start AI Build with Budget | Action |
| 2 | Frontend | FastAPI | POST /api/builder/ai-build {budget, preferences} | Request |
| 3 | FastAPI | PostgreSQL | Verify User & Get Preferences | Query |
| 4 | PostgreSQL | FastAPI | User Data | Response |
| 5 | FastAPI | FastAPI | Extract Features from Request | Process |
| 6 | FastAPI | Redis | Queue AI Task (task_id: uuid) | Queue |
| 7 | FastAPI | Frontend | Return task_id (HTTP 202) | Response |
| 8 | Frontend | User | Building... Show Progress | UI Update |
| 9 | Redis | Celery Worker | Dequeue Task | Trigger |
| 10 | Celery Worker | Celery Worker | Initialize Build Context | Process |
| 11 | Celery Worker | Venice AI | Request: Recommended Components {budget, preferences} | API Call |
| 12 | Venice AI | Celery Worker | AI Response: Component List | Response |
| 13 | Celery Worker | PostgreSQL | Query Products by Category & Price Range | Query |
| 14 | PostgreSQL | Celery Worker | Product List | Response |
| 15 | Celery Worker | Celery Worker | Rank Components by Score (FeatureExtractor) | Process |
| 16 | Celery Worker | Celery Worker | Check Compatibility (ScoringEngine) | Process |
| 17 | Celery Worker | PostgreSQL | Insert Build with Components | Query |
| 18 | PostgreSQL | Celery Worker | Build ID | Response |
| 19 | Celery Worker | Redis | Store Result (task_id → build_data) | Store |
| 20 | Frontend | FastAPI | Poll /api/tasks/{id} | Request |
| 21 | FastAPI | Redis | Check Task Status | Query |
| 22 | Redis | FastAPI | Result Ready | Response |
| 23 | FastAPI | Frontend | Build Result + Components | Response |
| 24 | Frontend | User | ✅ Build Complete (Show Components & Total Cost) | UI Update |

### Timeline Markers

```
T0:     User initiates action
T1-T4:  Request validation and feature extraction
T5-T8:  Async task queuing and UI feedback
T9-T18: Async processing (parallel background work)
T19-T23: Result polling and delivery
T24:    Final UI update
```

---

## 4. COMPONENT INTERACTION WORKFLOW

### Layer Structure (Top to Bottom)

```
LAYER 1:    User Input
LAYER 2:    Service Layer
LAYER 3:    Processing/Extraction
LAYER 4:    Scoring/Mapping
LAYER 5:    Persistence
LAYER 6:    Queue/Async
LAYER 7:    External Services
```

### Components List

#### LAYER 1: User Input
| Component | Type |
|-----------|------|
| User Initiates Build Request | Actor/Input |

#### LAYER 2: Service Layer
| Component | Type |
|-----------|------|
| BuilderService validates_build | Process Box |

#### LAYER 3: Processing/Extraction
| Component | Type |
|-----------|------|
| FeatureExtractor parse_specs normalize_values | Process Box |

#### LAYER 4: Scoring/Mapping
| Component | Type |
|-----------|------|
| ScoringEngine check_compatibility calculate_score | Process Box |
| Mapper transform_build_data serialize_components | Process Box |

#### LAYER 5: Persistence
| Component | Type |
|-----------|------|
| DatabaseService Create Build Record | Process Box |
| PostgreSQL INSERT Build INSERT BuildComponents | Cylinder |
| Response Handler format_response | Process Box |

#### LAYER 6: Queue/Async
| Component | Type |
|-----------|------|
| Redis Queue ai_tasks.py | Cylinder |
| CeleryWorker ai_build_task | Process Box |
| CeleryBeat Trigger Schedule | Timer/Process |
| ScrapingTasks telemart_scraper | Process Box |

#### LAYER 7: External Services
| Component | Type |
|-----------|------|
| Venice AI LLM Response | Cloud Service |
| Product Data Store | Database |

#### LAYER 8: Output
| Component | Type |
|-----------|------|
| Frontend Update State BuildCard Component | UI Component |
| Build Displayed to User | Output |

### Connections List

```
MAIN FLOW (Synchronous):
  User Initiates → BuilderService (Selected Components)
  BuilderService → FeatureExtractor (Extract Features)
  FeatureExtractor → ScoringEngine (Features Dict)
  ScoringEngine → Mapper (Component Scores)
  Mapper → DatabaseService (Build Data)
  DatabaseService → PostgreSQL (SQL Query)
  PostgreSQL → Response Handler (Result)
  Response Handler → Frontend (JSON Response)
  Frontend → Build Display (Display)
  Build Display → User (✅ Complete)

AI BRANCH (Asynchronous):
  AI Build Request → Redis Queue (Enqueue)
  Redis Queue → CeleryWorker (Worker Pick-up)
  CeleryWorker → Venice AI (API Call)
  Venice AI → BuilderService (Component Recs)

SCHEDULING BRANCH:
  Scheduled Scraping → CeleryBeat (Cron Job Trigger)
  CeleryBeat → Redis Queue (Queue)

SCRAPING BRANCH:
  CeleryWorker → ScrapingTasks (Product Scraping)
  ScrapingTasks → Product Data (Parse HTML)
  Product Data → PostgreSQL (Store)
```

---

## 5. DATABASE SCHEMA (ENTITY-RELATIONSHIP)

### Entity List with Attributes

#### USER Entity
| Attribute | Type | Key |
|-----------|------|-----|
| user_id | INT | PK |
| username | VARCHAR | |
| email | VARCHAR | |
| password_hash | VARCHAR | |
| created_at | TIMESTAMP | |

#### BUILD Entity
| Attribute | Type | Key |
|-----------|------|-----|
| build_id | INT | PK |
| user_id | INT | FK |
| name | VARCHAR | |
| description | TEXT | |
| total_cost | FLOAT | |
| total_power | INT | |
| created_at | TIMESTAMP | |

#### BUILD_COMPONENT Entity
| Attribute | Type | Key |
|-----------|------|-----|
| component_id | INT | PK |
| build_id | INT | FK |
| product_id | INT | FK |
| quantity | INT | |
| source | VARCHAR | |
| added_at | TIMESTAMP | |

#### PRODUCT Entity
| Attribute | Type | Key |
|-----------|------|-----|
| product_id | INT | PK |
| name | VARCHAR | |
| category | VARCHAR | |
| price | FLOAT | |
| source | VARCHAR | |
| specs | TEXT | |
| metadata | TEXT | |
| scraped_at | TIMESTAMP | |

#### PRODUCT SUBTYPES (via category)
| Subtype | Reference |
|---------|-----------|
| CPU | PRODUCT |
| GPU | PRODUCT |
| RAM | PRODUCT |
| STORAGE | PRODUCT |
| PSU | PRODUCT |
| MOTHERBOARD | PRODUCT |
| COOLING | PRODUCT |

#### CHAT Entity
| Attribute | Type | Key |
|-----------|------|-----|
| chat_id | INT | PK |
| user_id | INT | FK |
| build_id | INT | FK |
| created_at | TIMESTAMP | |

#### CHAT_MESSAGE Entity
| Attribute | Type | Key |
|-----------|------|-----|
| message_id | INT | PK |
| chat_id | INT | FK |
| role | VARCHAR | |
| content | TEXT | |
| created_at | TIMESTAMP | |

### Relationships List

```
1. USER → BUILD (One-to-Many)
   USER.user_id (PK) ← BUILD.user_id (FK)
   Label: "creates"

2. BUILD → BUILD_COMPONENT (One-to-Many)
   BUILD.build_id (PK) ← BUILD_COMPONENT.build_id (FK)
   Label: "contains"

3. BUILD_COMPONENT → PRODUCT (Many-to-One)
   BUILD_COMPONENT.product_id (FK) → PRODUCT.product_id (PK)
   Label: "uses"

4. PRODUCT → CPU/GPU/RAM/STORAGE/PSU/MOTHERBOARD/COOLING (Generalization)
   Based on PRODUCT.category column
   Label: "is_a"

5. USER → CHAT (One-to-Many)
   USER.user_id (PK) ← CHAT.user_id (FK)
   Label: "has"

6. CHAT → CHAT_MESSAGE (One-to-Many)
   CHAT.chat_id (PK) ← CHAT_MESSAGE.chat_id (FK)
   Label: "contains"

7. BUILD → CHAT (Optional relationship, via CHAT.build_id FK)
   BUILD.build_id (PK) ← CHAT.build_id (FK)
   Label: "discussed in"
```

### Cardinality Notation

```
USER ||--o{ BUILD           (USER: 1-to-many, BUILD: 0-to-many)
BUILD ||--|{ BUILD_COMPONENT (BUILD: 1-to-many, BUILD_COMPONENT: 1-to-1)
BUILD_COMPONENT ||--|| PRODUCT (BUILD_COMPONENT: 1-to-1, PRODUCT: 1-to-1)
PRODUCT ||--|| [SUBTYPES]    (PRODUCT: 1-to-1, SUBTYPES: 1-to-1)
USER ||--o{ CHAT            (USER: 1-to-many, CHAT: 0-to-many)
CHAT ||--o{ CHAT_MESSAGE    (CHAT: 1-to-many, CHAT_MESSAGE: 0-to-many)
```

---

## 6. AUTHENTICATION & SECURITY FLOW

### Swim Lanes (Vertical Columns)

```
LANE 1:    User
LANE 2:    Frontend Auth
LANE 3:    Backend Auth
LANE 4:    PostgreSQL
LANE 5:    Redis Rate Limit
```

### Action/Message Sequence (Top to Bottom)

| # | From | To | Message/Action | Type |
|---|------|----|---|---|
| 1 | User | Frontend | Enter Username + Password | Input |
| 2 | Frontend | Backend | POST /api/auth/login {username, password} | Request |
| 3 | Backend | Redis | Check Rate Limit (IP Address) | Query |
| 4 | Redis | Backend | Limit OK? | Response |
| 5 | Backend | PostgreSQL | Query User (SELECT * WHERE username) | Query |
| 6 | PostgreSQL | Backend | User Record | Response |
| 7 | Backend | Backend | Verify Password (bcrypt.verify()) | Process |
| 8 | Backend | Backend | Generate JWT Token (Include User ID + Role) | Process |
| 9 | Backend | Redis | Store Token (Blacklist Cache) | Store |
| 10 | Backend | Frontend | Return JWT Token + User Info | Response |
| 11 | Frontend | Frontend | Save Token to localStorage | Store |
| 12 | User | Frontend | Make API Request | Action |
| 13 | Frontend | Backend | Include Bearer Token in Header | Request |
| 14 | Backend | Backend | Verify JWT (signature & expiry) | Process |
| 15 | Backend | Redis | Check Blacklist (Token revoked?) | Query |
| 16 | Backend | PostgreSQL | Query User (Verify Active Status) | Query |
| 17 | Backend | Frontend | ✅ Request Allowed | Response |
| 18 | User | Frontend | Logout | Action |
| 19 | Frontend | Backend | POST /api/auth/logout | Request |
| 20 | Backend | Redis | Add Token to Blacklist | Store |
| 21 | Backend | Frontend | ✅ Logged Out | Response |

### Process Groups

```
GROUP 1: LOGIN FLOW (Steps 1-11)
  - User input
  - Server validation
  - Password verification
  - Token generation
  - Client storage

GROUP 2: REQUEST AUTHORIZATION (Steps 12-17)
  - Client request with token
  - Token verification
  - User status check
  - Access grant

GROUP 3: LOGOUT FLOW (Steps 18-21)
  - User logout action
  - Token invalidation
  - Confirmation
```

### Security Controls

```
RATE LIMITING: Redis blacklist check in step 3
PASSWORD HASHING: bcrypt verification in step 7
JWT SIGNING: Token generation in step 8
TOKEN EXPIRATION: JWT signature verification in step 14
TOKEN REVOCATION: Blacklist check in step 15
```

---

## LAYOUT RECOMMENDATIONS FOR VISIO

### System Architecture (1)
- **Width**: 1400px | **Height**: 900px
- **Margins**: 50px all sides
- Layer spacing: 120px vertical
- Horizontal grouping: 150px between components in same layer

### Data Flow (2)
- **Width**: 1600px | **Height**: 700px
- **Margins**: 50px all sides
- Column width: 280px each
- Flow indicators: Curved connectors where paths branch

### AI Build Sequence (3)
- **Width**: 1200px | **Height**: 1100px
- **Margins**: 50px all sides
- Lane width: 160px each
- Message spacing: 60px vertical
- Use diagonal lines for async processing

### Component Interaction (4)
- **Width**: 1000px | **Height**: 1000px
- **Margins**: 50px all sides
- Vertical spacing: 100px between layers
- Branch indicators for parallel paths (AI, Scraping)

### Database Schema (5)
- **Width**: 1200px | **Height**: 900px
- **Margins**: 50px all sides
- Entity box: 200px × 120px
- Relationship lines: Straight with labels centered

### Authentication Flow (6)
- **Width**: 1000px | **Height**: 1200px
- **Margins**: 50px all sides
- Lane width: 190px each
- Process boxes: 160px × 60px
- Decision diamonds: 80px × 80px
