import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from engenharia.engenharia.doctype.deadline.deadline import get_events
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_deadline,
	create_test_public_agency,
)


class TestDeadline(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_future_pending(self):
		deadline = create_test_deadline(due_date=add_days(today(), 10))
		self.assertEqual(deadline.status or "Pendente", "Pendente")

	def test_high_priority(self):
		deadline = create_test_deadline(priority="Alta")
		self.assertEqual(deadline.priority, "Alta")

	def test_customer_via_project(self):
		project = create_test_construction_project()
		deadline = create_test_deadline(project=project.name)
		self.assertEqual(deadline.customer, project.customer)

	def test_composed_title(self):
		project = create_test_construction_project()
		customer_name = frappe.db.get_value("Customer", project.customer, "customer_name")
		deadline = create_test_deadline(project=project.name, description="Entrega projeto")
		self.assertIn(deadline.name, deadline.title)
		self.assertIn(customer_name, deadline.title)

	def test_get_events(self):
		deadline = create_test_deadline(due_date=today())
		events = get_events(add_days(today(), -1), add_days(today(), 1))
		names = [e["name"] for e in events]
		self.assertIn(deadline.name, names)

	def test_without_project_fails(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Deadline",
					"due_date": today(),
					"description": "Sem obra",
				}
			).insert(ignore_permissions=True)

	def test_without_description_fails(self):
		project = create_test_construction_project().name
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Deadline",
					"project": project,
					"due_date": today(),
				}
			).insert(ignore_permissions=True)

	def test_orgao_type_requires_agency(self):
		project = create_test_construction_project().name
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Deadline",
					"project": project,
					"due_date": today(),
					"description": "Prazo prefeitura",
					"deadline_type": "Órgão",
				}
			).insert(ignore_permissions=True)

	def test_orgao_type_with_agency(self):
		project = create_test_construction_project().name
		agency = create_test_public_agency().name
		deadline = create_test_deadline(
			project=project,
			deadline_type="Órgão",
			public_agency=agency,
		)
		self.assertEqual(deadline.public_agency, agency)
