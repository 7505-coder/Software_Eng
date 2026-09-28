# Campus Canteen Pre-Order System

A small student/canteen web application for browsing menu availability, placing pickup orders, tracking order status, and managing the canteen queue. The UI uses HTML, CSS, and vanilla JavaScript; Flask provides the API and server-rendered shell; SQLite stores users, menu items, orders, order lines, and status events.

## Requirements

- Python 3.10 or newer
- Pip
- Network access for the first `pip install` (runtime UI and data handling are local after install)

## Run locally

From this folder, create and activate a virtual environment, install the one application dependency, then start Flask:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The SQLite database is created at `instance/canteen.sqlite3` on first run and is seeded with demo users and eight menu items. Delete that local database to reset the demonstration data.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Student | `student@campus.edu` | `student123` |
| Canteen staff | `staff@campus.edu` | `staff123` |
| Administrator | `admin@campus.edu` | `admin123` |

Students can also create a student account from the sign-in panel. Registration never creates staff or administrator accounts.

## Main workflows

1. Browse or search the menu. Sold-out items remain visible but cannot be added.
2. Add items, set quantities, optionally enter a pickup time or preparation note, and place an order. The server recalculates all prices and checks availability inside a database transaction.
3. Open **My orders** to follow status and order history. The page polls every 12 seconds and announces a newly ready order while it is open.
4. Sign in as staff to accept orders, start preparation, mark orders ready, complete pickup, or cancel an active order. The dashboard shows today's queue and completed sales.
5. Sign in as administrator to add menu items, mark them sold out/available, or archive them.

## Data and security notes

- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes. Role checks run on the server. Mutating API requests require a session CSRF token.
- Prices are stored as integer paise; the UI displays Indian rupees. Order lines keep the item name and unit price as a snapshot.
- Orders use a state transition rule: pending → accepted → preparing → ready → completed. Staff may cancel pending, accepted, or preparing orders.
- The notification is an in-page status update using polling. No email, SMS, payment gateway, or external push service is configured. Payment is collected at the counter.
- Demo credentials and the development secret must be replaced before any real deployment. For a private deployment set `CANTEEN_SECRET_KEY` to a strong random value and `CANTEEN_DATABASE` to a protected persistent path. Set `CANTEEN_HTTPS=1` only when TLS is configured; use a production WSGI server and HTTPS.
- This is a course prototype, not a production payment or identity system. It has no password reset, rate limiting, external campus SSO, inventory forecasting, or multi-canteen tenancy.

## Run the automated checks

```powershell
python -m unittest discover -s tests -v
```

The suite uses a temporary SQLite database and the Flask test client. The test scenarios are also documented in `docs/experiments/experiment-11-test-plan.md`.

Flask's official [application testing guide](https://flask.palletsprojects.com/en/stable/testing/) describes the test-client approach used here.

## Project map

```text
app.py                 Flask routes, validation, role checks, schema, seed data
templates/index.html   Student and staff interface
static/app.js          Menu, cart, authentication, order queue and polling
static/styles.css      Responsive styles
instance/              Local SQLite file created on first run
tests/                 Automated API and workflow checks
docs/                  Twelve lab experiment records, diagrams, demo and viva
```
