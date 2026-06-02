import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_project_stage,
	create_test_task,
)


class TestTask(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		task = create_test_task()
		self.assertTrue(frappe.db.exists("Task", task.name))
		task.status = "Fazendo"
		task.save(ignore_permissions=True)
		name = task.name
		task.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Task", name))

	def test_customer_from_project(self):
		project = create_test_construction_project()
		task = create_test_task(project=project.name)
		self.assertEqual(task.customer, project.customer)

	def test_complete_sets_date(self):
		task = create_test_task()
		task.complete()
		task.reload()
		self.assertEqual(task.status, "Feito")
		self.assertTrue(task.completed_on)

	def test_kanban_board_fixture(self):
		self.assertTrue(frappe.db.exists("Kanban Board", "Engenharia Obras"))
		board = frappe.get_doc("Kanban Board", "Engenharia Obras")
		self.assertEqual(board.reference_doctype, "Task")
		self.assertEqual(board.field_name, "status")
		self.assertEqual(len(board.columns), 4)

	def test_task_with_stage(self):
		project = create_test_construction_project().name
		stage = create_test_project_stage(project=project).name
		task = create_test_task(project=project, stage=stage)
		self.assertEqual(task.stage, stage)
