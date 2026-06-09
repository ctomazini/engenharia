import frappe
from frappe.tests.utils import FrappeTestCase

DOCTYPES_WITH_CONNECTIONS = (
	"Work Cost",
	"Payment",
	"Subcontract",
	"Commission",
	"Engineering Contract",
	"Task",
	"Permit",
	"Deadline",
	"Supplier",
	"Customer",
	"Construction Project",
)


class TestDocTypeDashboard(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_connection_shortcuts_not_duplicated(self):
		for doctype in DOCTYPES_WITH_CONNECTIONS:
			data = frappe.get_meta(doctype).get_dashboard_data()
			transactions = data.transactions or []
			if not transactions:
				self.assertTrue(
					data.internal_links,
					f"{doctype}: dashboard sem transactions nem internal_links",
				)
				continue
			seen_items: list[str] = []
			for group in transactions:
				self.assertTrue(
					group.get("label"),
					f"{doctype}: grupo de conexões sem label ({group})",
				)
				for item in group.get("items") or []:
					self.assertNotIn(
						item,
						seen_items,
						f"{doctype}: atalho duplicado para {item}",
					)
					seen_items.append(item)

	def test_hub_dashboard_internal_links(self):
		"""Dashboard nativo esvaziado — contadores ficam no hub_summary_bar."""
		data = frappe.get_meta("Construction Project").get_dashboard_data()
		self.assertEqual(data.internal_links, {})
		self.assertTrue(data.transactions)

	def test_customer_dashboard_internal_links(self):
		data = frappe.get_meta("Customer").get_dashboard_data()
		self.assertIn("Construction Project", data.internal_links)
		self.assertEqual(data.internal_links["Payment"], "customer")

	def test_get_dashboard_data_does_not_raise(self):
		for doctype in DOCTYPES_WITH_CONNECTIONS:
			data = frappe.get_meta(doctype).get_dashboard_data()
			self.assertTrue(data.internal_links or data.transactions)
