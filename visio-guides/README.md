# Visio Diagram Recreation - Complete Master Guide

## Overview

This guide provides comprehensive specifications for manually recreating all 6 architecture diagrams in Microsoft Visio. Each diagram includes:

- **Canvas specifications** (dimensions, margins)
- **Component positioning** (coordinates, shapes, sizes)
- **Connection definitions** (source, target, labels, styles)
- **Layout guidelines** (layers, spacing, alignment)
- **Color coding** (visual hierarchy)
- **Line styles** (solid, dashed, decorative)

---

## Quick Reference: Diagram Index

| # | Diagram | File | Canvas | Components | Connections |
|---|---------|------|--------|------------|------------|
| 1 | System Architecture | `01-system-architecture-visio.md` | 1400×900 | 22 | 40+ |
| 2 | Data Flow | `02-data-flow-visio.md` | 1600×700 | 15 | 20+ |
| 3 | AI Build Sequence | `03-ai-build-sequence-visio.md` | 1200×1100 | 7 lanes | 24 messages |
| 4 | Component Interaction | `04-component-interaction-visio.md` | 1000×1000 | 18 | 18 |
| 5 | Database Schema ER | `05-database-schema-visio.md` | 1200×900 | 8 entities | 7 relationships |
| 6 | Auth & Security | `06-authentication-security-visio.md` | 1000×1200 | 5 lanes | 23 messages |

---

## General Visio Setup Instructions

### Page Setup for Each Diagram

1. **File** → **Page Setup**
2. **Page Size**: Set to custom dimensions (see table above)
3. **Print Options**:
   - Orientation: Portrait (for sequences) or Landscape (for architecture)
   - Margins: 0.5 inches all sides
4. **Drawing Scale**: 1 inch = 1 pixel (100%)

### Connector Defaults

Set default connector properties:
1. Right-click connector → **Set as Default**
2. Default line width: 1.5pt
3. Default color: Black
4. Default line pattern: Solid

### Font Standards

Apply these across all diagrams:
- **Component labels**: Arial 10pt, bold
- **Connection labels**: Arial 9pt, normal
- **Entity attributes**: Arial 8pt, normal
- **Annotations**: Arial 8pt, italic

---

## Diagram 1: System Architecture

### Summary
Multi-layer architecture showing all system components and their interactions across 6 layers.

### Key Specifications
- **Canvas**: 1400 × 900px
- **Layers**: 6 (Client, API, Services, Queue, Storage, External)
- **Components**: 22 boxes/cylinders/clouds
- **Connections**: 40+ with various styles
- **Primary colors**: Blue (HTTP), Green (DB), Orange (Queue), Purple (External)

### Step-by-Step Recreation

1. **Create canvas** (1400×900)
2. **Draw layer separators** (6 horizontal guides at Y: 80, 200, 320, 470, 620, 750)
3. **Place layer 1 components** (Client: 3 boxes at Y≈80)
4. **Place layer 2 components** (API: 1 rectangle + 5 ovals at Y≈200)
5. **Place layer 3 components** (Services: 6 boxes at Y≈320)
6. **Place layer 4 components** (Queue: 5 items at Y≈470)
7. **Place layer 5 components** (Storage: 2 cylinders at Y≈620)
8. **Place layer 6 components** (External: 3 clouds at Y≈750)
9. **Draw all connections** (use routing guides for clean paths)
10. **Add labels** to connections
11. **Apply colors** to connection lines

### See File: `01-system-architecture-visio.md`

---

## Diagram 2: Data Flow

### Summary
Shows the flow of data through the system from request initiation to response delivery, including async branches.

### Key Specifications
- **Canvas**: 1600 × 700px
- **Layout**: 5 columns (Request, Processing, Async, Response, Feedback)
- **Components**: 15 process boxes + diamonds + actors
- **Connections**: 20+ with branching logic
- **Special feature**: Diamond decision node for authorization

### Step-by-Step Recreation

