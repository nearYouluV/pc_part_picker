# Visio: AI Build Sequence Diagram

## Canvas Size: 1200px × 1100px

## SWIM LANES (Vertical Columns)

```
┌──────────┬────────────┬────────────┬────────────┬────────────┬────────────┬────────────┐
│ LANE 1   │ LANE 2     │ LANE 3     │ LANE 4     │ LANE 5     │ LANE 6     │ LANE 7     │
│ (X: 80)  │ (X: 240)   │ (X: 400)   │ (X: 560)   │ (X: 720)   │ (X: 880)   │ (X: 1040)  │
│ User     │ Frontend   │ FastAPI    │ PostgreSQL │ Redis      │ Celery     │ Venice AI  │
│          │            │ Backend    │            │ Queue      │ Worker     │ API        │
└──────────┴────────────┴────────────┴────────────┴────────────┴────────────┴────────────┘
```

## ACTOR/COMPONENT POSITIONING (Top Y: 30px)

| Lane | X Pos | Actor | Shape | Width |
|------|-------|-------|-------|-------|
| 1 | 80 | User | Person | 60 |
| 2 | 240 | Frontend | Box | 100 |
| 3 | 400 | FastAPI Backend | Box | 100 |
| 4 | 560 | PostgreSQL | Cylinder | 100 |
| 5 | 720 | Redis Queue | Cylinder | 100 |
| 6 | 880 | Celery Worker | Box | 100 |
| 7 | 1040 | Venice AI API | Cloud | 100 |

## LIFELINES (Vertical Dashed Lines)

All lifelines run from Y: 60px to Y: 1050px at X positions: 80, 240, 400, 560, 720, 880, 1040

## MESSAGE SEQUENCE (Top to Bottom, Y positions)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 1 | 100 | User (1) | Frontend (2) | Start AI Build with Budget | Solid Arrow | Synchronous |
| 2 | 150 | Frontend (2) | FastAPI (3) | POST /api/builder/ai-build | Solid Arrow | HTTP Request |
| 3 | 200 | FastAPI (3) | PostgreSQL (4) | Verify User & Get Preferences | Solid Arrow | Query |
| 4 | 250 | PostgreSQL (4) | FastAPI (3) | User Data | Dashed Arrow | Response |
| 5 | 300 | FastAPI (3) | FastAPI (3) | Extract Features | Self-arrow | Process |
| 6 | 350 | FastAPI (3) | Redis (5) | Queue AI Task (task_id: uuid) | Solid Arrow | Async Queue |
| 7 | 400 | FastAPI (3) | Frontend (2) | Return task_id (HTTP 202) | Dashed Arrow | Response |
| 8 | 450 | Frontend (2) | User (1) | Building... Show Progress | Solid Arrow | UI Update |
| 9 | 500 | Redis (5) | Celery (6) | Dequeue Task | Solid Arrow | Trigger |
| 10 | 550 | Celery (6) | Celery (6) | Initialize Build Context | Self-arrow | Process |
| 11 | 600 | Celery (6) | Venice (7) | Request: Recommended Components | Solid Arrow | API Call |
| 12 | 650 | Venice (7) | Celery (6) | AI Response: Component List | Dashed Arrow | Response |
| 13 | 700 | Celery (6) | PostgreSQL (4) | Query Products by Category | Solid Arrow | Query |
| 14 | 750 | PostgreSQL (4) | Celery (6) | Product List | Dashed Arrow | Response |
| 15 | 800 | Celery (6) | Celery (6) | Rank Components by Score | Self-arrow | Process |
| 16 | 850 | Celery (6) | Celery (6) | Check Compatibility | Self-arrow | Process |
| 17 | 900 | Celery (6) | PostgreSQL (4) | Insert Build with Components | Solid Arrow | Insert |
| 18 | 950 | PostgreSQL (4) | Celery (6) | Build ID | Dashed Arrow | Response |
| 19 | 1000 | Celery (6) | Redis (5) | Store Result (task_id → data) | Solid Arrow | Store |
| 20 | 1050 | Frontend (2) | FastAPI (3) | Poll /api/tasks/{id} | Solid Arrow | Request |

## CONTINUATION SEQUENCE (2nd screen, if needed)

| Step | Y Pos | From Lane | To Lane | Message | Type |
|------|-------|-----------|---------|---------|------|
| 21 | 100 | FastAPI (3) | Redis (5) | Check Task Status | Query |
| 22 | 150 | Redis (5) | FastAPI (3) | Result Ready | Response |
| 23 | 200 | FastAPI (3) | Frontend (2) | Build Result + Components | Response |
| 24 | 250 | Frontend (2) | User (1) | ✅ Build Complete | UI Update |

## ARROW TYPES

```
Solid Arrow (→):     Synchronous call or request
Dashed Arrow (⇢):    Response or asynchronous notification
Self-Arrow:          Internal process or method call
Thick Arrow:         Critical path or primary flow
Thin Arrow:          Secondary flow or data flow
```

## TIMING ANNOTATIONS

```
T0-T4 (Y: 100-250):    Initial request and validation
T5-T8 (Y: 300-450):    Async task queueing
T9-T19 (Y: 500-1000):  Background async processing
T20-T24 (Y: 1050-250): Result polling and delivery
```

## GROUPING BOXES (Optional, for visual clarity)

| Group | Y Range | Height | Label | Color |
|-------|---------|--------|-------|-------|
| Request Phase | 100-300 | 200 | Synchronous Request | Light Blue |
| Queueing Phase | 350-450 | 100 | Async Queueing | Light Orange |
| Processing Phase | 500-1000 | 500 | Background Processing | Light Green |
| Delivery Phase | 1050-1100 | 50 | Result Delivery | Light Purple |

## POSITIONING GUIDELINES

1. Keep lane width consistent (160px each)
2. Vertical spacing between messages: 50px
3. Message labels: Centered above/below arrows
4. Self-arrows: Semi-circle on right side of lane
5. Response arrows: Dashed, returning to left
6. Processing boxes: Small rectangles on lifeline at step points
7. Long-running processes: Use activation boxes (small vertical rectangles on lifeline)

## ACTIVATION BOXES (Processing Duration)

Place small vertical rectangles (20px wide) on lifelines during:
- Steps 3-4: FastAPI & PostgreSQL
- Steps 13-18: Celery Worker & PostgreSQL
