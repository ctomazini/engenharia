import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.setup.install import ensure_event_custom_fields
from engenharia.tests.test_setup import create_test_deadline, create_test_permit


class TestCalendarSync(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_event_custom_fields()

	def tearDown(self):
		frappe.db.rollback()

	def _find_event(self, source_doctype, source_name):
		return frappe.db.get_value(
			"Event",
			{"custom_source_doctype": source_doctype, "custom_source_name": source_name},
			["name", "subject", "status", "all_day", "color"],
			as_dict=True,
		)

	def test_deadline_creates_all_day_event(self):
		deadline = create_test_deadline(priority="Alta")
		event = self._find_event("Deadline", deadline.name)
		self.assertTrue(event)
		self.assertEqual(event.all_day, 1)
		self.assertEqual(event.color, "red")
		self.assertIn(deadline.description, event.subject)

	def test_deadline_completed_closes_event(self):
		deadline = create_test_deadline()
		deadline.status = "Concluído"
		deadline.save(ignore_permissions=True)
		event = self._find_event("Deadline", deadline.name)
		self.assertEqual(event.status, "Closed")

	def test_deadline_medium_priority_orange(self):
		deadline = create_test_deadline(priority="Média")
		event = self._find_event("Deadline", deadline.name)
		self.assertEqual(event.color, "orange")

	def test_permit_creates_event(self):
		permit = create_test_permit()
		event = self._find_event("Permit", permit.name)
		self.assertTrue(event)
		self.assertEqual(event.all_day, 1)
		self.assertIn("PROTOCOLO", event.subject)

	def test_permit_cancelled_closes_event(self):
		permit = create_test_permit()
		permit.status = "Cancelado"
		permit.save(ignore_permissions=True)
		event = self._find_event("Permit", permit.name)
		self.assertEqual(event.status, "Closed")

	def test_permit_updates_event(self):
		permit = create_test_permit(permit_type="Alvará")
		permit.permit_type = "Habite-se"
		permit.save(ignore_permissions=True)
		event = self._find_event("Permit", permit.name)
		self.assertIn("Habite-se", event.subject)