1. **Create canvas** (1600×700)
2. **Draw column separators** (vertical guides at X: 100, 300, 500, 700, 900)
3. **Place column 1** (Request: User, Action, HTTP Request)
4. **Place column 2** (Processing: 5 boxes, 1 diamond decision)
5. **Place column 3** (Async: 5 process boxes on right side)
6. **Place column 4** (Response: 4 boxes)
7. **Place column 5** (Feedback: 2 boxes)
8. **Draw main flow** (left-to-right primary path)
9. **Draw auth failure path** (from diamond down to Send Response)
10. **Draw async branch** (from Apply Logic to Queue Task)
11. **Draw response flow** (Query → Prepare → Cache → Send)
12. **Draw notification loop** (Worker → WebSocket → RealTime → Update)
13. **Add all labels** and color-code connections

### See File: `02-data-flow-visio.md`

---

## Diagram 3: AI Build Sequence

### Summary
Detailed sequence diagram showing the AI-assisted PC build workflow with 7 swim lanes and 24 interaction messages.

### Key Specifications
- **Canvas**: 1200 × 1100px
- **Layout**: 7 swim lanes (columns)
- **Messages**: 24 steps (synchronous + asynchronous)
- **Special features**: Activation boxes, self-arrows, async messaging
- **Timeline**: Request → Queueing → Processing → Delivery (4 phases)

### Step-by-Step Recreation

1. **Create canvas** (1200×1100)
2. **Draw 7 vertical lifelines** (dashed lines at X: 80, 240, 400, 560, 720, 880, 1040)
3. **Place 7 actor boxes** at top (Y: 30)
4. **Label each lifeline** (User, Frontend, Backend, PostgreSQL, Redis, Celery Worker, Venice AI)
5. **Create activation boxes** (small rectangles on lifelines where components are active)
6. **Draw message 1-8** (Request phase, Y: 100-450)
   - Messages are arrows between lanes
   - Use solid arrows for requests, dashed for responses
7. **Draw messages 9-19** (Processing phase, Y: 500-1000)
   - Include self-arrows for internal processing
   - Route between worker and databases
8. **Draw messages 20-24** (Delivery phase, Y: 1050+)
   - Polling pattern (Frontend checks Redis status)
   - Final response to user
9. **Add message labels** (above/below arrows, centered)
10. **Add timing annotations** (optional: time markers on left)
11. **Apply colors** (Blue for HTTP, Green for DB, Orange for async, Purple for AI)

### See File: `03-ai-build-sequence-visio.md`

---

## Diagram 4: Component Interaction

### Summary
Shows how builder workflow components interact, with main synchronous path and parallel async branches (AI and Scraping).

### Key Specifications
- **Canvas**: 1000 × 1000px
- **Layers**: 7 (top to bottom)
- **Components**: 18 (mix of boxes, cylinders, clouds)
- **Special features**: 3 parallel branches (Main, AI, Scraping)
- **Flow**: Vertical with horizontal branching

### Step-by-Step Recreation

1. **Create canvas** (1000×1000)
2. **Draw 7 layer guidelines** (horizontal dashed lines at Y: 50, 130, 210, 310, 410, 550, 750)
3. **Place layer 1** (Y: 50): User Initiates (centered, X: 350)
4. **Place layer 2** (Y: 130): BuilderService (centered, X: 350)
5. **Place layer 3** (Y: 210): FeatureExtractor (left, X: 200)
6. **Place layer 4** (Y: 310): ScoringEngine (left, X: 150) + Mapper (right, X: 500)
7. **Place layer 5** (Y: 410): DatabaseService (center-left, X: 250) + PostgreSQL (right, X: 580)
8. **Place layer 6** (Y: 550):
   - Left: Redis Queue (X: 100), CeleryWorker (X: 300), Venice AI (X: 550)
   - Middle: Scheduled Scraping (X: 50), CeleryBeat (X: 250)
   - Right: ScrapingTasks (X: 700), ProductData (X: 900)
9. **Place layer 7** (Y: 750): Frontend (center-left, X: 350), Build Display (center-left, X: 350)
10. **Draw main flow** (central vertical path with right angles):
    - User → BuilderService → FeatureExtractor → ScoringEngine → Mapper → DatabaseService → PostgreSQL → Response Handler → Frontend → Display
11. **Draw AI branch** (left side with curves):
    - BuilderService → Redis Queue → CeleryWorker → Venice AI → BuilderService (feedback)
12. **Draw Scraping branch** (right side with curves):
    - Scheduled Scraping → CeleryBeat → Redis Queue → CeleryWorker → ScrapingTasks → ProductData → PostgreSQL
13. **Apply colors** (Blue for HTTP, Green for data, Orange for async, Purple for external)
14. **Add labels** to all connections

