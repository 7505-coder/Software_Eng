"""Campus Canteen Pre-Order System: Flask API and SQLite persistence."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import Flask, g, jsonify, render_template, request, session


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'staff', 'admin')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL,
    price_paise INTEGER NOT NULL CHECK (price_paise >= 0),
    is_available INTEGER NOT NULL DEFAULT 1 CHECK (is_available IN (0, 1)),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_code TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL CHECK (status IN ('pending', 'accepted', 'preparing', 'ready', 'completed', 'cancelled')),
    total_paise INTEGER NOT NULL CHECK (total_paise >= 0),
    pickup_slot TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(id),
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 20),
    unit_price_paise INTEGER NOT NULL CHECK (unit_price_paise >= 0)
);
CREATE TABLE IF NOT EXISTS order_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_user_created ON orders(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status_created ON orders(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
"""

SEED_MENU = [
    ("Samosa", "Crisp potato and pea pastry", "Snacks", 1500),
    ("Veg Sandwich", "Toasted seasonal vegetable sandwich", "Snacks", 4500),
    ("Paneer Wrap", "Paneer, salad and mint chutney", "Meals", 7500),
    ("Idli Sambhar", "Steamed idli with sambhar and chutney", "Meals", 5500),
    ("Masala Dosa", "Crisp dosa with spiced potato filling", "Meals", 8000),
    ("Veg Rice Bowl", "Rice, vegetables and house sauce", "Meals", 9000),
    ("Masala Chai", "Freshly brewed spiced tea", "Drinks", 1500),
    ("Filter Coffee", "South Indian filter coffee", "Drinks", 2500),
]

