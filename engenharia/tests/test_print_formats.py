import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today
from frappe.utils.print_utils import get_print

from engenharia.engenharia.doctype.construction_project.construction_project import create_project_item
from engenharia.setup.print_formats import (
	_REPORT_PRINT_FORMATS,
	PRINT_FORMAT_NAMES,
	ensure_engenharia_print_formats,
)
from engenharia.tests.test_project_item import create_test_technical_item_cylinder
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_engineering_contract,
	create_test_payment,
	get_contract_payments,
)


class TestPrintFormats(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_engenharia_print_formats()

	def tearDown(self):
		frappe.db.rollback()

	def test_print_formats_exist(self):
		for name in PRINT_FORMAT_NAMES:
			self.assertTrue(
				frappe.db.exists("Print Format", name),
				msg=f"Print Format {name} não encontrado — rode migrate",
			)

	def test_report_print_formats_linked(self):
		for spec in _REPORT_PRINT_FORMATS:
			meta = frappe.db.get_value(
				"Print Format",
				spec["name"],
				["print_format_for", "report", "print_format_type", "html"],
				as_dict=True,
			)
			self.assertEqual(meta.print_format_for, "Report")
			self.assertEqual(meta.report, spec["report"])
			self.assertEqual(meta.print_format_type, "JS")
			self.assertIn("eng-rpt-print", meta.html or "")

	def test_contract_print_preview(self):
		contract = create_test_engineering_contract(base_value=12000, installment_count=2)
		html = get_print(
			"Engineering Contract",
			contract.name,
			"Engenharia - Contrato de Obra",
		)
		self.assertIn(contract.name, html)
		self.assertIn("Contrato de Obra", html)
		self.assertIn("Parcelas", html)

	def test_payment_receipt_print_preview(self):
		contract = create_test_engineering_contract(base_value=5000, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name
		payment = frappe.get_doc("Payment", payment_name)
		payment.status = "Recebido"
		payment.received_date = today()
		payment.received_amount = payment.amount
		payment.nf_number = "NF-12345"
		payment.save(ignore_permissions=True)

		html = get_print("Payment", payment.name, "Engenharia - Recibo de Pagamento")
		self.assertIn("Recibo de Pagamento", html)
		self.assertIn("NF-12345", html)
		self.assertIn(payment.name, html)

	def test_project_budget_print_preview(self):
		project = create_test_construction_project(
			address_street="Rua Teste",
			address_number="100",
			city="Campinas",
			address_uf="SP",
			spec_project_total=2500,
			responsible_engineer="Eng. Teste",
		)
		item = create_test_technical_item_cylinder()
		create_project_item(project=project.name, technical_item=item.name)

		html = get_print(
			"Construction Project",
			project.name,
			"Engenharia - Orçamento da Obra",
		)
		self.assertIn("Orçamento da Obra", html)
		self.assertIn(project.name, html)
		self.assertIn("Itens do Orçamento", html)
		self.assertIn("Revisão", html)
