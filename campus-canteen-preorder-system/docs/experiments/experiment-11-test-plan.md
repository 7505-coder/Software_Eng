# Experiment 11 — Test Plan and Test Case Design

## Test plan

**Scope:** account creation/sign-in, role restrictions, menu browse/availability, cart and server-side order validation, order history and status transitions, menu administration, dashboard summary, and CSRF protection. External payment, campus SSO, email/SMS, and production load are out of scope.

**Levels:** focused function/API checks with Flask's test client; database persistence/integrity checks; manual browser workflow and keyboard/accessibility review. Test data uses the seeded demo users and a temporary SQLite database. A student order should never be tested against a live canteen database.

**Entry criteria:** dependencies installed; clean temporary DB initialized; demo seed present; current requirement IDs and test build identified. **Exit criteria:** all Must cases pass or have an approved defect disposition; no known role/data-integrity blocker; manual evidence and environment are recorded. Do not mark a case passed without observed evidence.

## Test cases

The `tests/test_app.py` automated suite covers the API and persistence paths. The expected outcomes below are the designed outcomes; execution results should be recorded from a real run and browser session.

**Automated result recorded 2026-09-28:** 13 `unittest` cases passed against temporary SQLite databases using Flask's test client. Covered: static page/assets, seeded menu/search, valid and invalid sign-in, CSRF rejection, student order persistence/server total, role restrictions, invalid ID/quantity, unavailable-item rejection without a partial order, student order isolation, complete status lifecycle, archived-item history, dashboard sales, admin menu controls, and student-only registration. Manual ready notification, keyboard/accessibility, peak-response timing, and stakeholder acceptance remain to be executed by the team.

| ID | Requirement | Scenario and input | Expected result | Execution result / evidence |
|---|---|---|---|---|
| TC-01 | FR-03/04 | Load menu, search an item, apply category filter | Active items show correct details; filters narrow results | Seed menu and search passed; category filter still needs a dedicated check |
| TC-02 | FR-02 | Sign in with valid student credentials | Student session established; student actions visible | Passed in automated student workflow tests |
| TC-03 | FR-02 | Sign in with wrong password | Generic 401 message; no session granted | Passed 2026-09-28 |
| TC-04 | FR-01 | Register valid name/email/password | Student account created and signed in | Passed 2026-09-28 |
| TC-05 | FR-05–07 | Submit an available item and quantity 2 | Order, event and item snapshot persist; total equals stored price × 2 | Passed 2026-09-28; server total and event checked |
| TC-06 | FR-06 | Submit an unavailable or archived item | Request rejected; no partial order is created | Unavailable item rejection and no-order result passed; archived-order submission remains to be tested |
| TC-07 | FR-05 | Submit quantity 0, 21, or malformed ID | Validation error; no order created | Quantity 21 and malformed ID path passed; quantity 0 remains to be tested |
| TC-08 | FR-02 | Student requests staff queue/dashboard/menu change | 403 response; data unchanged | Passed 2026-09-28 |
| TC-09 | FR-08 | Student A orders; student B requests order list | Student B receives only their own orders | Passed 2026-09-28 |
| TC-10 | FR-10/11 | Staff advances pending → accepted → preparing; tries pending → ready | Allowed transitions persist; skipped transition returns conflict | Full pending → accepted → preparing → ready → completed lifecycle passed; skipped transition rejected |
| TC-11 | FR-09 | Keep student order page open while staff marks ready | Poll sees ready state and announces it once | Manual browser evidence pending |
| TC-12 | FR-12 | Admin creates a valid menu item | Item appears with expected fields and price | Passed 2026-09-28 |
| TC-13 | FR-06/12 | Admin toggles availability; student submits a stale cart | Item remains visible as sold out; order rejected at server | Availability change and server rejection passed; browser sold-out display remains to be checked |
| TC-14 | FR-13 | Admin archives an item already referenced by an order | Item disappears from active menu; historical line snapshot remains | Passed: archived item is removed from active menu and order snapshot remains |
| TC-15 | FR-14 | Staff opens dashboard after orders complete | Today's counts and completed sales are returned | Passed: completed lifecycle total appears in dashboard sales |
| TC-16 | NFR-01 | Omit CSRF token or register with `role=admin` | Mutation is rejected without token; self-registration remains student | Both CSRF rejection and student-only registration passed |

## Defect and evidence log

| Defect ID | Test case | Observed result | Severity | Owner | Fix/build | Retest result |
|---|---|---|---|---|---|---|
| `[ID or none after actual run]` | `[TC]` | `[actual failure]` | `[critical/high/medium/low]` | `[member]` | `[revision]` | `[pass/fail/date]` |

Capture the command output for automated tests and screenshots or notes for manual checks. Redact student identifiers and do not use real credentials in attached screenshots.
