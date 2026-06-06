import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.dashboard import get as get_dashboard_data
from engenharia.setup.permissions import ensure_engenharia_permissions
from engenharia.setup.roles import seed_roles


def _create_user_with_role(role: str) -> str:
	email = f"perm_{role.replace(' ', '_').lower()}_{frappe.generate_hash(length=6)}@example.com"
	if frappe.db.exists("User", email):
		return email
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": "Perm",
			"last_name": role,
			"send_welcome_email": 0,
		}
	).insert(ignore_permissions=True)
	user.add_roles(role)
	frappe.clear_cache(user=user.name)
	return email


class TestEngenhariaPermissions(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		seed_roles()
		ensure_engenharia_permissions()
		frappe.clear_cache()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_engenharia_user_cannot_read_commission(self):
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		self.assertFalse(frappe.has_permission("Commission", "read"))

	def test_engenharia_manager_can_read_commission(self):
		user = _create_user_with_role("Engenharia Manager")
		frappe.set_user(user)
		self.assertTrue(frappe.has_permission("Commission", "read"))

	def test_engenharia_user_cannot_read_payment(self):
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		self.assertFalse(frappe.has_permission("Payment", "read"))

	def test_engenharia_user_can_read_subcontract(self):
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		self.assertTrue(frappe.has_permission("Subcontract", "read"))

	def test_engenharia_user_cannot_write_subcontract(self):
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		self.assertFalse(frappe.has_permission("Subcontract", "write"))

	def test_engenharia_user_can_read_construction_project(self):
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		self.assertTrue(frappe.has_permission("Construction Project", "read"))

	def test_engenharia_user_technical_item_read_only(self):
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		self.assertTrue(frappe.has_permission("Technical Item", "read"))
		self.assertFalse(frappe.has_permission("Technical Item", "write"))

	def test_dashboard_user_has_no_financial_payload(self):
		from engenharia.tests.test_setup import create_test_construction_project

		create_test_construction_project(status="Em andamento")
		user = _create_user_with_role("Engenharia User")
		frappe.set_user(user)
		payload = get_dashboard_data()
		self.assertFalse(payload.get("is_manager"))
		self.assertNotIn("financeiro", payload)
		self.assertNotIn("parcelas", payload)
		self.assertNotIn("amount_receivable", payload.get("kpis") or {})

	def test_dashboard_manager_has_financial_payload(self):
		from engenharia.tests.test_setup import create_test_construction_project

		create_test_construction_project(status="Em andamento")
		user = _create_user_with_role("Engenharia Manager")
		frappe.set_user(user)
		payload = get_dashboard_data()
		self.assertTrue(payload.get("is_manager"))
		self.assertIn("financeiro", payload)
		self.assertIn("parcelas", payload)