### See File: `04-component-interaction-visio.md`

---

## Diagram 5: Database Schema (ER)

### Summary
Entity-Relationship diagram showing 8 entities with 7 relationships and cardinality notation.

### Key Specifications
- **Canvas**: 1200 × 900px
- **Entities**: 8 (2 main - USER, PRODUCT; 5 related - BUILD, BUILD_COMPONENT, CHAT, CHAT_MESSAGE; 7 subtypes)
- **Relationships**: 7 (mostly One-to-Many)
- **Special features**: Generalization (subtype hierarchy for PRODUCT)

### Step-by-Step Recreation

1. **Create canvas** (1200×900)
2. **Place entities** (centered positioning):
   - USER (X: 200, Y: 100)
   - BUILD (X: 100, Y: 350)
   - BUILD_COMPONENT (X: 300, Y: 500)
   - PRODUCT (X: 500, Y: 350)
   - CHAT (X: 800, Y: 100)
   - CHAT_MESSAGE (X: 900, Y: 350)
   - 7 PRODUCT Subtypes (Y: 650, spread across X: 350-950)

3. **Create entity boxes** (for each entity):
   - Width: ~180px, Height: varies (140px minimum)
   - Header: Entity name in bold
   - Body: Attributes listed with type
   - PK attributes: bold with "PK" indicator
   - FK attributes: labeled "FK" with reference

