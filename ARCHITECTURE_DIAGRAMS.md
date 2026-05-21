# PC Builder System Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph Client["🖥️ Frontend"]
        Browser["React/TypeScript<br/>Vite SPA"]
        Pages["Pages: Login, Dashboard,<br/>Builder, AI Chat,<br/>Products, Scraping"]
        Hooks["Hooks: useAIBuild,<br/>useAIChat"]
    end

    subgraph API["🔗 API Gateway"]
        FastAPI["FastAPI Server<br/>Port 8000"]
        AuthRouter["Auth Router"]
        BuilderRouter["Builder Router"]
        ChatRouter["Chat Router"]
        ProductRouter["Product Router"]
        ScrapingRouter["Scraping Router"]
    end

    subgraph Services["⚙️ Backend Services"]
        AuthService["Auth Service<br/>JWT + Rate Limit"]
        BuilderService["Builder Service<br/>Component Management"]
        DatabaseService["Database Service<br/>ORM & Queries"]
        FeatureExtractor["Feature Extractor<br/>ML Pipeline"]
        ScoringEngine["Scoring Engine<br/>Compatibility Check"]
        Mapper["Mapper<br/>Data Transformation"]
    end

    subgraph Queue["📬 Task Queue"]
        Redis["Redis<br/>Broker & Cache"]
        CeleryWorker["Celery Worker<br/>Background Jobs"]
        CeleryBeat["Celery Beat<br/>Scheduled Tasks"]
    end

    subgraph Tasks["🔧 Task Processors"]
        AITasks["AI Tasks<br/>LLM Interactions"]
        ScrapingTasks["Scraping Tasks<br/>Web Crawling"]
    end

    subgraph Storage["💾 Data Storage"]
        PostgreSQL["PostgreSQL<br/>Main Database"]
        Tables["Tables: Users, Builds,<br/>Products, Chats,<br/>Components"]
    end

    subgraph External["🌐 External Services"]
        VeniceAI["Venice AI<br/>LLM API"]
        Telemart["Telemart<br/>Scraper"]
        OtherSources["Other Product<br/>Sources"]
    end

    Browser -->|HTTP/WS| FastAPI
    Pages -->|API Calls| Browser
    Hooks -->|State Management| Pages

    FastAPI --> AuthRouter
    FastAPI --> BuilderRouter
    FastAPI --> ChatRouter
    FastAPI --> ProductRouter
    FastAPI --> ScrapingRouter

    AuthRouter --> AuthService
    BuilderRouter --> BuilderService
    ChatRouter --> BuilderService
    ProductRouter --> DatabaseService
    ScrapingRouter --> DatabaseService

    BuilderService --> FeatureExtractor
    BuilderService --> ScoringEngine
    BuilderService --> Mapper

    DatabaseService --> PostgreSQL
    PostgreSQL --> Tables

    FastAPI --> Redis
    Redis --> CeleryWorker
    Redis --> CeleryBeat

    CeleryWorker --> AITasks
    CeleryWorker --> ScrapingTasks
    CeleryBeat -->|Trigger| ScrapingTasks

    AITasks -->|Query| PostgreSQL
    ScrapingTasks -->|Query| PostgreSQL

    AITasks -->|API Call| VeniceAI
    ScrapingTasks -->|Crawl| Telemart
    ScrapingTasks -->|Crawl| OtherSources

    CeleryWorker -->|Update Cache| Redis
    Redis -->|Query Cache| FastAPI
