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

	def test_follow_up_date_used_as_due_date(self):
		"""Task deve usar follow_up_date quando informado."""
		target_date = add_days(today(), 10)
		log = create_test_communication_log(
			create_task=1,
			next_steps="Retornar ligação",
			follow_up_date=target_date,
		)
		log.reload()
		self.assertTrue(log.task)
		task = frappe.get_doc("Task", log.task)
		self.assertEqual(getdate(task.due_date), getdate(target_date))

	def test_follow_up_date_default_when_empty(self):
		"""Sem follow_up_date, Task deve ter due_date = today + 3."""
		log = create_test_communication_log(
			create_task=1,
			next_steps="Retornar ligação",
		)
		log.reload()
		self.assertTrue(log.task)
		task = frappe.get_doc("Task", log.task)
		self.assertEqual(getdate(task.due_date), getdate(add_days(today(), 3)))

	def test_next_steps_rich_text_in_task(self):
		"""Text Editor HTML deve ser preservado na description da Task."""
		html_content = "<p>Ligar para <b>cliente</b> sobre orçamento.</p>"
		log = create_test_communication_log(
			create_task=1,
			next_steps=html_content,
		)
		log.reload()
		task = frappe.get_doc("Task", log.task)
		self.assertIn("<b>cliente</b>", task.description)
