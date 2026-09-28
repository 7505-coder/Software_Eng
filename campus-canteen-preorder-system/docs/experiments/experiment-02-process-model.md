# Experiment 2 — Process Model Selection and Increment Plan

## Selected model

Use an **iterative and incremental Agile process** with a short planning/review cycle. The team can demonstrate a small working slice early, receive feedback from students and canteen staff, and adjust menu, pickup, and queue details before the final build. Each increment ends with an integrated, reviewable application and acceptance checks.

Waterfall would make late feedback costly because field findings and availability rules are not yet verified. A throwaway prototype could clarify screens but would not ensure persistence, role control, or order-state correctness. The selected process keeps a working baseline while still using an explicit SRS, design, estimates, tests, and approval records.

## Increment plan

| Increment | Candidate duration | Deliverable | Exit / acceptance check |
|---|---:|---|---|
| 0 — Discovery and setup | 1 week | Charter, fieldwork plan, prioritized backlog, schema sketch, repo and Definition of Done | Stakeholders and open questions are listed; local app starts from a clean checkout |
| 1 — Menu and identity | 4 weeks | Student registration/sign-in, roles, menu browse/search/filter, availability display | Student sees active items and unavailable items cannot be added |
| 2 — Cart and ordering | 4 weeks | Cart, quantity validation, server-calculated total, order history | Valid order persists with item-price snapshots; invalid/unavailable order is rejected |
| 3 — Canteen operations | 4 weeks | Staff queue, controlled status transitions, status events, ready notification in page | Staff can move an order through allowed states; student sees updated state |
| 4 — Administration | 2 weeks | Menu add/edit/availability/archive, dashboard totals | Admin controls work; staff/student cannot access admin actions |
| 5 — Hardening and handover | 3 weeks | Regression checks, accessibility review, database backup notes, demo and viva | Required cases pass; known gaps and evidence placeholders are disclosed |

The six candidate increment durations total 18 weeks; Experiment 10 adds a two-week reserve to form the proposed 20-week baseline.

The durations are a proposed baseline, not a record of completed lab sessions. Experiment 10 derives a separate PERT/CPM forecast with contingency.

## Review cadence and control

- At the start of an iteration, select only backlog items that fit the team's capacity and record an owner and acceptance criteria.
- Hold a short daily coordination check during active implementation; record blockers and decisions.
- At iteration end, demonstrate the integrated increment, record stakeholder feedback, and update the backlog with a change rationale.
- Keep requirements, diagrams, test cases, source commits, and demo version traceable by the same requirement and test IDs.
- The instructor or product representative approves scope changes that affect the lab record or delivery date.

## Definition of Done

An item is done when the acceptance criteria are met; server-side validation and role checks exist where relevant; the change is integrated; focused automated or manual checks pass; the UI has a keyboard-accessible path; the docs and diagrams match the implementation; and known limitations are recorded. A screenshot or faculty signature is evidence only when it reflects the actual review.
