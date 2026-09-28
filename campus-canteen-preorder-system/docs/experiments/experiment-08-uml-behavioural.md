# Experiment 8 — UML Behavioural Diagrams and Design Quality

## Behavioural models

- [Order placement sequence](../diagrams/sequence-order.mmd) shows the browser, Flask application, session/role check, SQLite transaction, and response.
- [Order activity diagram](../diagrams/activity-order.mmd) shows validation branches, including unavailable item rejection.
- [Order state machine](../diagrams/order-state.mmd) shows allowed status transitions and terminal states.
- [Use case model](../diagrams/use-cases.mmd) relates visitor, student, staff, and administrator goals to system operations.

## Design quality review

| Quality attribute | Design choice | Evidence / remaining check |
|---|---|---|
| Correctness | Server recalculates total, rechecks item availability, and validates status transitions | Automated API tests; run in the target environment and attach actual output |
| Modularity | Browser UI is in templates/static; API, schema and transaction logic are in Flask | Small prototype remains concentrated in one Python module; split services before a larger release |
| Low coupling | Frontend exchanges JSON over same-origin API; DB tables form a persistence boundary | Direct SQLite calls remain coupled to route implementation; future repository layer is recommended |
| Security | Salted password hashes, role checks, CSRF token for mutations, student order ownership filter | No rate limiting, SSO, password reset, or independent security review |
| Reliability | Foreign keys, write transaction, status event history, seeded schema initialization | Backup/restore procedure is described but must be exercised on the team's environment |
| Usability | Availability labels, cart summary, visible errors, ready notice, responsive layout | Actual student/staff usability session is still required |
| Accessibility | Semantic headings/forms, accessible action labels, text status indicators and keyboard controls | Perform actual keyboard, contrast, and screen-reader review before claiming conformance |
| Maintainability | Stable requirement IDs and test IDs, Mermaid source diagrams, README setup | Record schema/API changes in the maintenance log; add migrations before deployed updates |

## Risk and mitigation

| Risk | Severity | Mitigation |
|---|---|---|
| Student assumes the ready state is a guaranteed preparation time | Medium | UI calls it a status update; validate actual service policy and display pickup instructions |
| Availability changes between menu display and submission | High | Recheck inside the order transaction and return a clear conflict response |
| Wrong role reaches staff endpoint | High | Apply server-side role decorator and test forbidden access |
| Local database file is lost | Medium | Provide backup/restore notes and test a backup copy before any real pilot |
| Browser closes before polling detects ready | Medium | Persist status in order history; user can reopen My Orders; external notifications remain future scope |

## Design conclusion

The models agree on a single order lifecycle, one student owner, status events, and a server-side availability check. The largest maintainability constraint is the prototype's single-file route/service implementation. The first safe refactor is to move schema access and order-state rules into dedicated modules while preserving the API contract and rerunning the traced test cases.
