# Experiment 12 — Maintenance Scenario, Final Demo and Viva

## Maintenance scenario: item becomes unavailable after it enters a cart

**Incident:** A student adds a menu item while it is available. Before checkout, staff or the administrator marks it sold out. The student submits the stale cart.

**Expected behavior:** the order API rechecks active/available status inside its transaction. It returns HTTP 409 with a refresh instruction and creates no partial order. The UI displays the error; the student refreshes the menu and removes or replaces the item.

**Maintenance workflow:**

1. Record timestamp, build, affected menu item, request path, and anonymized report. Avoid recording a student's password or personal data.
2. Reproduce in a disposable database by adding the item, changing availability, then submitting the saved cart.
3. Confirm server-side validation is the authority; do not rely on a disabled button alone.
4. If the regression fails, add a test for stale availability, fix the transactional check, and review whether archived items share the same path.
5. Run the order, menu-availability, and historical-snapshot regression cases; record actual results and code revision.
6. Deploy after backup and acceptance review; retain the prior source/database backup and document rollback steps.

The prototype already includes the server-side conflict response. This scenario describes the designed maintenance response; do not claim that a canteen incident occurred unless one is observed.

## Maintenance categories

| Type | Example for this system |
|---|---|
| Corrective | Fix a defect that permits a skipped order status |
| Adaptive | Update the pickup workflow if the canteen changes service policy |
| Perfective | Improve search, queue filters, or dashboard usefulness after measured feedback |
| Preventive | Add schema migrations, database backup/restore checks, dependency updates, and audit logs |

## Final demonstration script (about 5 minutes)

1. **Context (30 sec):** explain the queue problem, users, and prototype scope; distinguish verified field findings from unverified template text.
2. **Student (90 sec):** sign in with the demo student, search and filter the menu, add an available item, adjust quantity, place an order, and open My Orders.
3. **Staff (90 sec):** sign out, sign in as staff, show the dashboard, accept the order, start preparation, and mark it ready.
4. **Ready status (30 sec):** return to the still-open student page or refresh My Orders and show the ready notice/status.
5. **Administrator (45 sec):** sign in as admin, add a temporary menu item or mark one sold out, then demonstrate availability control.
6. **Close (30 sec):** state the main limitation, test evidence, one maintenance improvement, and ask for questions.

Use a disposable seeded database for the demo. Do not use real student data. If network, database, or browser state fails, show a prepared local screen and explain the failure; do not fabricate a successful run.

## Viva prompts with concise model answers

1. **Why choose an iterative process?** Early review can correct queue and availability assumptions while each increment remains runnable.
2. **How is the order total protected?** The browser sends item IDs and quantities; the server reads stored prices and calculates the total inside a transaction.
3. **Why store item snapshots?** Historical orders must keep the name and price accepted at order time even if the current menu changes.
4. **What prevents a student from seeing another student's orders?** The order query is filtered by the authenticated user ID, and staff access uses a separate role check.
5. **How is a transition controlled?** The server compares the requested state with the allowed transition set and records an event only for a valid transition.
6. **What is the ready notification?** An in-page status change found by polling every 12 seconds; it is not push, SMS, or an offline alert.
7. **What are the main limitations?** No online payment, campus SSO, automated inventory, external notifications, rate limiting, or production deployment hardening.
8. **How would you recover after a bad release?** Stop new changes, restore a known-good code/database backup, verify key order reads, then analyze the defect and retest.
9. **What is the critical path?** The longest dependent task sequence; the estimate here is 18 weeks before two weeks of reserve.
10. **Which evidence is still required?** Actual approved interviews/observations, lab dates, board records, test run output, user review, and faculty marks/signatures.

## Final handover checklist

- [ ] App starts from a clean environment using README steps.
- [ ] Demo credentials are known to the presenting team and changed before any non-demo use.
- [ ] Test output and manual browser checks are recorded accurately.
- [ ] Field evidence is real, consented, anonymized, and attached or left explicitly pending.
- [ ] All 12 lab dates, marks, remarks, and signatures are completed by the actual instructor.
- [ ] Diagrams and requirements reflect the final code revision.
- [ ] Known limitations and maintenance contact/owner are recorded by the team.
