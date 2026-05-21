# Visio: Database Schema ER Diagram

## Canvas Size: 1200px × 900px

## ENTITY POSITIONING (Center: X: 600, Y: 450)

```
                    ┌─────────────────┐
                    │      USER       │
                    └─────────────────┘
                         /  \
                        /    \
        ┌──────────────┴────┬─┴──────────────┐
        │                   │                │
        │                   │                │
    ┌───────────┐      ┌─────────┐    ┌──────────┐
    │  BUILD    │      │  CHAT   │    │   OTHER  │
    └─────┬─────┘      └────┬────┘    └──────────┘
          │                 │
          │                 │
    ┌─────────────────┐ ┌────────────────┐
    │ BUILD_COMPONENT │ │ CHAT_MESSAGE   │
    └────────┬────────┘ └────────────────┘
             │
             │
         ┌───────────┐
         │ PRODUCT   │
         └─────┬─────┘
         /  /  |  \  \
        /  /   |   \  \
      CPU GPU RAM STORAGE PSU MOTHERBOARD COOLING
```

## ENTITY DEFINITIONS & POSITIONING

### USER Entity (X: 200, Y: 100)
| Attribute | Type | Key | Notes |
|-----------|------|-----|-------|
| user_id | INT | PK | Auto-increment |
| username | VARCHAR(50) | UQ | Unique constraint |
| email | VARCHAR(100) | UQ | Unique constraint |
| password_hash | VARCHAR(255) | | Bcrypt hash |
| created_at | TIMESTAMP | | Auto-generated |

### BUILD Entity (X: 100, Y: 350)
| Attribute | Type | Key | Notes |
|-----------|------|-----|-------|
| build_id | INT | PK | Auto-increment |
| user_id | INT | FK | References USER |
| name | VARCHAR(255) | | Build name |
| description | TEXT | | Build notes |
| total_cost | FLOAT | | Sum of components |
| total_power | INT | | PSU wattage |
| created_at | TIMESTAMP | | Auto-generated |

### BUILD_COMPONENT Entity (X: 300, Y: 500)
| Attribute | Type | Key | Notes |
|-----------|------|-----|-------|
| component_id | INT | PK | Auto-increment |
| build_id | INT | FK | References BUILD |
| product_id | INT | FK | References PRODUCT |
| quantity | INT | | Component count |
| source | VARCHAR(100) | | Where bought |
| added_at | TIMESTAMP | | Auto-generated |

### PRODUCT Entity (X: 500, Y: 350)
| Attribute | Type | Key | Notes |
|-----------|------|-----|-------|
| product_id | INT | PK | Auto-increment |
| name | VARCHAR(255) | | Product name |
| category | VARCHAR(50) | | CPU, GPU, RAM, etc |
| price | FLOAT | | Current price |
| source | VARCHAR(100) | | Telemart, etc |
| specs | TEXT | | JSON specs |
| metadata | TEXT | | Additional data |
| scraped_at | TIMESTAMP | | When scraped |

### PRODUCT SUBTYPES (Category-based)
| Subtype | Category Value | X Position | Y Position |
|---------|---|---|---|
| CPU | "cpu" | 350 | 650 |
| GPU | "gpu" | 450 | 650 |
| RAM | "ram" | 550 | 650 |
| STORAGE | "storage" | 650 | 650 |
| PSU | "psu" | 750 | 650 |
| MOTHERBOARD | "motherboard" | 850 | 650 |
| COOLING | "cooling" | 950 | 650 |

### CHAT Entity (X: 800, Y: 100)
| Attribute | Type | Key | Notes |
|-----------|------|-----|-------|
| chat_id | INT | PK | Auto-increment |
| user_id | INT | FK | References USER |
| build_id | INT | FK | References BUILD (optional) |
| created_at | TIMESTAMP | | Auto-generated |

### CHAT_MESSAGE Entity (X: 900, Y: 350)
| Attribute | Type | Key | Notes |
|-----------|------|-----|-------|
| message_id | INT | PK | Auto-increment |
| chat_id | INT | FK | References CHAT |
| role | VARCHAR(20) | | "user" or "assistant" |
| content | TEXT | | Message text |
| created_at | TIMESTAMP | | Auto-generated |

## RELATIONSHIPS DEFINITION

### Relationship 1: USER ↔ BUILD
```
Type: One-to-Many
From: USER.user_id (PK)
To: BUILD.user_id (FK)
Cardinality: 1 ─ ∞
Label: "creates"
Delete Rule: CASCADE
Connector Type: Solid line
Line Style: |─ … ─<
```

### Relationship 2: BUILD ↔ BUILD_COMPONENT
```
Type: One-to-Many
From: BUILD.build_id (PK)
To: BUILD_COMPONENT.build_id (FK)
Cardinality: 1 ─ ∞
Label: "contains"
Delete Rule: CASCADE
Connector Type: Solid line
Line Style: |─ … ─<
```

### Relationship 3: BUILD_COMPONENT ↔ PRODUCT
```
Type: Many-to-One
From: BUILD_COMPONENT.product_id (FK)
To: PRODUCT.product_id (PK)
Cardinality: ∞ ─ 1
Label: "uses"
Delete Rule: NO ACTION
Connector Type: Solid line
Line Style: >─ … ─|
```

### Relationship 4: PRODUCT → SUBTYPES
```
Type: Generalization (Category-based)
Discriminator: PRODUCT.category
Values: cpu, gpu, ram, storage, psu, motherboard, cooling
Label: "is_a"
Connector Type: Solid line with triangle
Line Style: ─ … ┬ ─ … ─ △
```

