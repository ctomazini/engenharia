import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.receivables import (
	_build_receivables_context,
	_get_primary_addresses_batch,
	get_monthly_receivables_report,
)
from engenharia.tests.test_documents import (
	_create_test_document_template,
	_ensure_engineering_settings,
)
from engenharia.tests.test_setup import (
	_uid,
	create_test_construction_project,
	create_test_customer,
	create_test_engineering_contract,
	get_contract_payments,
)

TEST_YEAR = 2031
TEST_MONTH = 5


def _installment(due_date, amount, idx):
	return {
		"doctype": "Engineering Contract Installment",
		"amount": amount,
		"status": "Pendente",
		"description": f"Parcela {idx}",
		"payment_condition": "Data fixa",
		"due_date": due_date,
	}


class TestMonthlyReceivablesReport(FrappeTestCase):
	def setUp(self):
		_ensure_engineering_settings()
		self.customer = create_test_customer(
			customer_name=_uid("Cliente Recebíveis"),
			addresses=[
				{
					"street": "Rua das Obras",
					"number": "123",
					"district": "Centro",
					"city": "São Paulo",
					"state": "SP",
					"cep": "01001000",
					"is_primary": 1,
				}
			],
		)
		self.project = create_test_construction_project(customer=self.customer.name)
		# Duas parcelas no mês de teste e uma fora (mês seguinte).
		self.contract = create_test_engineering_contract(
			project=self.project.name,
			base_value=3000,
			current_value=3000,
			installment_count=3,
			installments=[
				_installment(f"{TEST_YEAR}-{TEST_MONTH:02d}-10", 1000, 1),
				_installment(f"{TEST_YEAR}-{TEST_MONTH:02d}-20", 1000, 2),
				_installment(f"{TEST_YEAR}-{TEST_MONTH + 1:02d}-15", 1000, 3),
			],
		)
		self.payments = get_contract_payments(self.contract.name)
		self.template_name = _create_test_document_template(
			"{{ report_title }} {{ month_label }}"
			"{% for c in customers %} {{ c.customer_name }} {{ c.cpf_cnpj }}"
			"{% for i in c.installments %} {{ i.valor_fmt }}{% endfor %}"
			"{% endfor %} Total {{ total_fmt }}"
		)
		if not self.template_name:
			self.skipTest("python-docx/docxtpl não instalado")
		self.template = frappe.get_doc("Document Template", self.template_name)

	def tearDown(self):
		frappe.db.rollback()

	def _mark_received(self):
		"""Marca as duas parcelas do mês como recebidas no mês de teste."""
		for p in self.payments:
			due = frappe.db.get_value("Payment", p.name, "due_date")
			if due and due.month == TEST_MONTH and due.year == TEST_YEAR:
				doc = frappe.get_doc("Payment", p.name)
				doc.manual_override = 1
				doc.status = "Recebido"
				doc.received_amount = doc.amount
				doc.received_date = f"{TEST_YEAR}-{TEST_MONTH:02d}-25"
				doc.save(ignore_permissions=True)

	def test_previsao_mode_returns_docx(self):
		result = get_monthly_receivables_report(
			month=TEST_MONTH,
			year=TEST_YEAR,
			mode="previsao",
			template_name=self.template.name,
		)
		self.assertTrue(result.get("file_content"))
		self.assertEqual(result.get("count"), 2)
		self.assertTrue(result["file_name"].endswith(".docx"))

	def test_previsao_context_groups_by_customer(self):
		context = _build_receivables_context(TEST_MONTH, TEST_YEAR, "previsao")
		match = next(
			(c for c in context["customers"] if c["customer"] == self.customer.name),
			None,
		)
		self.assertIsNotNone(match)
		self.assertEqual(match["count"], 2)
		self.assertEqual(match["subtotal"], 2000)
		self.assertEqual(match["cpf_cnpj_label"], "CPF")
		self.assertIn("Rua das Obras", match["address_full"])
		self.assertEqual(match["subtotal_fmt"], "2.000,00")

	def test_realizado_mode_returns_docx(self):
		self._mark_received()
		result = get_monthly_receivables_report(
			month=TEST_MONTH,
			year=TEST_YEAR,
			mode="realizado",
			template_name=self.template.name,
		)
		self.assertTrue(result.get("file_content"))
		self.assertEqual(result.get("count"), 2)

	def test_realizado_excludes_unreceived(self):
		# Sem marcar como recebido, modo realizado não deve trazer parcelas.
		context = _build_receivables_context(TEST_MONTH, TEST_YEAR, "realizado")
		match = next(
			(c for c in context["customers"] if c["customer"] == self.customer.name),
			None,
		)
		self.assertIsNone(match)

	def test_excludes_cancelled_payments(self):
		first = self.payments[0]
		doc = frappe.get_doc("Payment", first.name)
		doc.manual_override = 1
		doc.status = "Cancelado"
		doc.save(ignore_permissions=True)

		context = _build_receivables_context(TEST_MONTH, TEST_YEAR, "previsao")
		match = next(
			(c for c in context["customers"] if c["customer"] == self.customer.name),
			None,
		)
		self.assertIsNotNone(match)
		self.assertEqual(match["count"], 1)

	def test_excludes_payments_outside_month(self):
		context = _build_receivables_context(TEST_MONTH, TEST_YEAR, "previsao")
		match = next(
			(c for c in context["customers"] if c["customer"] == self.customer.name),
			None,
		)
		self.assertIsNotNone(match)
		# A parcela de junho não pode aparecer no relatório de maio.
		for inst in match["installments"]:
			self.assertNotIn(f"{TEST_YEAR}-{TEST_MONTH + 1:02d}", str(inst["due_date_fmt"]))
		self.assertEqual(match["count"], 2)

	def test_invalid_mode_raises(self):
		self.assertRaises(
			frappe.ValidationError,
			get_monthly_receivables_report,
			month=TEST_MONTH,
			year=TEST_YEAR,
			mode="invalido",
			template_name=self.template.name,
		)

	def test_invalid_month_raises(self):
		self.assertRaises(
			frappe.ValidationError,
			get_monthly_receivables_report,
			month=13,
			year=TEST_YEAR,
			mode="previsao",
			template_name=self.template.name,
		)

	def test_disabled_template_raises(self):
		self.template.enabled = 0
		self.template.save(ignore_permissions=True)
		self.assertRaises(
			frappe.ValidationError,
			get_monthly_receivables_report,
			month=TEST_MONTH,
			year=TEST_YEAR,
			mode="previsao",
			template_name=self.template.name,
		)

	def test_empty_period_returns_empty_context(self):
		context = _build_receivables_context(1, 1990, "previsao")
		self.assertEqual(context["count"], 0)
		self.assertEqual(context["customers"], [])
		self.assertEqual(context["total_fmt"], "0,00")

	def test_address_batch_lookup(self):
		addresses = _get_primary_addresses_batch([self.customer.name])
		self.assertIn(self.customer.name, addresses)
		self.assertIn("Rua das Obras", addresses[self.customer.name])
