# Experiment 7 — UML Structural Diagrams

## System structure

The architecture diagram is in [architecture.mmd](../diagrams/architecture.mmd). It shows the browser shell and JavaScript client calling Flask routes, the authorization/validation layer, and SQLite persistence. The design is a single deployable application with clear logical boundaries, not a distributed microservice system.

The [UML class diagram](../diagrams/classes.mmd) models the principal domain classes, responsibilities, and associations. The [ER diagram](../diagrams/erd.mmd) shows the relational persistence model used by SQLite.

## Class responsibilities

| Class / entity | Responsibility | Key relationships |
|---|---|---|
| User | Account identity and role | One user owns many orders; user may create status events |
| MenuItem | Current menu name, category, price, availability and active flag | Referenced by order lines; current menu can change without rewriting snapshots |
| Order | Public pickup code, owner, current status, total, pickup hint and note | Has one or more OrderItems and status events |
| OrderItem | Quantity and immutable item/price snapshot | Belongs to exactly one Order; may reference a MenuItem |
| OrderEvent | Timestamped status message and actor | Belongs to one Order; optionally references a User |
| CanteenService | Application service boundary for menu, order, status and dashboard operations | Coordinates entities and persistence; represented by Flask route/service logic |
| SQLiteRepository | Reads/writes entities and runs transactions | Implements persistence boundary over SQLite tables |

`CanteenService` and `SQLiteRepository` are logical design roles; the current prototype implements them through Flask route functions and SQLite helper calls in `app.py`. They are not separate deployed classes/modules yet.

## Relationships and multiplicities

- User 1 — 0..* Order: a student may place many orders; each order has one owner.
- Order 1 — 1..* OrderItem: a valid placed order contains one or more lines.
- MenuItem 0..1 — 0..* OrderItem: an item may be referenced by historical lines, but snapshots remain readable if the item is archived.
- Order 1 — 1..* OrderEvent: initial placement creates an event and each valid transition adds one.
- User 0..1 — 0..* OrderEvent: an event can have an actor; the initial session/system event may be nullable in the schema.

## Structural design checks

- Money is stored as integer paise to avoid floating-point totals.
- Current menu values and historical line snapshots are kept separate.
- Role is stored with the user and checked at the API boundary.
- The state vocabulary is constrained in the schema and transitions are validated in application logic.
- The diagrams describe current prototype scope; add revisions if the fieldwork changes pickup or inventory rules.
