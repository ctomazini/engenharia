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


def month_label(dt) -> str:
	dt = getdate(dt)
	return f"{MESES_PT[dt.month - 1]}/{dt.year}"


def short_label(text, max_len: int = 22) -> str:
	text = (text or "").strip()
	if len(text) <= max_len:
		return text
	return f"{text[: max_len - 1]}…"


def bar_chart(labels: list, datasets: list[dict], colors: list[str] | None = None) -> dict:
	chart = {
		"data": {"labels": [short_label(label, 32) for label in labels], "datasets": datasets},
		"type": "bar",
		"height": 280,
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
