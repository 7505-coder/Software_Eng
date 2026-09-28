# Automated Test Run Report

**Run date:** 2026-09-28  
**Command:** `python -m unittest discover -s tests -v`  
**Result:** **13 tests passed, 0 failed**.  
**Environment:** Python 3.12.14, Flask 3.1.3, temporary SQLite databases, Flask test client.  
**Elapsed test time:** 31.079 seconds.

## Cases executed

- Admin can add, update availability, and archive menu items.
- Archived menu item remains readable in a historical order snapshot.
- Full order status lifecycle updates completed sales.
- Health response, seeded menu, and search work.
- Home page and static CSS/JavaScript assets are served.
- Invalid login fails and a mutating request without a CSRF token is rejected.
- Student order request enforces role, item ID, and quantity limits.
- Registration cannot assign a privileged role.
- Staff dashboard requires staff role.
- Staff cannot skip an order-state transition.
- One student cannot read another student's order history.
- Server stores the order, status event, item snapshot, and recomputed total.
- Unavailable-item order is rejected without creating an order.

This run does not cover real browser interaction, the polling toast timing, keyboard/screen-reader review, load/performance targets, external services, real field interviews, or canteen acceptance. Those remain unverified and should not be reported as passed.
