import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime, today

from engenharia.engenharia.doctype.time_log.time_log import get_active_user_timer
from engenharia.tests.test_setup import create_test_construction_project, create_test_time_log


class TestTimeLog(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_valid_crud(self):
		log = create_test_time_log()
		self.assertTrue(log.name)
		self.assertEqual(log.duration_hours, 1.0)

	def test_create_without_duration_to_start_timer(self):
		log = frappe.get_doc(
			{
				"doctype": "Time Log",
				"project": create_test_construction_project().name,
				"log_date": today(),
				"activity": "Atendimento inicial",
			}
		).insert(ignore_permissions=True)
		self.assertEqual(log.duration_minutes, 0)
		self.assertEqual(log.duration_hours, 0.0)
		log.start_timer()
		log.reload()
		self.assertEqual(log.timer_active, 1)

	def test_composed_title(self):
		project = create_test_construction_project()
		customer_name = frappe.db.get_value("Customer", project.customer, "customer_name")
		log = create_test_time_log(project=project.name, activity="Reunião")
		self.assertIn(log.name, log.title)
		self.assertIn(customer_name, log.title)

	def test_duration_from_start_end(self):
		log = frappe.get_doc(
			{
				"doctype": "Time Log",
				"project": create_test_construction_project().name,
				"log_date": today(),
				"activity": "Projeto",
				"start_time": "09:00:00",
				"end_time": "11:30:00",
			}
		)
		log.insert(ignore_permissions=True)
		self.assertEqual(log.duration_minutes, 150)
		self.assertEqual(log.duration_hours, 2.5)

	def test_hours_from_minutes(self):
		log = create_test_time_log(duration_minutes=90)
		self.assertEqual(log.duration_hours, 1.5)

	def test_customer_via_project(self):
		project = create_test_construction_project()
		log = create_test_time_log(project=project.name)
		self.assertEqual(log.customer, project.customer)

	def test_without_project_fails(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Time Log",
					"log_date": today(),
					"activity": "Teste",
					"duration_minutes": 30,
				}
			).insert(ignore_permissions=True)

	def test_without_activity_fails(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Time Log",
					"project": create_test_construction_project().name,
					"log_date": today(),
					"duration_minutes": 30,
				}
			).insert(ignore_permissions=True)

	def test_start_timer(self):
		log = create_test_time_log(duration_minutes=30)
		result = log.start_timer()
		log.reload()
		self.assertEqual(log.timer_active, 1)
		self.assertTrue(log.timer_started_at)
		self.assertIn("timer_started_at", result)

	def test_stop_timer_adds_duration(self):
		log = create_test_time_log(duration_minutes=30)
		log.start_timer()
		frappe.db.set_value(
			"Time Log",
			log.name,
			"timer_started_at",
			add_to_date(now_datetime(), minutes=-10),
		)
		log.reload()
		result = log.stop_timer()
		log.reload()
		self.assertEqual(log.timer_active, 0)
		self.assertFalse(log.timer_started_at)
		self.assertEqual(log.duration_minutes, 40)
		self.assertEqual(result["duration_minutes"], 40)

	def test_duplicate_start_timer_fails(self):
		log = create_test_time_log()
		log.start_timer()
		log.reload()
		with self.assertRaises(ValidationError):
			log.start_timer()

	def test_stop_without_active_fails(self):
		log = create_test_time_log()
		with self.assertRaises(ValidationError):
			log.stop_timer()

	def test_edit_duration_while_active_fails(self):
		log = create_test_time_log(duration_minutes=30)
		log.start_timer()
		log.reload()
		log.duration_minutes = 60
		with self.assertRaises(ValidationError):
			log.save()

	def test_get_active_user_timer(self):
		for log_name in frappe.get_all(
			"Time Log",
			filters={"timer_active": 1, "owner": frappe.session.user},
			pluck="name",
		):
			frappe.db.set_value(
				"Time Log",
				log_name,
				{"timer_active": 0, "timer_started_at": None},
				update_modified=False,
			)

		log = create_test_time_log(duration_minutes=30)
		self.assertIsNone(get_active_user_timer())

		log.start_timer()
		log.reload()
		active = get_active_user_timer()
		self.assertIsNotNone(active)
		self.assertEqual(active["name"], log.name)
		self.assertTrue(active["timer_started_at"])

		log.stop_timer()
		self.assertIsNone(get_active_user_timer())

	def test_get_active_user_timer_no_permission_returns_none(self):
		user_email = f"timer_sem_perm_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "Timer",
					"last_name": "SemPerm",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user_email)
		try:
			self.assertIsNone(get_active_user_timer())
		finally:
			frappe.set_user("Administrator")
