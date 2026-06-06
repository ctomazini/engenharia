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
			transactions = frappe.get_meta(doctype).get_dashboard_data().transactions
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