```

---

## Data Flow Diagram

```mermaid
graph LR
    subgraph Request["📥 Request Phase"]
        User["👤 User"]
        Action["Action:<br/>Build PC / Chat / Search"]
        HTTPReq["HTTP Request"]
    end

    subgraph Processing["⚡ Processing Phase"]
        Validate["Validate &<br/>Authenticate"]
        AuthCheck{Auth OK?}
        ParseData["Parse Request<br/>Data"]
        ApplyLogic["Apply Business<br/>Logic"]
        Query["Query Database"]
    end

    subgraph Async["🔄 Async Processing"]
        QueueTask["Queue Task<br/>to Redis"]
        AsyncWork["Background<br/>Worker Process"]
        ExternalAPI["Call External<br/>API/Scraper"]
        ProcessResult["Process<br/>Result"]
        StoreResult["Store in<br/>Database"]
    end

    subgraph Response["📤 Response Phase"]
        PrepareResp["Prepare<br/>Response"]
        Cache["Cache in<br/>Redis"]
        SendResp["Send HTTP<br/>Response"]
        ClientUpdate["Update<br/>Client State"]
    end

    subgraph Feedback["🔁 Feedback Loop"]
        WSNotify["WebSocket<br/>Notification"]
        RealTime["Real-time<br/>Updates"]
    end

    User -->|Trigger| Action
    Action -->|Send| HTTPReq
    HTTPReq --> Validate
    Validate --> AuthCheck
    AuthCheck -->|Yes| ParseData
    AuthCheck -->|No| SendResp
    ParseData --> ApplyLogic
    ApplyLogic --> Query
    Query --> PrepareResp

    ApplyLogic -->|Heavy Task| QueueTask
    QueueTask --> AsyncWork
    AsyncWork --> ExternalAPI
    ExternalAPI --> ProcessResult
    ProcessResult --> StoreResult
    StoreResult -->|Update DB| Query

    PrepareResp --> Cache
    Cache --> SendResp
    SendResp --> ClientUpdate

    AsyncWork -->|Notify| WSNotify
    WSNotify --> RealTime
    RealTime --> ClientUpdate
```

---

## Sequence Diagram: AI-Assisted PC Build Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend as FastAPI<br/>Backend
    participant DB as PostgreSQL
    participant Redis as Redis<br/>Queue
    participant Worker as Celery<br/>Worker
    participant AI as Venice AI<br/>API

    User->>Frontend: Start AI Build<br/>with Budget
    Frontend->>Backend: POST /api/builder/ai-build<br/>{budget, preferences}

    Backend->>DB: Verify User<br/>& Get Preferences
    DB-->>Backend: User Data

    Backend->>Backend: Extract Features<br/>from Request

    Backend->>Redis: Queue AI Task<br/>task_id: uuid
    Backend-->>Frontend: Return task_id<br/>HTTP 202
    Frontend->>User: Building...<br/>Show Progress

    Backend->>Worker: Dequeue Task
    Worker->>Worker: Initialize<br/>Build Context

    Worker->>AI: Request:<br/>Recommended Components<br/>{budget, preferences}
    AI-->>Worker: AI Response:<br/>Component List

    Worker->>DB: Query Products<br/>by Category<br/>& Price Range
    DB-->>Worker: Product List

    Worker->>Worker: Rank Components<br/>by Score<br/>(FeatureExtractor)

    Worker->>Worker: Check Compatibility<br/>(ScoringEngine)

    Worker->>DB: Insert Build<br/>with Components
    DB-->>Worker: Build ID

    Worker->>Redis: Store Result<br/>task_id → build_data

    Frontend->>Backend: Poll /api/tasks/{id}
    Backend->>Redis: Check Task Status
    Redis-->>Backend: Result Ready
    Backend-->>Frontend: Build Result<br/>+ Components

    Frontend->>User: ✅ Build Complete<br/>Show Components<br/>& Total Cost
```

---

## Component Interaction: Builder Workflow