### Relationship 5: USER ↔ CHAT
```
Type: One-to-Many
From: USER.user_id (PK)
To: CHAT.user_id (FK)
Cardinality: 1 ─ ∞
Label: "has"
Delete Rule: CASCADE
Connector Type: Solid line
Line Style: |─ … ─<
```

### Relationship 6: CHAT ↔ CHAT_MESSAGE
```
Type: One-to-Many
From: CHAT.chat_id (PK)
To: CHAT_MESSAGE.chat_id (FK)
Cardinality: 1 ─ ∞
Label: "contains"
Delete Rule: CASCADE
Connector Type: Solid line
Line Style: |─ … ─<
```

### Relationship 7: BUILD ↔ CHAT (Optional)
```
Type: One-to-Many (Optional)
From: BUILD.build_id (PK)
To: CHAT.build_id (FK)
Cardinality: 1 ─ ∞ (optional)
Label: "discussed_in"
Delete Rule: SET NULL
Connector Type: Dashed line
Line Style: |─ ○ … ○ ─<
Indicator: Dashed line shows optional FK
```

## CONNECTION ROUTING

```
USER (200, 100)
  ├─ "creates" line ↓ to BUILD (100, 350)
  │  └─ Line curves down-left
  │
  └─ "has" line ↓ to CHAT (800, 100)
     └─ Line curves down-right

BUILD (100, 350)
  ├─ "contains" line → to BUILD_COMPONENT (300, 500)
  │  └─ Line angles down-right
  │
  └─ "discussed_in" line ⇢ to CHAT (800, 100) [Optional, dashed]
     └─ Dashed line curves right and up

BUILD_COMPONENT (300, 500)
  └─ "uses" line ↓ to PRODUCT (500, 350)
     └─ Line angles down-right

PRODUCT (500, 350)
  ├─ "is_a" lines ↓ to each SUBTYPE (Y: 650)
  │  ├─ to CPU (350, 650)
  │  ├─ to GPU (450, 650)
  │  ├─ to RAM (550, 650)
  │  ├─ to STORAGE (650, 650)
  │  ├─ to PSU (750, 650)
  │  ├─ to MOTHERBOARD (850, 650)
  │  └─ to COOLING (950, 650)
  │  └─ Lines fan out downward
  │
  └─ Implicit relationship for categories

CHAT (800, 100)
  ├─ "contains" line ↓ to CHAT_MESSAGE (900, 350)
  │  └─ Line curves down-right
  │
  └─ Relationship with BUILD (optional, from BUILD → CHAT)
```

## ENTITY BOX SPECIFICATIONS

### Standard Entity Box
```
┌─────────────────────┐
│    ENTITY_NAME      │  (Header: Bold, centered, height: 20px)
├─────────────────────┤
│ PK user_id: INT     │  (Primary Key highlighted in bold, height: 16px per line)
│    username: VARCHAR│
│    email: VARCHAR   │  (Regular attributes, normal weight)
│    password: VARCHAR│
│    created_at: TS   │
└─────────────────────┘

Width: 180px
Min Height: 140px (scales with attributes)
Padding: 10px internal
Background: Light blue (#E6F2FF) for USER, light green for PRODUCT, etc.
Border: Solid black, 1.5pt
```

### Subtype Entity Box (Smaller)
```
┌──────────┐
│   CPU    │
├──────────┤
│ category │
│= "cpu"   │
└──────────┘

Width: 100px
Height: 80px
Background: Very light gray (#F5F5F5)
Border: Solid black, 1pt
```

## RELATIONSHIP LINE SPECIFICATIONS

### One-to-Many Relationship
```
Line Style: Solid black, 1.5pt
End 1 (One side): Single vertical line |
End Many: Crow's foot < or three lines ⟨
Label Position: Center of line, offset 5px above
Example: |─────────────<
```

### Optional Relationship (FK can be NULL)
```
Line Style: Dashed black, 1.5pt
End 1 (One side): Circle ○ (open)
End Many: Crow's foot < or circle/crow's foot
Label Position: Center of line
Example: |─ ○ ────────<
```

### Generalization (Subtype)
```
Line Style: Solid black, 1.5pt
End (Parent): Triangle △ pointing to parent
End (Children): Lines connect to triangle junction
Label: "is_a" positioned at junction
Example: Multiple lines converge to △ at parent
```

## LABEL SPECIFICATIONS

All relationship labels:
- Font: Arial, 10pt, normal weight
- Background: White rounded rectangle
- Padding: 2px
- Position: Center of connector
- Examples:
  - "creates"
  - "contains"
  - "uses"
  - "has"
  - "is_a"
  - "discussed_in"

## NOTES & CONSTRAINTS

Add text boxes (small, gray background) for:
```
1. FK Constraints:
   "BUILD.user_id → USER.user_id (CASCADE)"
   "BUILD_COMPONENT.build_id → BUILD.build_id (CASCADE)"
   "CHAT.build_id → BUILD.build_id (SET NULL, optional)"

2. Unique Constraints:
   "USER: username UNIQUE"
   "USER: email UNIQUE"

3. Indexes:
   "BUILD: INDEX (user_id)"
   "BUILD_COMPONENT: INDEX (build_id, product_id)"
```

## COLOR CODING (Optional)

- **User Entity**: Light blue (#E6F2FF)
- **Build Entities**: Light green (#E6FFE6)
- **Product/Chat Entities**: Light yellow (#FFFFE6)
- **FK Relationships**: Orange line or label
- **PK Attributes**: Bold text
- **Subtype hierarchy**: Light gray boxes
