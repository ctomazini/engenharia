#!/usr/bin/env python3
"""Regenerate CODEBASE.md from live DocType JSON and repo metrics."""

import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DT_DIR = ROOT / "engenharia/engenharia/doctype"
OUT_PATH = ROOT / "CODEBASE.md"
REPORT_COUNT = 6  # engenharia/engenharia/report/* (projects_by_status removido em v1.1.0)
PRINT_FORMAT_COUNT = 15  # engenharia/setup/print_formats.py PRINT_FORMAT_NAMES


def esc(s):
	if s is None:
		return ""
	return str(s).replace("|", "/").replace("\n", " ")


def md_table(headers, rows):
	lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
	for r in rows:
		lines.append("| " + " | ".join(esc(c) for c in r) + " |")
	return "\n".join(lines) + "\n\n"


def count_lines(ext):
	total = 0
	for p in ROOT.rglob(f"*{ext}"):
		if ".git" in p.parts or "__pycache__" in p.parts or "node_modules" in p.parts:
			continue
		try:
			with open(p, encoding="utf-8", errors="ignore") as f:
				total += sum(1 for _ in f)
		except OSError:
			pass
	return total


def count_test_methods():
	total = 0
	files = 0
	for pattern in ("engenharia/tests/test_*.py", "engenharia/engenharia/doctype/**/test_*.py"):
		for tf in ROOT.glob(pattern):
			files += 1
			total += len(
				re.findall(r"^\s+def test_", tf.read_text(encoding="utf-8", errors="ignore"), re.M)
			)
	return total, files


def render_dt(name, d):
	meta_line = (
		f"**Meta:** autoname=`{d.get('autoname')}` · naming_rule=`{d.get('naming_rule', '')}` · "
		f"title_field=`{d.get('title_field', '')}` · istable={d.get('istable', 0)} · "
		f"issingle={d.get('issingle', 0)}"
	)
	rows = []
	for f in sorted(d.get("fields", []), key=lambda x: x.get("idx") or 0):
		ft = f.get("fieldtype", "")
		if ft in ("Section Break", "Column Break", "Tab Break"):
			continue
		opts = (f.get("options") or "").replace("\n", " ")
		if len(opts) > 60:
			opts = opts[:57] + "..."
		rows.append([
			f.get("fieldname", ""),
			f.get("label", ""),
			ft,
			opts,
			"✓" if f.get("reqd") else "",
			"✓" if f.get("unique") else "",
		])
	return (
		f"### {name}\n\n{meta_line}\n\n"
		+ md_table(["fieldname", "label", "fieldtype", "options", "reqd", "unique"], rows)
	)


def load_doctypes():
	child_tables, standalone, auxiliary, single = [], [], [], []
	aux_names = {
		"Cost Category",
		"Supplier",
		"Technical Item",
		"Public Agency",
		"Project Stage",
		"Stage Type",
		"Permit Type",
		"Project Stage Template",
	}
	for folder in sorted(DT_DIR.iterdir()):
		jpath = folder / f"{folder.name}.json"
		if not jpath.exists():
			continue
		d = json.loads(jpath.read_text(encoding="utf-8"))
		name = d.get("name") or folder.name
		if d.get("istable"):
			child_tables.append((name, d))
		elif d.get("issingle"):
			single.append((name, d))
		elif name in aux_names:
			auxiliary.append((name, d))
		else:
			standalone.append((name, d))
	return child_tables, standalone, auxiliary, single