```mermaid
graph TD
    A["👤 User Initiates<br/>Build Request"] -->|Selected Components| B["BuilderService<br/>validates_build"]

    B -->|Extract Features| C["FeatureExtractor<br/>parse_specs<br/>normalize_values"]
    C -->|Features Dict| D["ScoringEngine<br/>check_compatibility<br/>calculate_score"]

    D -->|Component Scores| E["Mapper<br/>transform_build_data<br/>serialize_components"]

    E -->|Build Data| F["DatabaseService<br/>Create Build Record"]
    F -->|SQL Query| G["PostgreSQL<br/>INSERT Build<br/>INSERT BuildComponents"]

    G -->|Result| H["Response Handler<br/>format_response"]

    H -->|JSON Response| I["Frontend<br/>Update State<br/>BuildCard Component"]

    I -->|Display| J["✅ Build Displayed<br/>to User"]

    K["AI Build Request"] -->|Enqueue| L["Redis Queue<br/>ai_tasks.py"]
    L -->|Worker Pick-up| M["CeleryWorker<br/>ai_build_task"]
    M -->|API Call| N["Venice AI<br/>LLM Response"]
    N -->|Component Recs| B

    O["Scheduled Scraping"] -->|Cron Job| P["CeleryBeat<br/>Trigger Schedule"]
    P -->|Queue| L
    M -->|Product Scraping| Q["ScrapingTasks<br/>telemart_scraper"]
    Q -->|Parse HTML| R["Product Data"]
    R -->|Store| G
```

---

## Database Schema Overview

```mermaid
erDiagram
    USER ||--o{ BUILD : creates
    USER ||--o{ CHAT : has
    USER {
        int user_id
        string username
        string email
        string password_hash
        timestamp created_at
    }

    BUILD ||--|{ BUILD_COMPONENT : contains
    BUILD {
        int build_id
        int user_id
        string name
        text description
        float total_cost
        int total_power
        timestamp created_at
    }

    BUILD_COMPONENT ||--|| PRODUCT : uses
    BUILD_COMPONENT {
        int component_id
        int build_id
        int product_id
        int quantity
        string source
        timestamp added_at
    }

    PRODUCT ||--|| CPU : is_a
    PRODUCT ||--|| GPU : is_a
    PRODUCT ||--|| RAM : is_a
    PRODUCT ||--|| STORAGE : is_a
    PRODUCT ||--|| PSU : is_a
    PRODUCT ||--|| MOTHERBOARD : is_a
    PRODUCT ||--|| COOLING : is_a

    PRODUCT {
        int product_id
        string name
        string category
        float price
        string source
        text specs
        text metadata
        timestamp scraped_at
    }

    CHAT ||--o{ CHAT_MESSAGE : contains
    CHAT {
        int chat_id
        int user_id
        int build_id FK
        timestamp created_at
    }

    CHAT_MESSAGE {
        int message_id
        int chat_id
        string role
        text content
        timestamp created_at
    }
```

---

## Authentication & Security Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend<br/>Auth
    participant Backend as Backend<br/>Auth
    participant DB as PostgreSQL
    participant Redis as Redis<br/>Rate Limit

    User->>Frontend: Enter Username +<br/>Password
    Frontend->>Backend: POST /api/auth/login<br/>{username, password}

    Backend->>Redis: Check Rate Limit<br/>IP Address
    Redis-->>Backend: Limit OK?

    Backend->>DB: Query User<br/>SELECT * WHERE username
    DB-->>Backend: User Record

    Backend->>Backend: Verify Password<br/>bcrypt.verify()

    Backend->>Backend: Generate JWT Token<br/>Include User ID + Role

    Backend->>Redis: Store Token<br/>Blacklist Cache

    Backend-->>Frontend: Return JWT Token<br/>+ User Info

    Frontend->>Frontend: Save Token<br/>to localStorage

    User->>Frontend: Make API Request
    Frontend->>Backend: Include Bearer Token<br/>in Header

    Backend->>Backend: Verify JWT<br/>signature & expiry

    Backend->>Redis: Check Blacklist<br/>Token revoked?

    Backend->>DB: Query User<br/>Verify Active Status

    Backend-->>Frontend: ✅ Request Allowed

    User->>Frontend: Logout
    Frontend->>Backend: POST /api/auth/logout
    Backend->>Redis: Add Token<br/>to Blacklist
    Backend-->>Frontend: ✅ Logged Out
```
