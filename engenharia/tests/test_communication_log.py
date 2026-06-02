import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, now_datetime, today

from engenharia.tests.test_setup import (
	create_test_communication_log,
	create_test_construction_project,
	create_test_customer,
)


class TestCommunicationLog(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_valid_crud(self):
		log = create_test_communication_log()
		self.assertTrue(log.name)

	def test_customer_via_project(self):
		project = create_test_construction_project()
		log = frappe.get_doc(
			{
				"doctype": "Communication Log",
				"project": project.name,
				"subject": "Teste via obra",
				"communication_type": "Telefone",
				"communication_date": now_datetime(),
			}
		)
		log.insert(ignore_permissions=True)
		self.assertEqual(log.customer, project.customer)

	def test_auto_create_task(self):
		log = create_test_communication_log(
			create_task=1,
			next_steps="Retornar ligação amanhã",
		)
		log.reload()
		self.assertTrue(log.task)
		task = frappe.get_doc("Task", log.task)
		self.assertIn("Follow-up:", task.subject)

	def test_without_subject_fails(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Communication Log",
					"customer": create_test_customer().name,
					"communication_type": "Telefone",
					"communication_date": now_datetime(),
				}
			).insert(ignore_permissions=True)

	def test_without_type_fails(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Communication Log",
					"customer": create_test_customer().name,
					"subject": "Teste",
					"communication_type": "",
					"communication_date": now_datetime(),
				}
			).insert(ignore_permissions=True)

	def test_create_task_without_next_steps(self):
		log = create_test_communication_log(create_task=1, next_steps=None)
		log.reload()
		self.assertFalse(log.task)

	def test_create_task_after_first_save(self):
		log = create_test_communication_log(next_steps="Ligar na segunda-feira")
		self.assertFalse(log.task)
		log.create_task = 1
		log.save(ignore_permissions=True)
		log.reload()
		self.assertTrue(log.task)
		task = frappe.get_doc("Task", log.task)
		self.assertEqual(getdate(task.due_date), getdate(add_days(today(), 3)))
