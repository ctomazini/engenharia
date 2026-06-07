"""Generate manual_usuario.md from DocType JSONs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DT_DIR = ROOT / "engenharia/engenharia/doctype"
OUT_PATH = ROOT / "engenharia/docs/manual_usuario.md"

DOCTYPE_ORDER = [
	("Cadastros", ["Customer", "Supplier", "Cost Category", "Public Agency", "Technical Item"]),
	("Obra (Hub)", ["Construction Project"]),
	(
		"Financeiro",
		["Engineering Contract", "Payment", "Work Cost", "Subcontract", "Reimbursable Expense", "Commission"],
	),
	("Acompanhamento", ["Deadline", "Permit", "Task", "Communication Log", "Time Log"]),
	("Documentos", ["Document Template", "Document Kit"]),
	("Configuração", ["Engineering Settings"]),
]

SKIP_TYPES = {"Section Break", "Column Break", "Tab Break", "HTML", "Fold"}


def _load_doctype(name: str) -> dict | None:
	folder = DT_DIR / name.lower().replace(" ", "_")
	jpath = folder / f"{folder.name}.json"
	if not jpath.exists():
		return None
	return json.loads(jpath.read_text(encoding="utf-8"))


def _render_fields(meta: dict) -> list[str]:
	lines = ["| Campo | Tipo | Obrigatório |", "| --- | --- | --- |"]
	for field in sorted(meta.get("fields", []), key=lambda x: x.get("idx") or 0):
		ft = field.get("fieldtype", "")
		if ft in SKIP_TYPES:
			continue
		lines.append(
			"| {label} (`{name}`) | {ft} | {reqd} |".format(
				label=field.get("label", ""),
				name=field.get("fieldname", ""),
				ft=ft,
				reqd="Sim" if field.get("reqd") else "",
			)
		)
	return lines


def main() -> None:
	lines = [
		"# Manual do Usuário — Engenharia\n",
		"> Gerado automaticamente por `engenharia/scripts/generate_manual.py`.\n",
	]
	for section, doctypes in DOCTYPE_ORDER:
		lines.append(f"\n## {section}\n")
		for dt in doctypes:
			meta = _load_doctype(dt)
			if not meta:
				continue
			lines.append(f"\n### {dt}\n")
			lines.extend(_render_fields(meta))
			lines.append("")

	OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
	print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
	main()
