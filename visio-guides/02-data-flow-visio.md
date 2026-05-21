# Visio: Data Flow Diagram

## Canvas Size: 1600px × 700px

## COLUMN STRUCTURE

```
┌────────────────┬────────────────┬────────────────┬────────────────┬────────────────┐
│ COLUMN 1       │ COLUMN 2       │ COLUMN 3       │ COLUMN 4       │ COLUMN 5       │
│ (X: 100-280px) │ (X: 300-480px) │ (X: 500-680px) │ (X: 700-880px) │ (X: 900-1080px)│
│ REQUEST PHASE  │ PROCESSING PH. │ ASYNC BRANCH   │ RESPONSE PH.   │ FEEDBACK LOOP  │
└────────────────┴────────────────┴────────────────┴────────────────┴────────────────┘
```

## COMPONENTS & POSITIONING

### COLUMN 1: REQUEST PHASE (X: 100-280px)
| Component | Y Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| User | 50 | Person | 60×60 | 👤 User |
| Action | 150 | Text Box | 140×60 | Action: Build PC / Chat / Search |
| HTTP Request | 250 | Arrow | 140×40 | HTTP Request |

### COLUMN 2: PROCESSING PHASE (X: 300-480px)
| Component | Y Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| Validate & Authenticate | 80 | Rectangle | 140×60 | Validate & Authenticate |
| Auth OK? | 180 | Diamond | 100×80 | Auth OK? |
| Parse Request Data | 300 | Rectangle | 140×60 | Parse Request Data |
| Apply Business Logic | 400 | Rectangle | 140×60 | Apply Business Logic |
| Query Database | 500 | Rectangle | 140×60 | Query Database |

### COLUMN 3: ASYNC PROCESSING (X: 500-680px)
| Component | Y Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| Queue Task to Redis | 150 | Rectangle | 140×60 | Queue Task to Redis |
| Background Worker | 280 | Rectangle | 140×60 | Background Worker Process |
| Call External API | 380 | Rectangle | 140×60 | Call External API/Scraper |
| Process Result | 480 | Rectangle | 140×60 | Process Result |
| Store in Database | 580 | Rectangle | 140×60 | Store in Database |

### COLUMN 4: RESPONSE PHASE (X: 700-880px)
| Component | Y Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| Prepare Response | 150 | Rectangle | 140×60 | Prepare Response |
| Cache in Redis | 250 | Rectangle | 140×60 | Cache in Redis |
| Send HTTP Response | 350 | Rectangle | 140×60 | Send HTTP Response |
| Update Client State | 450 | Rectangle | 140×60 | Update Client State |

### COLUMN 5: FEEDBACK LOOP (X: 900-1080px)
| Component | Y Position | Shape | Size | Label |
|-----------|-----------|-------|------|-------|
| WebSocket Notification | 300 | Rectangle | 140×60 | WebSocket Notification |
| Real-time Updates | 420 | Rectangle | 140×60 | Real-time Updates |

## FLOW PATHS

### Path 1: Main Synchronous Flow
```
User → Action → HTTP Request → Validate & Authenticate → Auth OK? (YES)
  → Parse Request Data → Apply Business Logic → Query Database → Prepare Response
  → Cache in Redis → Send HTTP Response → Update Client State
```

### Path 2: Auth Failed Path
```
Auth OK? (NO) → Send HTTP Response
```

### Path 3: Async Processing Branch
```
Apply Business Logic → Queue Task to Redis (Heavy Task indicator)
  → Background Worker Process → Call External API/Scraper → Process Result
  → Store in Database → Query Database (Update DB feedback)
```

### Path 4: Async Notification Loop
```
Background Worker Process → WebSocket Notification (Notify)
  → Real-time Updates → Update Client State
```

## CONNECTIONS & LABELS

### Main Flow Connectors
| From | To | Label | Style |
|------|-----|-------|-------|
| User | Action | | Solid black arrow |
| Action | HTTP Request | Send | Solid blue arrow |
| HTTP Request | Validate & Authenticate | | Solid blue arrow |
| Validate & Authenticate | Auth OK? | | Solid black arrow |
| Auth OK? | Parse Request Data | Yes | Solid green arrow (right) |
| Auth OK? | Send HTTP Response | No | Solid red arrow (down) |
| Parse Request Data | Apply Business Logic | | Solid black arrow |
| Apply Business Logic | Query Database | | Solid blue arrow |
| Apply Business Logic | Queue Task | Heavy Task | Solid orange arrow (branch) |
| Query Database | Prepare Response | | Solid black arrow |
| Prepare Response | Cache in Redis | | Solid orange arrow |
| Cache in Redis | Send HTTP Response | | Solid orange arrow |
| Send HTTP Response | Update Client State | | Solid blue arrow |

### Async Branch Connectors
| From | To | Label | Style |
|------|-----|-------|-------|
| Queue Task | Background Worker | | Solid orange arrow |
| Background Worker | Call External API | | Solid purple arrow |
| Call External API | Process Result | | Solid purple arrow |
| Process Result | Store in Database | | Solid green arrow |
| Store in Database | Query Database | Update DB | Dashed green arrow (feedback) |

### Async Notification Connectors
| From | To | Label | Style |
|------|-----|-------|-------|
| Background Worker | WebSocket Notification | Notify | Dashed orange arrow |
| WebSocket Notification | Real-time Updates | | Dashed orange arrow |
| Real-time Updates | Update Client State | | Dashed blue arrow |

## POSITIONING GUIDELINES

1. **Column widths**: 180px per column, 20px margins
2. **Flow direction**: Left-to-right primary, top-to-bottom within columns
3. **Branching**: Use curved arrows for branch paths (Auth failure, async)
4. **Feedback loops**: Use dashed lines for return paths
5. **Labels**: Place on connector center with light background
6. **Grouping**: Use swim lane backgrounds for visual grouping

## COLOR CODING

- **Blue**: HTTP/Frontend communication
- **Green**: Database operations
- **Orange**: Queue/Cache operations
- **Purple**: External services
- **Red**: Error/rejection paths
- **Black**: Control flow
- **Dashed**: Async/Feedback operations
