import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from engenharia.engenharia.doctype.engineering_contract.engineering_contract import apply_amendment
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_engineering_contract,
	get_contract_payments,
)


class TestEngineeringContract(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_contract_with_installments(self):
		contract = create_test_engineering_contract(base_value=10000, installment_count=3)
		self.assertEqual(len(contract.installments), 3)
		self.assertAlmostEqual(flt(contract.current_value), 10000, places=2)

	def test_installments_sum_equals_current_value(self):
		contract = create_test_engineering_contract(base_value=9000, installment_count=3)
		total = sum(flt(row.amount) for row in contract.installments)
		self.assertAlmostEqual(total, 9000, places=2)

	def test_sync_creates_payments(self):
		contract = create_test_engineering_contract(base_value=6000, installment_count=2)
		payments = get_contract_payments(contract.name)
		self.assertEqual(len(payments), 2)

	def test_installment_origin_id_linked(self):
		contract = create_test_engineering_contract(installment_count=2)
		for row in contract.installments:
			self.assertTrue(row.installment_origin_id)
		payment_ids = {p.installment_origin_id for p in get_contract_payments(contract.name)}
		installment_ids = {p.installment_origin_id for p in contract.installments}
		self.assertEqual(payment_ids, installment_ids)

	def test_current_value_with_amendment(self):
		contract = create_test_engineering_contract(base_value=10000, installment_count=0, installments=[])
		contract.append(
			"amendments",
			{
				"amendment_date": today(),
				"amendment_type": "Adição",
				"amount": 2000,
				"description": "Aditivo teste",
			},
		)
		contract.save(ignore_permissions=True)
		contract.reload()
		self.assertEqual(flt(contract.current_value), 12000)

	def test_installments_sum_mismatch_fails(self):
		project = create_test_construction_project().name
		customer = frappe.db.get_value("Construction Project", project, "customer")
		with self.assertRaises(ValidationError) as ctx:
			frappe.get_doc(
				{
					"doctype": "Engineering Contract",
					"project": project,
					"customer": customer,
					"base_value": 10000,
					"installments": [
						{
							"due_date": today(),
							"amount": 1000,
							"status": "Pendente",
						}
					],
				}
			).insert(ignore_permissions=True)
		self.assertIn("falta", str(ctx.exception).lower())

	def test_apply_amendment_history_only(self):
		contract = create_test_engineering_contract(base_value=10000, installment_count=2)
		contract.append(
			"amendments",
			{
				"amendment_date": today(),
				"amendment_type": "Adição",
				"amount": 1000,
			},
		)
		frappe.flags.skip_installment_sum_validation = True
		try:
			contract.save(ignore_permissions=True)
		finally:
			frappe.flags.skip_installment_sum_validation = False
		apply_amendment(contract.name, regenerate=0)
		contract.reload()
		self.assertEqual(flt(contract.current_value), 11000)
		self.assertEqual(len(get_contract_payments(contract.name)), 2)

	def test_apply_amendment_regenerates_future_installments(self):
		contract = create_test_engineering_contract(base_value=9000, installment_count=3)
		contract.installments[0].status = "Recebido"
		contract.installments[0].received_amount = 3000
		contract.installments[0].receipt_date = today()
		contract.save(ignore_permissions=True)

		contract.append(
			"amendments",
			{
				"amendment_date": today(),
				"amendment_type": "Adição",
				"amount": 3000,
			},
		)
		frappe.flags.skip_installment_sum_validation = True
		try:
			contract.save(ignore_permissions=True)
		finally:
			frappe.flags.skip_installment_sum_validation = False

		apply_amendment(contract.name, regenerate=1)
		contract.reload()

		received = [row for row in contract.installments if row.status == "Recebido"]
		pending = [row for row in contract.installments if row.status == "Pendente"]
		self.assertEqual(len(received), 1)
		self.assertEqual(len(pending), 2)
		self.assertAlmostEqual(flt(contract.current_value), 12000, places=2)
		pending_total = sum(flt(row.amount) for row in pending)
		self.assertAlmostEqual(pending_total, 9000, places=2)

	def test_project_contract_value_synced(self):
		project = create_test_construction_project()
		contract = create_test_engineering_contract(project=project.name, base_value=15000, installment_count=1)
		value = frappe.db.get_value("Construction Project", project.name, "current_contract_value")
		self.assertEqual(flt(value), 15000)
		self.assertEqual(flt(contract.current_value), 15000)

	def test_multiple_contracts_aggregate_project_value(self):
		project = create_test_construction_project()
		create_test_engineering_contract(project=project.name, base_value=10000, installment_count=1)
		create_test_engineering_contract(project=project.name, base_value=5000, installment_count=1)
		value = frappe.db.get_value("Construction Project", project.name, "current_contract_value")
		self.assertEqual(flt(value), 15000)

	def test_installment_without_due_date(self):
		"""Parcela com payment_condition != Data fixa pode ter due_date vazio."""
		contract = create_test_engineering_contract(
			base_value=8000,
			current_value=8000,
			installment_count=2,
			installments=[
				{
					"due_date": today(),
					"amount": 500,
					"status": "Pendente",
					"payment_condition": "Data fixa",
					"description": "Parcela 1",
				},
				{
					"amount": 7500,
					"status": "Pendente",
					"payment_condition": "Na conclusão",
					"description": "Parcela 2",
				},
			],
		)
		self.assertEqual(len(contract.installments), 2)
		self.assertFalse(contract.installments[1].due_date)
		self.assertEqual(contract.installments[1].payment_condition, "Na conclusão")

	def test_payment_narrative_grouped(self):
		"""Narrativa agrupa parcelas de mesmo valor com ajuste na última."""
		from engenharia.documents import _build_payment_narrative

		installments = [
			{"payment_condition": "Data fixa", "due_date": "2026-06-10", "amount": 500, "status": "Pendente", "description": "Parcela 1 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2026-07-10", "amount": 500, "status": "Pendente", "description": "Parcela 2 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2026-08-10", "amount": 500, "status": "Pendente", "description": "Parcela 3 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2026-09-10", "amount": 929, "status": "Pendente", "description": "Parcela 4 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2026-10-10", "amount": 929, "status": "Pendente", "description": "Parcela 5 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2026-11-10", "amount": 929, "status": "Pendente", "description": "Parcela 6 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2026-12-10", "amount": 929, "status": "Pendente", "description": "Parcela 7 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2027-01-10", "amount": 929, "status": "Pendente", "description": "Parcela 8 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2027-02-10", "amount": 929, "status": "Pendente", "description": "Parcela 9 de 10"},
			{"payment_condition": "Data fixa", "due_date": "2027-03-10", "amount": 926, "status": "Pendente", "description": "Parcela 10 de 10"},
		]

		result = _build_payment_narrative(installments)

		self.assertIn("03 (três) parcelas", result)
		self.assertIn("quinhentos reais", result)
		self.assertIn("07 (sete) parcelas", result)
		self.assertIn("novecentos e vinte e nove reais", result)
		self.assertIn("última parcela", result)
		self.assertIn("novecentos e vinte e seis reais", result)
		self.assertIn("dia 10", result)

	def test_payment_narrative_mixed_conditions(self):
		"""Narrativa com parcelas fixas + Na conclusão."""
		from engenharia.documents import _build_payment_narrative

		installments = [
			{"payment_condition": "Data fixa", "due_date": "2026-06-10", "amount": 2000, "status": "Pendente", "description": "Entrada"},
			{"payment_condition": "Na conclusão", "due_date": "", "amount": 6000, "status": "Pendente", "description": "Saldo final"},
		]

		result = _build_payment_narrative(installments)

		self.assertIn("01 (uma) parcela", result)
		self.assertIn("dois mil reais", result)
		self.assertIn("conclusão do serviço", result)
		self.assertIn("saldo final", result.lower())

	def test_payment_narrative_empty(self):
		"""Narrativa vazia para lista sem parcelas."""
		from engenharia.documents import _build_payment_narrative

		self.assertEqual(_build_payment_narrative([]), "")
		self.assertEqual(_build_payment_narrative([{"status": "Cancelado", "amount": 100}]), "")

	def test_contract_settled_when_all_payments_received(self):
		from engenharia.tasks import on_payment_update

		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		for payment in get_contract_payments(contract.name):
			doc = frappe.get_doc("Payment", payment.name)
			doc.status = "Recebido"
			doc.received_date = today()
			doc.received_amount = doc.amount
			doc.save(ignore_permissions=True)
			on_payment_update(doc, "on_update")

		status = frappe.db.get_value("Engineering Contract", contract.name, "status")
		self.assertEqual(status, "Quitado")
