"""Automated API and workflow checks for the course prototype."""

import os
import tempfile
import unittest
from pathlib import Path

_TEST_HOME = tempfile.TemporaryDirectory(prefix="canteen-test-")
os.environ["CANTEEN_DATABASE"] = str(Path(_TEST_HOME.name) / "module-import.sqlite3")

from app import create_app  # noqa: E402


class CanteenApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="canteen-case-")
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(Path(self.temp.name) / "canteen.sqlite3"),
            "SESSION_COOKIE_SECURE": False,
        })
        self.client = self.app.test_client()
        self.csrf = self.client.get("/api/session").get_json()["csrf_token"]

    def tearDown(self):
        self.temp.cleanup()

    def headers(self):
        return {"X-CSRF-Token": self.csrf}

    def post_json(self, path, body):
        response = self.client.post(path, json=body, headers=self.headers())
        if response.is_json and response.get_json().get("csrf_token"):
            self.csrf = response.get_json()["csrf_token"]
        return response

    def patch_json(self, path, body):
        return self.client.patch(path, json=body, headers=self.headers())

    def login(self, email="student@campus.edu", password="student123"):
        response = self.post_json("/api/auth/login", {"email": email, "password": password})
        if response.status_code == 200:
            self.csrf = response.get_json()["csrf_token"]
        return response

    def create_order(self, item_id=None, quantity=2):
        if item_id is None:
            item_id = self.client.get("/api/menu").get_json()["items"][0]["id"]
        return self.post_json("/api/orders", {"items": [{"menu_item_id": item_id, "quantity": quantity}]})

    def test_health_and_seed_menu(self):
        self.assertEqual(self.client.get("/api/health").get_json()["status"], "ok")
        items = self.client.get("/api/menu").get_json()["items"]
        self.assertEqual(len(items), 8)
        self.assertTrue(all("price" in item and "available" in item for item in items))
        searched = self.client.get("/api/menu?q=chai").get_json()["items"]
        self.assertEqual([item["name"] for item in searched], ["Masala Chai"])

    def test_home_and_static_assets_are_served(self):
        page = self.client.get("/")
        script = self.client.get("/static/app.js")
        stylesheet = self.client.get("/static/styles.css")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Campus Canteen", page.data)
        self.assertIn(b"placeOrder", script.data)
        self.assertIn(b"@media", stylesheet.data)

    def test_login_rejects_wrong_password_and_csrf_is_required(self):
        response = self.login(password="wrongpass")
        self.assertEqual(response.status_code, 401)
        no_token = self.client.post("/api/auth/login", json={"email": "student@campus.edu", "password": "student123"})
        self.assertEqual(no_token.status_code, 400)

    def test_student_order_uses_server_price_and_records_status_event(self):
        self.assertEqual(self.login().status_code, 200)
        item = self.client.get("/api/menu").get_json()["items"][0]
        response = self.create_order(item_id=item["id"], quantity=2)
        self.assertEqual(response.status_code, 201)
        order = response.get_json()["order"]
        self.assertEqual(order["total"], f"{float(item['price']) * 2:.2f}")
        self.assertEqual(order["status"], "pending")
        self.assertEqual(order["events"][0]["status"], "pending")

    def test_order_requires_student_and_valid_available_items(self):
        self.assertEqual(self.create_order().status_code, 401)
        self.login(email="staff@campus.edu", password="staff123")
        self.assertEqual(self.create_order().status_code, 403)
        self.login(email="student@campus.edu", password="student123")
        self.assertEqual(self.create_order(item_id=99999).status_code, 409)
        self.assertEqual(self.create_order(item_id=1, quantity=21).status_code, 400)

    def test_unavailable_item_is_rejected_without_creating_an_order(self):
        self.login(email="admin@campus.edu", password="admin123")
        item_id = self.client.get("/api/menu").get_json()["items"][0]["id"]
        toggled = self.patch_json(f"/api/menu/{item_id}", {"available": False})
        self.assertFalse(toggled.get_json()["item"]["available"])
        self.login()
        response = self.create_order(item_id=item_id)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.client.get("/api/orders").get_json()["orders"], [])

    def test_student_cannot_view_another_students_orders(self):
        self.login()
        created = self.create_order()
        self.assertEqual(created.status_code, 201)
        self.post_json("/api/auth/logout", {})
        register = self.post_json("/api/auth/register", {"name": "Second Student", "email": "second@campus.edu", "password": "longpassword"})
        self.assertEqual(register.status_code, 201)
        data = self.client.get("/api/orders").get_json()
        self.assertEqual(data["orders"], [])

    def test_staff_must_follow_order_status_sequence(self):
        self.login()
        order = self.create_order().get_json()["order"]
        self.post_json("/api/auth/logout", {})
        self.login(email="staff@campus.edu", password="staff123")
        invalid = self.patch_json(f"/api/staff/orders/{order['id']}", {"status": "ready"})
        self.assertEqual(invalid.status_code, 409)
        accepted = self.patch_json(f"/api/staff/orders/{order['id']}", {"status": "accepted"})
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.get_json()["order"]["status"], "accepted")

    def test_full_status_lifecycle_updates_completed_sales(self):
        self.login()
        order = self.create_order(quantity=1).get_json()["order"]
        self.post_json("/api/auth/logout", {})
        self.login(email="staff@campus.edu", password="staff123")
        for status in ("accepted", "preparing", "ready", "completed"):
            response = self.patch_json(f"/api/staff/orders/{order['id']}", {"status": status})
            self.assertEqual(response.status_code, 200, status)
        dashboard = self.client.get("/api/dashboard").get_json()
        self.assertEqual(dashboard["completed_sales"], order["total"])
        self.assertEqual(dashboard["ready_orders"], 0)

    def test_archived_item_remains_in_historical_order_snapshot(self):
        self.login()
        menu_item = self.client.get("/api/menu").get_json()["items"][0]
        order = self.create_order(item_id=menu_item["id"], quantity=1).get_json()["order"]
        self.post_json("/api/auth/logout", {})
        self.login(email="admin@campus.edu", password="admin123")
        self.assertEqual(self.client.delete(f"/api/menu/{menu_item['id']}", headers=self.headers()).status_code, 200)
        self.login()
        history = self.client.get("/api/orders").get_json()["orders"]
        self.assertEqual(history[0]["id"], order["id"])
        self.assertEqual(history[0]["items"][0]["name"], menu_item["name"])

    def test_admin_can_add_update_and_archive_menu_item(self):
        self.login(email="admin@campus.edu", password="admin123")
        created = self.post_json("/api/menu", {"name": "Fruit Cup", "category": "Snacks", "price": "35", "description": "Seasonal fruit"})
        self.assertEqual(created.status_code, 201)
        item_id = created.get_json()["item"]["id"]
        toggled = self.patch_json(f"/api/menu/{item_id}", {"available": False})
        self.assertFalse(toggled.get_json()["item"]["available"])
        archived = self.client.delete(f"/api/menu/{item_id}", headers=self.headers())
        self.assertEqual(archived.status_code, 200)
        ids = [item["id"] for item in self.client.get("/api/menu").get_json()["items"]]
        self.assertNotIn(item_id, ids)

    def test_staff_dashboard_requires_staff_role(self):
        self.login()
        self.assertEqual(self.client.get("/api/dashboard").status_code, 403)
        self.post_json("/api/auth/logout", {})
        self.login(email="staff@campus.edu", password="staff123")
        dashboard = self.client.get("/api/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        self.assertIn("active_orders", dashboard.get_json())

    def test_registration_never_grants_privileged_role(self):
        response = self.post_json("/api/auth/register", {
            "name": "New Student", "email": "new@campus.edu", "password": "password123", "role": "admin",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["user"]["role"], "student")


if __name__ == "__main__":
    unittest.main()
