import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.boot import boot_session
from engenharia.tests.test_setup import _gerar_cnpj_valido


class TestBoot(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_boot_session_exposes_office(self):
		settings = frappe.get_single("Engineering Settings")
		settings.company_name = "Escritório Boot Teste"
		settings.company_cnpj = _gerar_cnpj_valido()
		settings.save(ignore_permissions=True)

		bootinfo = frappe._dict()
		boot_session(bootinfo)

		self.assertEqual(bootinfo.eng_office["company_name"], "Escritório Boot Teste")
		self.assertEqual(bootinfo.eng_office["company_cnpj"], settings.company_cnpj)