def main():
	py_lines = count_lines(".py")
	js_lines = count_lines(".js")
	test_methods, test_files = count_test_methods()
	head = subprocess.check_output(
		["git", "log", "-1", "--format=%h %ci %s"], cwd=ROOT, text=True
	).strip()
	recent = subprocess.check_output(["git", "log", "--oneline", "-12"], cwd=ROOT, text=True).strip()
	child_tables, standalone, auxiliary, single = load_doctypes()
	dt_total = len(standalone) + len(auxiliary) + len(child_tables) + len(single)

	L = []
	L.append("# CODEBASE — App Engenharia (Frappe v16)\n\n")
	L.append(
		f"> Gerado em **{date.today().isoformat()}** — inventário técnico do app greenfield EN. "
		"Frappe puro, **sem ERPNext**.\n\n"
	)
	L.append(f"> **HEAD:** `{head}`\n\n---\n\n")

	L.append("## 1. Visão Geral\n\n")
	L.append(
		md_table(
			["Item", "Valor"],
			[
				["Nome", "engenharia"],
				["Versão", "1.2.0 (`pyproject.toml`)"],
				["Framework", "Frappe v16"],
				["Licença", "MIT"],
				["Site dev", "engenharia.local"],
				["Linhas Python", f"~{py_lines}"],
				["Linhas JavaScript", f"~{js_lines}"],
				["Métodos de teste", f"{test_methods} ({test_files} arquivos)"],
				["DocTypes", f"{dt_total} (`custom: 0`)"],
				["Script Reports", str(REPORT_COUNT)],
				["Print Formats", str(PRINT_FORMAT_COUNT)],
			],
		)
	)
	L.append(
		"**Propósito:** gestão de obras — projetos, contratos, custos (obra + escritório), "
		"subcontratos, comissões, prazos, protocolos, pagamentos, painel modular, "
		"documentos `.docx`, impressão PDF de relatórios.\n\n"
		"**Deps:** `docxtpl>=0.18.0`.\n\n"
	)
	L.append(f"**Commits recentes:**\n```text\n{recent}\n```\n\n")

	L.append("## 2. Árvore de Arquivos (anotada)\n\n```text\n")
	L.append("engenharia/\n├── CODEBASE.md, README.md, REGRAS_OBRIGATORIAS.md, pyproject.toml\n")
	L.append("└── engenharia/\n")
	L.append("    ├── hooks.py, boot.py, dashboard_api.py, agent_api.py, documents.py\n")
	L.append("    ├── financial.py, work_costs.py, report_visuals.py, titles.py, validators.py\n")
	L.append("    ├── dashboard/ (kpis, financial, budget_margin, deadlines, timeline, attention, health, …)\n")
	L.append("    ├── public/js/ (masks, list_nav, hub, reports_common, dashboard/*)\n")
	L.append("    ├── public/css/ (reports, hub, list_filters, sidebar_fix)\n")
	L.append("    ├── setup/ (install, sidebar, workspace, reports, print_formats, permissions, seed)\n")
	L.append("    ├── print_formats/reports/ (templates PDF Script Reports)\n")
	L.append("    └── engenharia/ (doctype/, report/, page/eng_dashboard/)\n")
	L.append("```\n\n")

	L.append("## 3. Script Reports\n\n")
	L.append(
		md_table(
			["Report", "Pasta", "Print formats"],
			[
				["work_cost_by_project", "Compras avulsas por obra", "Resumo"],
				["work_cost_by_category", "Compras avulsas por categoria", "Resumo"],
				["cash_flow", "Fluxo de Caixa", "Resumo + Paisagem"],
				["project_margin", "Margem por Obra", "Resumo + Paisagem"],
				["consolidated_cost", "Custos Realizados", "Resumo + Detalhado + Paisagem"],
				["budget_vs_actual", "Orçado vs Realizado", "Resumo + Paisagem"],
			],
		)
	)

	L.append("## 4. Mapa de DocTypes\n\n")
	for section, group in [
		("Standalone / transacionais", standalone),
		("Auxiliares (cadastro rígido)", auxiliary),
		("Child tables", child_tables),
		("Single", single),
	]:
		L.append(f"#### {section}\n\n")
		for name, d in sorted(group, key=lambda x: x[0]):
			L.append(render_dt(name, d))

	L.append("## 5. hooks.py (resumo)\n\n")
	L.append("### fixtures\n")
	L.append(
		"- Workspace `Engenharia`, Notification (4), Print Format (15), Custom Field Event `custom_source%`, "
		"Role (2), Kanban Board\n\n"
	)
	L.append("### app_include_css\n")
	for css in ("list_filters.css", "reports.css", "hub.css", "dashboard.css", "sidebar_fix.css"):
		L.append(f"- `/assets/engenharia/css/{css}`\n")
	L.append("\n### app_include_js\n")
	for js in (
		"masks.js",
		"list_nav.js",
		"list_filters.js",
		"customer_from_project.js",
		"documents_placeholders.js",
		"timer_global.js",
		"reports_common.js",
		"hub.js",
	):
		L.append(f"- `/assets/engenharia/js/{js}`\n")
	L.append("\n### boot_session\n")
	L.append("- `engenharia.boot.boot_session` → `bootinfo.eng_office` (logo, dados do escritório para print)\n\n")
	L.append("### scheduler_events\n")
	L.append(
		"- **daily:** check_overdue_installments, check_overdue_office_expenses, "
		"check_overdue_reimbursable_expenses, notify_deadlines_daily, notify_expiring_permits, "
		"notify_overdue_tasks, notify_overdue_payments\n"
		"- **weekly:** check_project_status_weekly\n\n"
	)
	L.append("### doc_events\n")
	L.append(
		"- Engineering Contract, Reimbursable Expense, Engineering Contract Installment, Payment, "
		"Deadline, Permit, Project Stage\n\n"
	)
	L.append("### after_migrate\n")
	L.append(
		"reinstall_child_doctypes → roles → ensure_event_custom_fields → permissions → seed → "
		"translations → sidebar → reports → print_formats → workspace\n\n"
	)

	L.append("## 6. API whitelisted (facade e principais)\n\n")
	L.append(
		md_table(
			["Função", "Módulo", "Permissão"],
			[
				["get_dashboard_data", "dashboard_api", "Construction Project read"],
				["mark_payment_received", "dashboard_api", "Payment write"],
				["mark_office_expense_paid", "dashboard_api", "Office Expense write"],
				["get_consolidated_costs", "engenharia.api.costs", "Construction Project read"],
				["get_project_hub_data", "project_hub", "Construction Project read"],
				["get_active_projects / get_project_summary", "agent_api", "Construction Project read"],
				["get_placeholder_reference", "documents", "Document Template read"],
				["bulk_delete_payments / resync / cancel", "financial", "Payment / Contract write"],
				["create_next_office_expense", "office_expense", "Office Expense create"],
				["apply_template_to_project", "stage_template", "Construction Project write"],
			],
		)
	)

	L.append("## 7. Testes\n\n")
	L.append(f"- **{test_methods}** métodos em **{test_files}** arquivos.\n")
	L.append("- `bench --site engenharia.local run-tests --app engenharia`\n\n")

	text = "".join(L)
	OUT_PATH.write_text(text, encoding="utf-8")
	count = text.count("\n### ")
	print(f"Wrote {OUT_PATH} ({len(text.splitlines())} lines, {count} DocType headers)")


if __name__ == "__main__":
	main()
