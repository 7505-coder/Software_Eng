# Experiment 6 — Structured Modeling: DFD and Data Dictionary

## Data-flow model

The context diagram treats the application as one process and names its external actors and stores. The Level 1 decomposition separates identity/roles, menu browsing, order placement, staff processing, and reporting. Diagram sources are editable Mermaid files: [Context DFD](../diagrams/context.mmd) and [Level 1 DFD](../diagrams/dfd-level-1.mmd).

### Process descriptions

| Process | Input | Output | Validation / control |
|---|---|---|---|
| P1 Identity and access | Registration, login, session request | User role, session, CSRF token | Password hash verification; student-only self-registration; server-side role checks |
| P2 Browse menu | Search/category filters | Active items and availability | Active items only; unavailable state is shown |
| P3 Place and view order | Cart IDs/quantities, pickup slot, note | Order, snapshots, student history | Re-read availability and price inside a transaction; student sees own orders |
| P4 Process queue | Staff status change | Updated order and event | Enforce allowed state transition; actor must be staff/admin |
| P5 Maintain menu/report | Admin menu changes; dashboard request | Menu state and daily summary | Admin-only changes; archived rows retained for history |

## Data dictionary

SQLite stores monetary values in integer paise. Timestamps are ISO-8601 UTC strings. `PK` is primary key, `FK` is foreign key, `NN` is not null, and `UQ` is unique.

### USERS

| Field | Type | Constraints | Meaning |
|---|---|---|---|
| id | integer | PK | Internal account identifier |
| name | text | NN, 2–80 chars on registration | Display name |
| email | text | NN, UQ, normalized lowercase | Sign-in address |
| password_hash | text | NN | PBKDF2-HMAC-SHA256 encoded hash, never plaintext |
| role | text | NN, one of student/staff/admin | Authorization role |
| created_at | text | NN | Account creation time |

### MENU_ITEMS

| Field | Type | Constraints | Meaning |
|---|---|---|---|
| id | integer | PK | Menu item identifier |
| name | text | NN, 2–80 chars | Current menu name |
| description | text | NN, up to 240 chars | Short student-facing description |
| category | text | NN, 2–40 chars | Menu filter group |
| price_paise | integer | NN, >= 0 | Current price in paise |
| is_available | integer | NN, Boolean | Whether orders may be placed now |
| is_active | integer | NN, Boolean | Whether item is listed; 0 means archived |
| updated_at | text | NN | Latest menu edit time |

### ORDERS and ORDER_ITEMS

| Entity.field | Type | Constraints | Meaning |
|---|---|---|---|
| ORDERS.id | integer | PK | Internal order identifier |
| ORDERS.public_code | text | NN, UQ | Short pickup/reference code |
| ORDERS.user_id | integer | NN, FK → USERS.id | Owning student |
| ORDERS.status | text | NN, state check | Current workflow state |
| ORDERS.total_paise | integer | NN, >= 0 | Server-calculated total |
| ORDERS.pickup_slot | text | NN, max 40 | Optional pickup hint |
| ORDERS.note | text | NN, max 300 | Optional preparation note |
| ORDERS.created_at / updated_at | text | NN | Creation and latest transition time |
| ORDER_ITEMS.id | integer | PK | Order-line identifier |
| ORDER_ITEMS.order_id | integer | NN, FK → ORDERS.id, cascade delete | Parent order |
| ORDER_ITEMS.menu_item_id | integer | FK → MENU_ITEMS.id, nullable | Original item reference; may be unavailable later |
| ORDER_ITEMS.item_name | text | NN | Name snapshot at order time |
| ORDER_ITEMS.quantity | integer | NN, 1–20 | Ordered count |
| ORDER_ITEMS.unit_price_paise | integer | NN, >= 0 | Price snapshot at order time |

### ORDER_EVENTS

| Field | Type | Constraints | Meaning |
|---|---|---|---|
| id | integer | PK | Event identifier |
| order_id | integer | NN, FK → ORDERS.id | Order being changed |
| status | text | NN | State recorded for the event |
| message | text | NN | Human-readable status event |
| created_by | integer | FK → USERS.id, nullable | Student or staff actor |
| created_at | text | NN | Event timestamp |

## Data integrity and privacy

Foreign keys are enabled for each connection. Order creation reads the current item price and availability while holding a write transaction; it stores immutable line snapshots and commits order/event/lines together. Students can query only their own order records. Do not put real payment details or unnecessary identifiers into the database.