ORDER_TRANSITIONS = {
    "pending": {"accepted", "cancelled"},
    "accepted": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"completed"},
    "completed": set(),
    "cancelled": set(),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    iterations = 310_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, raw_iterations, raw_salt, raw_digest = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(raw_salt.encode("ascii"))
        expected = base64.urlsafe_b64decode(raw_digest.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(raw_iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def money(paise: int) -> str:
    return f"{paise // 100}.{paise % 100:02d}"


def user_json(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("CANTEEN_SECRET_KEY", "local-development-key-change-before-deployment"),
        DATABASE=os.environ.get("CANTEEN_DATABASE", str(Path(app.instance_path) / "canteen.sqlite3")),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("CANTEEN_HTTPS", "0") == "1",
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            db = sqlite3.connect(app.config["DATABASE"])
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("PRAGMA busy_timeout = 5000")
            g.db = db
        return g.db

    @app.teardown_appcontext
    def close_db(_error: BaseException | None = None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def initialize_database() -> None:
        with app.app_context():
            db = get_db()
            db.executescript(SCHEMA)
            if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
                demo_users = [
                    ("Demo Student", "student@campus.edu", "student123", "student"),
                    ("Canteen Staff", "staff@campus.edu", "staff123", "staff"),
                    ("System Administrator", "admin@campus.edu", "admin123", "admin"),
                ]
                for name, email, password, role in demo_users:
                    db.execute(
                        "INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                        (name, email, hash_password(password), role, now_iso()),
                    )
            if db.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0] == 0:
                db.executemany(
                    "INSERT INTO menu_items(name,description,category,price_paise,is_available,is_active,updated_at) VALUES(?,?,?,?,1,1,?)",
                    [(name, desc, category, price, now_iso()) for name, desc, category, price in SEED_MENU],
                )
            db.commit()

    def error(message: str, status: int = 400, **details: Any):
        return jsonify({"error": message, **details}), status

    def require_login(fn: Callable):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if g.get("user") is None:
                return error("Sign in to continue.", 401)
            return fn(*args, **kwargs)

        return wrapped

    def require_roles(*roles: str):
        def decorator(fn: Callable):
            @wraps(fn)
            @require_login
            def wrapped(*args, **kwargs):
                if g.user["role"] not in roles:
                    return error("Your account cannot perform this action.", 403)
                return fn(*args, **kwargs)

            return wrapped

        return decorator

    def menu_json(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "category": row["category"],
            "price": money(row["price_paise"]),
            "available": bool(row["is_available"]),
            "active": bool(row["is_active"]),
        }

    def order_json(db: sqlite3.Connection, row: sqlite3.Row, include_events: bool = False) -> dict[str, Any]:
        items = db.execute(
            "SELECT item_name,quantity,unit_price_paise FROM order_items WHERE order_id=? ORDER BY id",
            (row["id"],),
        ).fetchall()
        result = {
            "id": row["id"],
            "code": row["public_code"],
            "student": row["student_name"],
            "student_email": row["student_email"],
            "status": row["status"],
            "total": money(row["total_paise"]),
            "pickup_slot": row["pickup_slot"],
            "note": row["note"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "items": [
                {"name": item["item_name"], "quantity": item["quantity"], "unit_price": money(item["unit_price_paise"])}
                for item in items
            ],
        }
        if include_events:
            events = db.execute(
                "SELECT status,message,created_at FROM order_events WHERE order_id=? ORDER BY id",
                (row["id"],),
            ).fetchall()
            result["events"] = [dict(event) for event in events]
        return result

    @app.before_request
    def establish_request_context():
        session.setdefault("csrf_token", secrets.token_urlsafe(32))
        g.user = None
        user_id = session.get("user_id")
        if user_id:
            g.user = get_db().execute("SELECT id,name,email,role FROM users WHERE id=?", (user_id,)).fetchone()
            if g.user is None:
                session.pop("user_id", None)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.path.startswith("/api/"):
            supplied = request.headers.get("X-CSRF-Token", "")
            expected = session.get("csrf_token", "")
            if not expected or not hmac.compare_digest(expected, supplied):
                return error("The request token is missing or expired. Refresh the page and try again.", 400)

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "campus-canteen-preorder"})

    @app.get("/api/session")
    def current_session():
        return jsonify({"user": user_json(g.user), "csrf_token": session["csrf_token"]})

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        if len(name) < 2 or len(name) > 80:
            return error("Enter a name between 2 and 80 characters.")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 160:
            return error("Enter a valid email address.")
        if len(password) < 8 or len(password) > 128:
            return error("Use a password between 8 and 128 characters.")
        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,'student',?)",
                (name, email, hash_password(password), now_iso()),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return error("An account with that email already exists.", 409)
        session["user_id"] = cursor.lastrowid
        return jsonify({"user": user_json(db.execute("SELECT id,name,email,role FROM users WHERE id=?", (cursor.lastrowid,)).fetchone())}), 201

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        row = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if row is None or not verify_password(password, row["password_hash"]):
            return error("Email or password is incorrect.", 401)
        session.clear()
        session["csrf_token"] = secrets.token_urlsafe(32)
        session["user_id"] = row["id"]
        return jsonify({"user": user_json(row), "csrf_token": session["csrf_token"]})

    @app.post("/api/auth/logout")
    @require_login
    def logout():
        session.clear()
        session["csrf_token"] = secrets.token_urlsafe(32)
        return jsonify({"ok": True, "csrf_token": session["csrf_token"]})

    @app.get("/api/menu")
    def get_menu():
        db = get_db()
        clauses = ["is_active=1"]
        params: list[Any] = []
        category = request.args.get("category", "").strip()
        query = request.args.get("q", "").strip()[:80]
        if category:
            clauses.append("category=?")
            params.append(category)
        if query:
            clauses.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        if request.args.get("available") == "1":
            clauses.append("is_available=1")
        rows = db.execute(
            f"SELECT * FROM menu_items WHERE {' AND '.join(clauses)} ORDER BY category,name", params
        ).fetchall()
        return jsonify({"items": [menu_json(row) for row in rows]})

    @app.post("/api/orders")
    @require_roles("student")
    def place_order():
        data = request.get_json(silent=True) or {}
        raw_items = data.get("items")
        if not isinstance(raw_items, list) or not raw_items or len(raw_items) > 30:
            return error("Add between 1 and 30 menu items to your order.")
        quantities: dict[int, int] = {}
        for item in raw_items:
            if not isinstance(item, dict):
                return error("Each order item must include a menu item and quantity.")
            try:
                item_id = int(item.get("menu_item_id"))
                quantity = int(item.get("quantity"))
            except (ValueError, TypeError):
                return error("Menu item and quantity must be whole numbers.")
            if quantity < 1 or quantity > 20:
                return error("Each quantity must be between 1 and 20.")
            quantities[item_id] = quantities.get(item_id, 0) + quantity
            if quantities[item_id] > 20:
                return error("A menu item cannot exceed 20 in one order.")
        pickup_slot = str(data.get("pickup_slot", "")).strip()[:40]
        note = str(data.get("note", "")).strip()
        if len(note) > 300:
            return error("Order notes must be 300 characters or fewer.")
        db = get_db()
        try:
            db.execute("BEGIN IMMEDIATE")
            ids = list(quantities)
            placeholders = ",".join("?" for _ in ids)
            rows = db.execute(
                f"SELECT * FROM menu_items WHERE is_active=1 AND is_available=1 AND id IN ({placeholders})",
                ids,
            ).fetchall()
            menu = {row["id"]: row for row in rows}
            if len(menu) != len(ids):
                db.rollback()
                return error("One or more items are unavailable. Refresh the menu and try again.", 409)
            total = sum(menu[item_id]["price_paise"] * quantity for item_id, quantity in quantities.items())
            if total <= 0 or total > 10_000_000:
                db.rollback()
                return error("The order total is outside the allowed range.")
            created_at = now_iso()
            code = "C-" + secrets.token_hex(3).upper()
            cursor = db.execute(
                "INSERT INTO orders(public_code,user_id,status,total_paise,pickup_slot,note,created_at,updated_at) VALUES(?,?,'pending',?,?,?,?,?)",
                (code, g.user["id"], total, pickup_slot, note, created_at, created_at),
            )
            order_id = cursor.lastrowid
            for item_id, quantity in quantities.items():
                item = menu[item_id]
                db.execute(
                    "INSERT INTO order_items(order_id,menu_item_id,item_name,quantity,unit_price_paise) VALUES(?,?,?,?,?)",
                    (order_id, item_id, item["name"], quantity, item["price_paise"]),
                )
            db.execute(
                "INSERT INTO order_events(order_id,status,message,created_by,created_at) VALUES(?,'pending','Order placed',?,?)",
                (order_id, g.user["id"], created_at),
            )
            db.commit()
        except sqlite3.Error:
            db.rollback()
            app.logger.exception("Could not place order")
            return error("The order could not be saved. Please retry.", 500)
        row = db.execute(
            "SELECT o.*,u.name AS student_name,u.email AS student_email FROM orders o JOIN users u ON u.id=o.user_id WHERE o.id=?",
            (order_id,),
        ).fetchone()
        return jsonify({"order": order_json(db, row, include_events=True)}), 201

    @app.get("/api/orders")
    @require_login
    def list_orders():
        db = get_db()
        if g.user["role"] in {"staff", "admin"}:
            rows = db.execute(
                "SELECT o.*,u.name AS student_name,u.email AS student_email FROM orders o JOIN users u ON u.id=o.user_id ORDER BY CASE WHEN o.status IN ('completed','cancelled') THEN 1 ELSE 0 END,o.created_at DESC LIMIT 100"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT o.*,u.name AS student_name,u.email AS student_email FROM orders o JOIN users u ON u.id=o.user_id WHERE o.user_id=? ORDER BY o.created_at DESC LIMIT 50",
                (g.user["id"],),
            ).fetchall()
        return jsonify({"orders": [order_json(db, row, include_events=True) for row in rows]})

    @app.patch("/api/staff/orders/<int:order_id>")
    @require_roles("staff", "admin")
    def update_order_status(order_id: int):
        data = request.get_json(silent=True) or {}
        target = str(data.get("status", "")).strip()
        db = get_db()
        row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if row is None:
            return error("Order not found.", 404)
        if target not in ORDER_TRANSITIONS.get(row["status"], set()):
            return error("That order status change is not allowed.", 409, current_status=row["status"])
        updated_at = now_iso()
        message = {
            "accepted": "The canteen accepted your order.",
            "preparing": "Your food is being prepared.",
            "ready": "Your order is ready for pickup.",
            "completed": "Order handed over.",
            "cancelled": "The order was cancelled by canteen staff.",
        }[target]
        db.execute("UPDATE orders SET status=?,updated_at=? WHERE id=?", (target, updated_at, order_id))
        db.execute(
            "INSERT INTO order_events(order_id,status,message,created_by,created_at) VALUES(?,?,?,?,?)",
            (order_id, target, message, g.user["id"], updated_at),
        )
        db.commit()
        updated = db.execute(
            "SELECT o.*,u.name AS student_name,u.email AS student_email FROM orders o JOIN users u ON u.id=o.user_id WHERE o.id=?",
            (order_id,),
        ).fetchone()
        return jsonify({"order": order_json(db, updated, include_events=True)})

    @app.get("/api/dashboard")
    @require_roles("staff", "admin")
    def dashboard():
        db = get_db()
        today = datetime.now(timezone.utc).date().isoformat()
        counts = db.execute(
            "SELECT COUNT(*) AS total, SUM(CASE WHEN status IN ('pending','accepted','preparing','ready') THEN 1 ELSE 0 END) AS active, SUM(CASE WHEN status='ready' THEN 1 ELSE 0 END) AS ready FROM orders WHERE substr(created_at,1,10)=?",
            (today,),
        ).fetchone()
        sales = db.execute(
            "SELECT COALESCE(SUM(total_paise),0) FROM orders WHERE status='completed' AND substr(updated_at,1,10)=?",
            (today,),
        ).fetchone()[0]
        return jsonify({
            "today_orders": counts["total"],
            "active_orders": counts["active"] or 0,
            "ready_orders": counts["ready"] or 0,
            "completed_sales": money(sales),
            "currency": "INR",
        })

    @app.post("/api/menu")
    @require_roles("admin")
    def create_menu_item():
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        description = str(data.get("description", "")).strip()
        category = str(data.get("category", "")).strip()
        try:
            price = round(float(data.get("price")) * 100)
        except (TypeError, ValueError, OverflowError):
            return error("Enter a valid price.")
        if not 2 <= len(name) <= 80 or not 2 <= len(category) <= 40:
            return error("Name and category must be 2-80 and 2-40 characters.")
        if len(description) > 240 or price < 0 or price > 100_000:
            return error("Description or price is outside the allowed range.")
        available = bool(data.get("available", True))
        db = get_db()
        cursor = db.execute(
            "INSERT INTO menu_items(name,description,category,price_paise,is_available,is_active,updated_at) VALUES(?,?,?,?,?,1,?)",
            (name, description, category, price, int(available), now_iso()),
        )
        db.commit()
        return jsonify({"item": menu_json(db.execute("SELECT * FROM menu_items WHERE id=?", (cursor.lastrowid,)).fetchone())}), 201

    @app.patch("/api/menu/<int:item_id>")
    @require_roles("admin")
    def update_menu_item(item_id: int):
        data = request.get_json(silent=True) or {}
        db = get_db()
        current = db.execute("SELECT * FROM menu_items WHERE id=? AND is_active=1", (item_id,)).fetchone()
        if current is None:
            return error("Menu item not found.", 404)
        name = str(data.get("name", current["name"])).strip()
        description = str(data.get("description", current["description"])).strip()
        category = str(data.get("category", current["category"])).strip()
        try:
            price = round(float(data.get("price", current["price_paise"] / 100)) * 100)
        except (TypeError, ValueError, OverflowError):
            return error("Enter a valid price.")
        if not 2 <= len(name) <= 80 or not 2 <= len(category) <= 40 or len(description) > 240 or not 0 <= price <= 100_000:
            return error("Menu fields are outside the allowed range.")
        available = int(bool(data.get("available", current["is_available"])))
        db.execute(
            "UPDATE menu_items SET name=?,description=?,category=?,price_paise=?,is_available=?,updated_at=? WHERE id=?",
            (name, description, category, price, available, now_iso(), item_id),
        )
        db.commit()
        return jsonify({"item": menu_json(db.execute("SELECT * FROM menu_items WHERE id=?", (item_id,)).fetchone())})

    @app.delete("/api/menu/<int:item_id>")
    @require_roles("admin")
    def archive_menu_item(item_id: int):
        db = get_db()
        cursor = db.execute("UPDATE menu_items SET is_active=0,updated_at=? WHERE id=? AND is_active=1", (now_iso(), item_id))
        db.commit()
        if cursor.rowcount == 0:
            return error("Menu item not found.", 404)
        return jsonify({"ok": True})

    initialize_database()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
