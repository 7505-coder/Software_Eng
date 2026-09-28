# Experiment 5 — Software Requirements Specification

**Project:** SE-01 Campus Canteen Pre-Order System  
**Document state:** Working baseline for the course prototype; stakeholder approval and revision date are to be completed by the team.  
**Structure:** IEEE-style SRS sections aligned with the requirements-engineering guidance in ISO/IEC/IEEE 29148:2018. IEEE lists the 2018 edition as an active standard and describes requirements information items and life-cycle requirements engineering. See [IEEE Standards Association](https://standards.ieee.org/ieee/29148/6937/).

## 1. Introduction

### 1.1 Purpose

This SRS defines the functional and quality requirements for a single-campus canteen pre-order prototype. It provides a reviewable baseline for design, implementation, and test-case traceability. It does not claim that proposed workflow assumptions have been confirmed by fieldwork.

### 1.2 Scope

Students browse the active menu, see item availability, build a cart, place pickup orders, and view status. Canteen staff manage the order queue and progress orders through controlled states. Administrators maintain menu entries and see a basic daily dashboard. The prototype uses Flask, a same-origin HTML/CSS/JavaScript client, and SQLite. Payment is collected at pickup; no payment credentials are handled.

### 1.3 Terms

**Order:** one student's pickup request and its immutable item/price snapshots. **Availability:** whether a menu item may be ordered now. **Status event:** a timestamped record of an order-state transition. **Ready notification:** an in-page notice when polling detects the order has become ready; it is not an SMS or push notification.

### 1.4 References

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*, IEEE Standards Association record: <https://standards.ieee.org/ieee/29148/6937/>.
- Project artifacts: Experiments 1–4 and the diagrams in `docs/diagrams/`.

## 2. Overall description

### 2.1 Product perspective

The product is a small standalone web application for one canteen. The browser sends same-origin JSON requests to Flask. Flask validates identity, role, data, and state changes; SQLite stores normalized records. The client polls status while the page is open. No external campus identity, point-of-sale, inventory, payment, or messaging system is integrated.

### 2.2 User classes

| User class | Capabilities |
|---|---|
| Student | Register/sign in, view menu, place order, view own order history/status |
| Canteen staff | View queue and student pickup details, progress/cancel eligible orders, view dashboard |
| Administrator | Staff capabilities plus add/edit availability/archive menu items |
| Visitor | Browse menu and availability before signing in |

### 2.3 Operating environment and interfaces

The prototype targets Python 3.10+, Flask 3.x, SQLite, and a modern browser with JavaScript enabled. The browser interface is responsive and uses JSON endpoints under `/api`. Data transfer stays on the local origin. The default deployment uses `127.0.0.1:5000`; a shared deployment requires HTTPS and a production WSGI server.

### 2.4 Constraints, assumptions, dependencies

- One canteen and one local SQLite database are in scope.
- Students pay at pickup; online payment is out of scope.
- Staff and admin accounts are provisioned by the demo seed; student registration always creates the student role.
- A short pickup-time string is informational. The prototype does not reserve kitchen capacity or guarantee an exact ready time.
- Menu availability is maintained by an administrator; automatic stock deduction is not implemented.
- Real lab dates, field findings, canteen policy, and stakeholder acceptance must be supplied by the team.

## 3. Specific requirements

Each requirement has a unique ID and a testable statement. Priority is Must, Should, or Could for the prototype.

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-01 | Must | The system shall allow a visitor to create a student account with name, campus email, and password; registration shall never assign staff/admin role. | TC-04, TC-16 |
| FR-02 | Must | The system shall authenticate a user and expose only actions allowed for that user's role. | TC-02, TC-03, TC-08 |
| FR-03 | Must | The system shall list active menu items with name, category, description, price, and availability. | TC-01 |
| FR-04 | Should | The system shall filter menu results by category and search text. | TC-01 |
| FR-05 | Must | The system shall let a student add/remove items and change quantities from 1 through 20 per item. | TC-05, TC-07 |
| FR-06 | Must | The server shall calculate the order total from stored menu prices and reject inactive or unavailable items at submission time. | TC-05, TC-06 |
| FR-07 | Must | The system shall persist an order, item-name/price snapshots, optional pickup slot, optional note, and initial pending event atomically. | TC-05 |
| FR-08 | Must | The system shall show a student only that student's orders, item lines, total, and status history. | TC-09 |
| FR-09 | Must | The student page shall refresh visible status while open and show an in-page notice when an order becomes ready. | TC-11 |
| FR-10 | Must | Staff shall view the active queue and update an order only along permitted state transitions. | TC-10 |
| FR-11 | Should | Staff shall cancel pending, accepted, or preparing orders; completed and cancelled orders cannot be reopened. | TC-10 |
| FR-12 | Must | An administrator shall add menu items and change an item's availability. | TC-12, TC-13 |
| FR-13 | Should | An administrator shall archive a menu item without deleting historical order snapshots. | TC-14 |
| FR-14 | Should | Staff and administrators shall see today's order, active, ready, and completed-sales summary. | TC-15 |
| FR-15 | Must | The system shall retain timestamped status events for order placement and staff transitions. | TC-05, TC-10 |

## 4. External interface requirements

- **User interface:** semantic labels, keyboard-operable controls, clear validation and role messages, responsive menu/cart/queue views.
- **Software interface:** same-origin HTTP JSON API. Mutating endpoints require the session CSRF token. Error responses include a human-readable `error` field.
- **Database interface:** SQLite with foreign keys enabled. Money is integer paise; order lines snapshot name and price.
- **Communications interface:** no external network service is required for the core workflow.

## 5. Non-functional requirements

| ID | Quality | Requirement / target | Verification method |
|---|---|---|---|
| NFR-01 | Security | Passwords shall be salted and hashed; authorization shall be checked server-side; state-changing API requests shall require CSRF token. | Code review and TC-02/03/08/16 |
| NFR-02 | Privacy | Students shall not read another student's orders. Collect only name/email needed for the prototype. | TC-09 and data review |
| NFR-03 | Integrity | Order totals shall be server-derived and a placed order shall keep item/price snapshots. | TC-05/06 and database inspection |
| NFR-04 | Reliability | A database transaction shall prevent partial order creation. SQLite foreign keys shall be enabled. | Failure-path checks and schema review |
| NFR-05 | Performance | On a classroom laptop with local SQLite and up to 50 menu items, menu/order API calls should complete within 2 seconds at the 95th percentile. Measure before claiming achieved. | Timed test in the target environment |
| NFR-06 | Usability | A first-time student should be able to find an item, add it, and submit an order using keyboard or touch. Validate with real users; no usability result is claimed yet. | Observed usability session |
| NFR-07 | Accessibility | Forms have visible labels, status has text as well as color, and core actions are keyboard reachable. | Manual keyboard and contrast review |
| NFR-08 | Maintainability | Routes, browser behavior, schema, and docs are separated; order state transitions are centralized and explicit. | Code review and change-impact exercise |
| NFR-09 | Portability | The application shall run on Python 3.10+ with Flask installed and a writable database directory. | Clean-environment startup |

## 6. Data and business rules

- Account roles are `student`, `staff`, and `admin`.
- Order states are `pending`, `accepted`, `preparing`, `ready`, `completed`, and `cancelled`.
- Allowed transitions: pending → accepted or cancelled; accepted → preparing or cancelled; preparing → ready or cancelled; ready → completed; completed/cancelled are terminal.
- Each line quantity is 1–20; an order has 1–30 submitted line entries; notes are limited to 300 characters.
- A placed order's total is the sum of integer unit-price snapshots multiplied by quantity.
- Historical order lines are retained when an item is archived.

## 7. Traceability and acceptance

| Requirement group | Design | Test cases |
|---|---|---|
| FR-01–02, NFR-01 | `users`, session endpoints, role decorators | TC-02, TC-03, TC-08, TC-16 |
| FR-03–04, FR-12–13 | `menu_items`, menu API and admin UI | TC-01, TC-12–14 |
| FR-05–07, FR-15 | `orders`, `order_items`, `order_events` | TC-05–07, TC-10 |
| FR-08–11 | student/staff order APIs and polling UI | TC-09–11 |
| FR-14 | dashboard API and staff view | TC-15 |

Acceptance requires the Must requirements to pass against the test plan, known limitations to be documented, and actual stakeholder review to be recorded. No approval signature is prefilled.
