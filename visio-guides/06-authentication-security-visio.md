# Visio: Authentication & Security Flow

## Canvas Size: 1000px × 1200px

## SWIM LANES (Vertical Columns)

```
┌──────────┬────────────┬────────────┬────────────┬────────────┐
│ LANE 1   │ LANE 2     │ LANE 3     │ LANE 4     │ LANE 5     │
│ (X: 80)  │ (X: 220)   │ (X: 360)   │ (X: 500)   │ (X: 640)   │
│ User     │ Frontend   │ Backend    │ PostgreSQL │ Redis      │
│          │ Auth       │ Auth       │            │ Rate Limit │
└──────────┴────────────┴────────────┴────────────┴────────────┘
```

## ACTOR/COMPONENT POSITIONING (Top Y: 30px)

| Lane | X Pos | Actor | Shape | Width |
|------|-------|-------|-------|-------|
| 1 | 80 | User | Person | 60 |
| 2 | 220 | Frontend Auth | Box | 100 |
| 3 | 360 | Backend Auth | Box | 100 |
| 4 | 500 | PostgreSQL | Cylinder | 100 |
| 5 | 640 | Redis Rate Limit | Cylinder | 100 |

## LIFELINES (Vertical Dashed Lines)

All lifelines run from Y: 60px to Y: 1150px at X positions: 80, 220, 360, 500, 640

## SEQUENCE FLOW (Top to Bottom, Y positions)

### Phase 1: LOGIN REQUEST (Y: 80-200)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 1 | 80 | User (1) | Frontend (2) | Enter Username + Password | Solid Arrow | User input |
| 2 | 130 | Frontend (2) | Backend (3) | POST /api/auth/login {username, password} | Solid Arrow | HTTPS |
| 3 | 180 | Backend (3) | Redis (5) | Check Rate Limit (IP Address) | Solid Arrow | Query |
| 4 | 230 | Redis (5) | Backend (3) | Limit OK? | Dashed Arrow | Response |

### Phase 2: USER VERIFICATION (Y: 250-350)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 5 | 280 | Backend (3) | PostgreSQL (4) | Query User (SELECT * WHERE username) | Solid Arrow | Query |
| 6 | 330 | PostgreSQL (4) | Backend (3) | User Record | Dashed Arrow | Response |

### Phase 3: PASSWORD & TOKEN (Y: 370-470)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 7 | 400 | Backend (3) | Backend (3) | Verify Password (bcrypt.verify()) | Self-arrow | Process |
| 8 | 450 | Backend (3) | Backend (3) | Generate JWT Token (User ID + Role) | Self-arrow | Process |
| 9 | 500 | Backend (3) | Redis (5) | Store Token (Blacklist Cache) | Solid Arrow | Store |

### Phase 4: LOGIN RESPONSE & STORAGE (Y: 520-600)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 10 | 550 | Backend (3) | Frontend (2) | Return JWT Token + User Info | Dashed Arrow | HTTPS Response |
| 11 | 600 | Frontend (2) | Frontend (2) | Save Token to localStorage | Self-arrow | Client storage |

### Phase 5: SUBSEQUENT API REQUEST (Y: 650-800)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 12 | 680 | User (1) | Frontend (2) | Make API Request | Solid Arrow | User action |
| 13 | 730 | Frontend (2) | Backend (3) | Include Bearer Token in Header | Solid Arrow | Authorization header |
| 14 | 780 | Backend (3) | Backend (3) | Verify JWT (signature & expiry) | Self-arrow | Cryptographic check |
| 15 | 830 | Backend (3) | Redis (5) | Check Blacklist (Token revoked?) | Solid Arrow | Query |
| 16 | 880 | Redis (5) | Backend (3) | Blacklist status | Dashed Arrow | Response |

### Phase 6: USER STATUS CHECK (Y: 920-1020)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 17 | 950 | Backend (3) | PostgreSQL (4) | Query User (Verify Active Status) | Solid Arrow | Query |
| 18 | 1000 | PostgreSQL (4) | Backend (3) | User status | Dashed Arrow | Response |
| 19 | 1050 | Backend (3) | Frontend (2) | ✅ Request Allowed | Dashed Arrow | Response |

### Phase 7: LOGOUT (Y: 1080-1150)

| Step | Y Pos | From Lane | To Lane | Message | Type | Notes |
|------|-------|-----------|---------|---------|------|-------|
| 20 | 1100 | User (1) | Frontend (2) | Logout | Solid Arrow | User action |
| 21 | 1130 | Frontend (2) | Backend (3) | POST /api/auth/logout | Solid Arrow | Request |
| 22 | 1160 | Backend (3) | Redis (5) | Add Token to Blacklist | Solid Arrow | Store |
| 23 | 1200 | Backend (3) | Frontend (2) | ✅ Logged Out | Dashed Arrow | Response |

