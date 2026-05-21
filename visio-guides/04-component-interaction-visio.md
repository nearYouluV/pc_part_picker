# Visio: Component Interaction Builder Workflow

## Canvas Size: 1000px × 1000px

## LAYER STRUCTURE (Top to Bottom)

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1 (Y: 50px)      - USER INPUT                │
├─────────────────────────────────────────────────────┤
│ LAYER 2 (Y: 130px)     - SERVICE LAYER             │
├─────────────────────────────────────────────────────┤
│ LAYER 3 (Y: 210px)     - FEATURE EXTRACTION        │
├─────────────────────────────────────────────────────┤
│ LAYER 4 (Y: 310px)     - SCORING & MAPPING         │
├─────────────────────────────────────────────────────┤
│ LAYER 5 (Y: 410px)     - PERSISTENCE               │
├─────────────────────────────────────────────────────┤
│ LAYER 6 (Y: 550px)     - ASYNC/QUEUE               │
├─────────────────────────────────────────────────────┤
│ LAYER 7 (Y: 750px)     - OUTPUT & DISPLAY          │
└─────────────────────────────────────────────────────┘
```

## COMPONENTS & POSITIONING

### LAYER 1: USER INPUT (Y: 50px)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| User Initiates Build | 350 | Person | 300×60 | 👤 User Initiates Build Request |

### LAYER 2: SERVICE LAYER (Y: 130px)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| BuilderService | 350 | Rectangle | 300×60 | BuilderService validates_build |

### LAYER 3: FEATURE EXTRACTION (Y: 210px)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| FeatureExtractor | 200 | Rectangle | 280×60 | FeatureExtractor parse_specs normalize_values |

### LAYER 4: SCORING & MAPPING (Y: 310px)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| ScoringEngine | 150 | Rectangle | 280×60 | ScoringEngine check_compatibility |
| Mapper | 500 | Rectangle | 280×60 | Mapper transform_build_data |

### LAYER 5: PERSISTENCE (Y: 410px)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| DatabaseService | 250 | Rectangle | 260×60 | DatabaseService Create Build Record |
| PostgreSQL | 580 | Cylinder | 140×80 | INSERT Build/Components |

### LAYER 6: ASYNC/QUEUE (Y: 550px - TOP BRANCH)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| Redis Queue | 100 | Cylinder | 120×80 | Redis Queue ai_tasks.py |
| CeleryWorker | 300 | Rectangle | 160×60 | CeleryWorker ai_build_task |
| Venice AI | 550 | Cloud | 140×60 | Venice AI LLM Response |

### LAYER 6: SCHEDULING BRANCH (Y: 550px - MIDDLE)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| Scheduled Scraping | 50 | Event | 120×40 | Scheduled Scraping |
| CeleryBeat | 250 | Rectangle | 140×60 | CeleryBeat Trigger |

### LAYER 6: ASYNC/QUEUE (Y: 550px - BOTTOM BRANCH)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| ScrapingTasks | 700 | Rectangle | 160×60 | ScrapingTasks telemart_scraper |
| ProductData | 900 | Database | 120×60 | Product Data |

### LAYER 7: OUTPUT (Y: 750px)
| Component | X Pos | Shape | Size | Label |
|-----------|-------|-------|------|-------|
| Frontend | 350 | Rectangle | 280×60 | Frontend Update State BuildCard |
| Display | 350 | Rectangle | 280×60 | ✅ Build Displayed to User |

## FLOW PATHS & CONNECTIONS

### PRIMARY FLOW (Synchronous Main Path)
```
User Initiates Build (Y: 50)
  ↓ [Selected Components]
BuilderService (Y: 130)
  ↓ [Extract Features]
FeatureExtractor (Y: 210)
  ↓ [Features Dict]
ScoringEngine (Y: 310)
  ↓ [Component Scores]
Mapper (Y: 310)
  ↓ [Build Data]
DatabaseService (Y: 410)
  ↓ [SQL Query]
PostgreSQL (Y: 410)
  ↓ [Result]
Response Handler
  ↓ [JSON Response]
Frontend (Y: 750)
  ↓ [Display]
Build Display (Y: 750)
```

### AI BUILD BRANCH (Asynchronous)
```
AI Build Request (initiates at Layer 2)
  ↓ [Enqueue]
