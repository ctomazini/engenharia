"""Marca is_primary nos contratos de obras que têm exatamente um contrato ativo.

Obras com múltiplos contratos ficam sem principal definido (decisão do usuário);
nesses casos a geração de documentos usa o fallback determinístico.
"""

import frappe


def execute():
	if not frappe.db.table_exists("Engineering Contract"):
		return
	if not frappe.db.has_column("Engineering Contract", "is_primary"):
		return

	projects_with_primary = set(
		frappe.get_all(
			"Engineering Contract",
			filters={"is_primary": 1, "project": ["!=", ""]},
			pluck="project",
			limit_page_length=0,
		)
	)

	single_contract_projects = frappe.db.sql(
		"""
		SELECT project, MIN(name) AS contract, COUNT(*) AS total
		FROM `tabEngineering Contract`
		WHERE status != 'Cancelado' AND IFNULL(project, '') != ''
		GROUP BY project
		HAVING total = 1
		""",
		as_dict=True,
	)

	updated = False
	for row in single_contract_projects:
		if row.project in projects_with_primary:
			continue
		frappe.db.set_value(
			"Engineering Contract", row.contract, "is_primary", 1, update_modified=False
		)
		updated = True

	if updated:
		frappe.db.commit()  # patch: backfill is_primary p/ obras com contrato único