## ACTIVATION BOXES (Processing Duration)

Place small vertical rectangles (20px wide × 30-50px height) on lifelines:

| Step | Lane | Y Range | Duration | Label |
|------|------|---------|----------|-------|
| 3-4 | Redis | 180-230 | 50px | Rate Check |
| 5-6 | Backend & PostgreSQL | 280-330 | 50px | User Query |
| 7-8 | Backend | 400-450 | 50px | Auth Process |
| 9 | Backend & Redis | 500-550 | 50px | Token Store |
| 15-16 | Backend & Redis | 830-880 | 50px | Blacklist Check |
| 17-18 | Backend & PostgreSQL | 950-1000 | 50px | Status Check |

## GROUPING BOXES (Optional, for visual clarity)

| Group | Y Range | Height | Label | Color | Lane Range |
|-------|---------|--------|-------|-------|-----------|
| LOGIN FLOW | 80-600 | 520 | Authentication | Light Blue | All |
| REQUEST AUTH | 650-1050 | 400 | Authorization | Light Green | All |
| LOGOUT | 1080-1200 | 120 | Session Termination | Light Red | All |

## ARROW SPECIFICATIONS

### Solid Arrows (Synchronous/Direct calls)
```
Line: Solid black, 1.5pt
Head: Filled triangle (→)
Used for: Requests, direct queries
Example: POST request, SELECT query
```

### Dashed Arrows (Responses/Returns)
```
Line: Dashed black, 1.5pt
Head: Open triangle or line (⇢)
Used for: Responses, return values
Example: API response, query result
```

### Self-Arrows (Internal processing)
```
Line: Solid black, 1.5pt
Shape: Semi-circle on right side of lifeline
Head: Arrow pointing right then left (↪)
Used for: Internal methods, calculations
Example: Password verification, JWT generation
```

## TIMING ANNOTATIONS

Add vertical reference lines with labels:
```
T0: User submits credentials
T1: Rate limit check
T2: Database query
T3: Password verification & token generation
T4: Token storage
T5: Login response
T6: Subsequent request with token
T7: Token validation
T8: Logout & token revocation
```

## SECURITY CONTROLS (Annotations)

Add small text boxes with gray background:
```
Security Checkpoints:
1. Rate Limiting (Redis, Step 3)
   "Prevent brute force attacks"

2. Password Hashing (Backend, Step 7)
   "bcrypt with salt"

3. JWT Signing (Backend, Step 8)
   "HS256 algorithm with SECRET_KEY"

4. Token Expiration (Backend, Step 14)
   "Verify exp claim in JWT"

5. Blacklist Verification (Redis, Step 15)
   "Check revoked tokens"

6. User Status Check (PostgreSQL, Step 17)
   "Verify user is active"

7. HTTPS Transport
   "All requests should be encrypted"
```

## POSITIONING GUIDELINES

### Swim Lane Widths
| Lane | Width | X Range |
|------|-------|---------|
| User | 120px | 20-140 |
| Frontend Auth | 120px | 160-280 |
| Backend Auth | 120px | 300-420 |
| PostgreSQL | 120px | 440-560 |
| Redis Rate Limit | 120px | 580-700 |

### Message Label Placement
- Position labels 5px above/below connectors
- Centered horizontally on connector
- White background box with padding
- Font: Arial 9pt

### Lifeline Dashes
- Dashed vertical lines (dash: 5px, gap: 5px)
- Light gray color (gray-50% or similar)
- Full height of canvas
- Should align with swim lane centers

## PHASE SEPARATORS (Optional)

Add horizontal dividing lines between major phases:
```
Phase 1 ↓ (Y: 240)  ─────────────────────────────
Phase 2 ↓ (Y: 360)  ─────────────────────────────
Phase 3 ↓ (Y: 510)  ─────────────────────────────
Phase 4 ↓ (Y: 630)  ─────────────────────────────
Phase 5 ↓ (Y: 1060) ─────────────────────────────
Phase 6 ↓ (Y: 1080) ─────────────────────────────
```

Lines should be light gray, thin (0.5pt), span all lanes.

## DECISION DIAMONDS (Optional)

For "Limit OK?" and similar decisions:
```
Shape: Diamond (rotated square)
Size: 60×60px
Position: Center of lane, at message Y position
Label: Question text (centered)
Yes/No labels on outgoing arrows
```