Redis Queue (Y: 550)
  ↓ [Worker Pick-up]
CeleryWorker (Y: 550)
  ↓ [API Call]
Venice AI (Y: 550)
  ↓ [Component Recs]
BuilderService (feedback to Layer 2)
```

### SCRAPING BRANCH (Scheduled)
```
Scheduled Scraping (Y: 550 trigger)
  ↓ [Cron Job Trigger]
CeleryBeat (Y: 550)
  ↓ [Queue]
Redis Queue (Y: 550)
  ↓ [Product Scraping]
ScrapingTasks (Y: 550)
  ↓ [Parse HTML]
ProductData (Y: 550)
  ↓ [Store]
PostgreSQL (feedback to Layer 5)
```

## CONNECTION SPECIFICATIONS

### Connection 1: User → BuilderService
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| User Initiates | BuilderService | Selected Components | Request | Solid arrow, blue |

### Connection 2: BuilderService → FeatureExtractor
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| BuilderService | FeatureExtractor | Extract Features | Process | Solid arrow, black |

### Connection 3: FeatureExtractor → ScoringEngine
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| FeatureExtractor | ScoringEngine | Features Dict | Data | Solid arrow, green |

### Connection 4: ScoringEngine → Mapper
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| ScoringEngine | Mapper | Component Scores | Data | Solid arrow, green |

### Connection 5: Mapper → DatabaseService
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| Mapper | DatabaseService | Build Data | Request | Solid arrow, blue |

### Connection 6: DatabaseService → PostgreSQL
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| DatabaseService | PostgreSQL | SQL Query | Query | Solid arrow, orange |

### Connection 7: PostgreSQL → ResponseHandler
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| PostgreSQL | Response Handler | Result | Response | Dashed arrow, orange |

### Connection 8: ResponseHandler → Frontend
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| Response Handler | Frontend | JSON Response | Data | Solid arrow, blue |

### Connection 9: Frontend → Display
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| Frontend | Build Display | Display | UI Update | Solid arrow, green |

### Connection 10: BuilderService → Redis Queue (AI Branch)
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| BuilderService | Redis Queue | Enqueue | Async | Dashed arrow, orange |

### Connection 11: Redis Queue → CeleryWorker
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| Redis Queue | CeleryWorker | Worker Pick-up | Trigger | Dashed arrow, orange |

### Connection 12: CeleryWorker → Venice AI
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| CeleryWorker | Venice AI | API Call | Request | Solid arrow, purple |

### Connection 13: Venice AI → BuilderService (Feedback)
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| Venice AI | BuilderService | Component Recs | Response | Dashed arrow, purple |

### Connection 14: Scheduled Scraping → CeleryBeat
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| Scheduled Scraping | CeleryBeat | Cron Job Trigger | Trigger | Dashed arrow, red |

### Connection 15: CeleryBeat → Redis Queue
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| CeleryBeat | Redis Queue | Queue | Async | Dashed arrow, orange |

### Connection 16: CeleryWorker → ScrapingTasks
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| CeleryWorker | ScrapingTasks | Product Scraping | Process | Dashed arrow, black |

### Connection 17: ScrapingTasks → ProductData
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| ScrapingTasks | ProductData | Parse HTML | Transform | Solid arrow, green |

### Connection 18: ProductData → PostgreSQL (Feedback)
| From | To | Label | Type | Style |
|------|-----|-------|------|-------|
| ProductData | PostgreSQL | Store | Insert | Solid arrow, orange |

## COLOR LEGEND

- **Blue**: Request/Response, HTTP communication
- **Green**: Data transformation, successful operations
- **Orange**: Database, async queues
- **Purple**: External API calls
- **Red**: Scheduled/Trigger events
- **Black**: Internal process calls
- **Solid arrows**: Synchronous/active connections
- **Dashed arrows**: Asynchronous/trigger connections

## LAYOUT NOTES

1. Main flow runs vertically down center (X: 350)
2. Left branch (X: 100-300): AI/Async processing
3. Right branch (X: 500-900): External services, storage, scraping
4. Layer spacing: 80-100px vertical
5. Horizontal distribution: Keep related components near each other
