"""Cores e helpers visuais para Script Reports do app engenharia."""

from __future__ import annotations

from frappe.utils import flt, getdate

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Paleta alinhada ao painel (semântica financeira / obra)
REPORT_COLORS = {
	"green": "#22c55e",
	"red": "#dc2626",
	"blue": "#2563eb",
	"orange": "#f97316",
	"amber": "#eab308",
	"teal": "#0d9488",
	"slate": "#64748b",
	"purple": "#7c3aed",
}

CASH_IN_OUT = [REPORT_COLORS["green"], REPORT_COLORS["red"]]

PROJECT_STATUS_COLORS = {
	"Orçamento": REPORT_COLORS["blue"],
	"Em andamento": REPORT_COLORS["teal"],
	"Paralisada": REPORT_COLORS["amber"],
	"Concluída": REPORT_COLORS["green"],
	"Cancelada": REPORT_COLORS["slate"],
}


def month_label(dt) -> str:
	dt = getdate(dt)
	return f"{MESES_PT[dt.month - 1]}/{dt.year}"


def bar_chart(labels: list, datasets: list[dict], colors: list[str] | None = None) -> dict:
	chart = {
		"data": {"labels": labels, "datasets": datasets},
		"type": "bar",
	}
	if colors:
		chart["colors"] = colors
	return chart


def donut_chart(labels: list, values: list, colors: list[str] | None = None) -> dict:
	chart = {
		"data": {"labels": labels, "datasets": [{"values": values}]},
		"type": "donut",
	}
	if colors:
		chart["colors"] = colors
	return chart


def currency_summary(value: float, label: str, indicator: str) -> dict:
	return {
		"value": flt(value),
		"label": label,
		"datatype": "Currency",
		"indicator": indicator,
	}


def int_summary(value: int, label: str, indicator: str = "Blue") -> dict:
	return {
		"value": int(value),
		"label": label,
		"datatype": "Int",
		"indicator": indicator,
	}


def percent_summary(value: float, label: str, indicator: str = "Blue") -> dict:
	return {
		"value": flt(value),
		"label": label,
		"datatype": "Percent",
		"indicator": indicator,
	}