4. **Draw relationship lines** from USER:
   - To BUILD: "creates" (1-to-many, solid line with crow's foot)
   - To CHAT: "has" (1-to-many, solid line with crow's foot)

5. **Draw relationship lines** from BUILD:
   - To BUILD_COMPONENT: "contains" (1-to-many)
   - To CHAT: "discussed_in" (optional, dashed line)

6. **Draw relationship lines** from BUILD_COMPONENT:
   - To PRODUCT: "uses" (many-to-1)

7. **Draw generalization** from PRODUCT to 7 subtypes:
   - Single line from PRODUCT down to junction point
   - 7 lines radiating from junction to each subtype box
   - Triangle indicator at junction (pointing to PRODUCT)

8. **Draw CHAT relationships**:
   - To CHAT_MESSAGE: "contains" (1-to-many)

9. **Apply cardinality notation**:
   - One side: Single vertical line |
   - Many side: Crow's foot <
   - Optional side: Circle ○
   - Example: |────────<

10. **Add relationship labels** (centered on connectors)
11. **Optional**: Add constraint boxes (gray background) for FK rules and unique constraints

### See File: `05-database-schema-visio.md`

---

## Diagram 6: Authentication & Security Flow

### Summary
Detailed sequence diagram showing login, request authorization, and logout flows with 5 swim lanes.

### Key Specifications
- **Canvas**: 1000 × 1200px
- **Swim lanes**: 5 (User, Frontend Auth, Backend Auth, PostgreSQL, Redis Rate Limit)
- **Messages**: 23 steps across 3 phases (Login, Request Auth, Logout)
- **Special features**: Activation boxes, self-arrows, security annotations

### Step-by-Step Recreation

1. **Create canvas** (1000×1200)
2. **Draw 5 vertical lifelines** (dashed lines at X: 80, 220, 360, 500, 640)
3. **Place 5 actor boxes** at top (Y: 30):
   - User (person icon)
   - Frontend Auth (box)
   - Backend Auth (box)
   - PostgreSQL (cylinder)
   - Redis Rate Limit (cylinder)

4. **Draw Phase 1 messages** (LOGIN, Y: 80-200):
   - User → Frontend: "Enter Username + Password"
   - Frontend → Backend: "POST /api/auth/login"
   - Backend → Redis: "Check Rate Limit"
   - Redis → Backend: "Limit OK?" (dashed response)

5. **Draw Phase 2 messages** (VERIFICATION, Y: 250-500):
   - Backend → PostgreSQL: "Query User"
   - PostgreSQL → Backend: "User Record" (dashed)
   - Backend self: "Verify Password (bcrypt)"
   - Backend self: "Generate JWT Token"
   - Backend → Redis: "Store Token"
   - Backend → Frontend: "Return JWT + User Info" (dashed)
   - Frontend self: "Save Token to localStorage"

6. **Draw Phase 3 messages** (REQUEST AUTH, Y: 650-1050):
   - User → Frontend: "Make API Request"
   - Frontend → Backend: "Include Bearer Token in Header"
   - Backend self: "Verify JWT (sig & expiry)"
   - Backend → Redis: "Check Blacklist"
   - Redis → Backend: "Blacklist status" (dashed)
   - Backend → PostgreSQL: "Query User (Verify Active)"
   - PostgreSQL → Backend: "User status" (dashed)
   - Backend → Frontend: "✅ Request Allowed" (dashed)

7. **Draw Phase 4 messages** (LOGOUT, Y: 1080-1200):
   - User → Frontend: "Logout"
   - Frontend → Backend: "POST /api/auth/logout"
   - Backend → Redis: "Add Token to Blacklist"
   - Backend → Frontend: "✅ Logged Out" (dashed)

8. **Create activation boxes** (small rectangles on lifelines):
   - At steps 3-4 (Rate check)
   - At steps 5-6 (User query)
   - At steps 7-8 (Auth process)
   - At steps 15-16 (Blacklist check)
   - At steps 17-18 (Status check)

9. **Add phase separator lines** (horizontal, light gray, thin):
   - Between Phase 1 and 2
   - Between Phase 2 and 3
   - Between Phase 3 and 4

10. **Add security control annotations** (gray boxes with italic text):
    - Step 3: "Prevent brute force attacks"
    - Step 7: "bcrypt with salt"
    - Step 8: "HS256 algorithm"
    - Step 14: "Verify exp claim in JWT"
    - Step 15: "Check revoked tokens"
    - Step 17: "Verify user is active"

11. **Apply colors**:
    - Blue arrows: Requests/HTTP
    - Dashed arrows: Responses
    - Orange: Rate limiting/Redis operations
    - Green: Database operations

### See File: `06-authentication-security-visio.md`

---

## Universal Design Standards

### Component Styles

**Boxes (Processes, Services)**
- Shape: Rectangle with rounded corners (optional: 0.1" radius)
- Width: 100-300px (varies by context)
- Height: 60px (standard) or scale with content
- Border: Solid black, 1.5pt
- Fill: Light color (blue #E6F2FF, green #E6FFE6, yellow #FFFFE6)
- Text: Arial 10pt, bold, centered, black

**Cylinders (Databases)**
- Shape: Cylinder (3D effect)
- Width: 100-120px
- Height: 80-100px
- Border: Solid black, 1.5pt
- Fill: Light blue-green (#D4F1D4)
- Text: Arial 10pt, bold, centered, white or black

**Clouds (External Services)**
- Shape: Cloud
- Width: 120-140px
- Height: 60-80px
- Border: Solid black, 1.5pt
- Fill: Light purple (#F0E6FF)
- Text: Arial 10pt, bold, centered, black

**People (Actors)**
- Shape: Person (stick figure or icon)
- Width: 60px
- Height: 60px
- Fill: Light gray (#E8E8E8)

**Diamonds (Decisions)**
- Shape: Diamond (rotated square)
- Width/Height: 60-80px
- Border: Solid black, 1.5pt
- Fill: Light yellow (#FFFFCC)
- Text: Arial 9pt, centered, black

### Connector Styles

**Primary Flow (Solid Blue)**
- Line: Solid, 1.5pt
- Color: Blue (#0066CC)
- End: Filled triangle arrow →
- Use: Frontend-backend communication, primary requests

**Database Operations (Solid Green)**
- Line: Solid, 1.5pt
- Color: Green (#00AA00)
- End: Filled triangle arrow →
- Use: Database queries, inserts, updates

**Queue/Async Operations (Solid Orange)**
- Line: Solid, 1.5pt
- Color: Orange (#FF9933)
- End: Filled triangle arrow →
- Use: Redis operations, async tasks, queueing

**External Services (Solid Purple)**
- Line: Solid, 1.5pt
- Color: Purple (#9933CC)
- End: Filled triangle arrow →
- Use: API calls to external services

**Error/Rejection (Solid Red)**
- Line: Solid, 1.5pt
- Color: Red (#CC0000)
- End: Filled triangle arrow →
- Use: Negative paths, failures, rejections

**Responses/Returns (Dashed Black)**
- Line: Dashed, 1.5pt (dash: 5px, gap: 5px)
- Color: Black
- End: Open triangle or line ⇢
- Use: Responses, return values, asynchronous notifications

**Internal/Self Processing (Solid Gray)**
- Line: Solid, 1.5pt
- Color: Gray (#666666)
- Shape: Semi-circle (self-loop)
- End: Arrow pointing back to source
- Use: Internal methods, calculations, processing

### Text Label Styles

**Component Labels**
- Font: Arial 10pt, bold
- Color: Black
- Background: None
- Alignment: Center
- Padding: 5px

**Connection Labels**
- Font: Arial 9pt, regular weight
- Color: Black
- Background: White rectangle (rounded, 2px padding)
- Alignment: Center
- Position: On connector or above/below

**Entity Attributes (ER Diagram)**
- Font: Arial 8pt, regular weight
- Color: Black
- Background: None
- Format: `attribute_name: TYPE`
- PK attributes: bold or with "PK" indicator

**Annotations/Notes**
- Font: Arial 8pt, italic
- Color: Gray
- Background: Light gray rectangle (2px padding)
- Format: Short descriptive text (1-2 lines max)

---

## Color Reference Chart

```
Primary Colors (HTTP/Frontend):
  RGB: 0, 102, 204     HEX: #0066CC    Name: Bright Blue

Database Colors:
  RGB: 0, 170, 0       HEX: #00AA00    Name: Bright Green

Async/Queue Colors:
  RGB: 255, 153, 51    HEX: #FF9933    Name: Dark Orange

External Service Colors:
  RGB: 153, 51, 204    HEX: #9933CC    Name: Purple

Error Colors:
  RGB: 204, 0, 0       HEX: #CC0000    Name: Dark Red

Component Fills:
  User/Frontend:       RGB: 230, 242, 255   HEX: #E6F2FF
  Services:            RGB: 230, 255, 230   HEX: #E6FFE6
  External:            RGB: 240, 230, 255   HEX: #F0E6FF
  Subtypes:            RGB: 245, 245, 245   HEX: #F5F5F5
  Callouts/Notes:      RGB: 232, 232, 232   HEX: #E8E8E8
```

---

## Tips for Clean Recreation

1. **Use Visio grids/guides**: Enable View → Grid & Guides for snapping
2. **Align components**: Use Format → Align → Left/Right/Top/Bottom/Center
3. **Distribute evenly**: Use Format → Distribute for consistent spacing
4. **Connector routing**: Use connectors with "Right Angle" or "Curved" routing style
5. **Group related items**: Select items → Format → Group to move together
6. **Use layers/pages**: Create separate Visio pages for each diagram
7. **Apply styles**: Create custom styles/themes for consistency
8. **Zoom appropriately**: 75-100% zoom while working for best precision

---

## Files in This Guide

```
visio-guides/
├── 01-system-architecture-visio.md      (22 components, 6 layers)
├── 02-data-flow-visio.md                (15 components, 5 columns)
├── 03-ai-build-sequence-visio.md        (7 lanes, 24 messages)
├── 04-component-interaction-visio.md    (18 components, 7 layers)
├── 05-database-schema-visio.md          (8 entities, 7 relationships)
├── 06-authentication-security-visio.md  (5 lanes, 23 messages)
└── README.md                             (THIS FILE)
```

---

## Getting Started

**Start with Diagram 1 (System Architecture)** - it provides the best overview and reference for all other diagrams.

**Then proceed to:**
1. Diagram 2 (Data Flow) - shows flow through architecture
2. Diagram 3 (AI Build Sequence) - most complex, but most detailed
3. Diagram 4 (Component Interaction) - simplified variant of Diagram 3
4. Diagram 5 (Database Schema) - entity relationships
5. Diagram 6 (Auth Security) - important for understanding security

Each subsequent diagram builds on understanding from previous ones.

---

## Questions & Adjustments

**If components don't fit**: Increase canvas size by 10-15% per dimension

**If connections cross too much**: Reorganize component positions or use connector routing options

**If text overlaps**: Reduce font size by 1pt or increase component box size

**If unclear connections**: Add connection labels or use color coding more distinctly

---

**Total Estimated Recreation Time**: 8-10 hours per diagram (beginner), 2-3 hours per diagram (experienced Visio user)

**Recommended tools**: Microsoft Visio 2019+, or online alternative (draw.io, LucidChart) that supports similar notation
