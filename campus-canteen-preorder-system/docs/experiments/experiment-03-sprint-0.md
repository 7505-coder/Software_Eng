# Experiment 3 — Agile Simulation: Sprint 0

## Sprint 0 goal

Prepare the team and technical foundation so Sprint 1 can deliver an integrated menu slice. This is a simulation plan; update the board, dates, assignments, and capacity with the team's actual lab evidence before submission.

**Proposed duration:** 1 week.  
**Sprint goal:** agree the MVP boundary, confirm the local development path, and make the first backlog items ready.  
**Proposed working agreements:** keep the main branch runnable, review changes before integration, raise blockers early, and write acceptance criteria before coding.

## Roles to assign with the team

| Role | Responsibility | Actual member assignment |
|---|---|---|
| Product representative | Clarifies student/canteen outcomes and orders backlog | To be agreed by team |
| Scrum facilitator | Runs planning/review and tracks blockers | To be agreed by team |
| Developers | Implement frontend, backend, data and integration | Team members to record actual split |
| Test/documentation owner | Keeps cases, evidence and lab record aligned | To be agreed by team |

These are role slots, not assignments inferred from the roster.

## Initial product backlog

Story-point values are relative planning estimates for the simulation, not elapsed hours.

| ID | User story | Priority | Points | Acceptance summary |
|---|---|---:|---:|---|
| US-01 | As a student, I can browse the current menu so I can choose food | Must | 5 | Active items show name, category, price, and availability |
| US-02 | As a student, I can search and filter menu items | Should | 3 | Search is case-insensitive; category filter can be cleared |
| US-03 | As a student, I can edit a cart and submit an order | Must | 8 | Quantities are bounded; server recomputes total; unavailable items fail clearly |
| US-04 | As a student, I can see my order status | Must | 5 | Only my orders are returned; latest state is visible |
| US-05 | As staff, I can manage the preparation queue | Must | 8 | Staff can perform only allowed status transitions |
| US-06 | As an administrator, I can maintain menu items | Should | 5 | Add, availability update, and archive actions are role-protected |
| US-07 | As a manager, I can see today's queue summary | Could | 3 | Dashboard counts orders, active/ready queue, and completed sales |
| US-08 | As a user, I can sign in under a role | Must | 8 | Invalid credentials fail; student cannot call staff/admin actions |
| **Total** |  |  | **45** | Planned backlog; do not treat as measured velocity |

## Readiness and quality agreements

**Definition of Ready:** a story has a named user, testable acceptance criteria, known dependencies, and no unresolved question that blocks implementation.  
**Definition of Done:** integrated code, server-side validation, access control where needed, test evidence, updated docs, and a demo path.  
**Proposed sprint events:** planning and story refinement (start); brief daily sync; working demo and retrospective (end).

## Sprint 0 checklist and evidence slots

- [ ] Team confirms role assignments and availability.
- [ ] Repository and Python environment run on every contributor's machine.
- [ ] Initial schema and order-state vocabulary reviewed.
- [ ] Board snapshot and actual meeting date attached as Annexure 3A.
- [ ] Actual blockers, decisions, and carry-over tasks recorded below.

**Board evidence:** `[Attach dated screenshot or photograph here]`  
**Actual dates / participants / decisions:** `[Complete from the team's real Sprint 0 session]`  
**Sprint 0 outcome:** `[Record completed items and carry-over items after the session]`
