import frappe
from frappe import _
from frappe.utils import add_days, cint, get_first_day, get_last_day, today

from engenharia.dashboard import deadlines as dashboard_deadlines
from engenharia.dashboard import financial as dashboard_financial
from engenharia.dashboard import kpis as dashboard_kpis
from engenharia.dashboard import timeline as dashboard_timeline
from engenharia.dashboard._helpers import (
	LIST_LIMIT_MAX,
	_list_cap,
	_normalize_list_limits,
	_normalize_period_days,
)


def get(
	limit_start=0,
	limit_page_length=20,
	period_days=7,
	list_limit=5,
	list_limits=None,
):
	if not frappe.has_permission("Construction Project", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	limit_start = cint(limit_start)
	limit_page_length = min(cint(limit_page_length or 20), 100)
	period_days = _normalize_period_days(period_days)
	list_limits = _normalize_list_limits(list_limits, list_limit)

	hoje = today()
	period_end = add_days(hoje, period_days)
	month_start = get_first_day(hoje)
	month_end = get_last_day(hoje)

	kpis = dashboard_kpis.build_kpis(hoje, period_end, month_start, month_end)
	financeiro = dashboard_financial.build_financial(hoje, period_end, kpis)
	resumo = dashboard_kpis.build_summary(hoje, kpis, period_days)
	alertas = dashboard_deadlines.build_alerts(hoje, period_end)

	deadlines_cap = _list_cap(list_limits, "deadlines")
	tasks_cap = _list_cap(list_limits, "tasks")
	payments_cap = _list_cap(list_limits, "payments")
	timeline_cap = _list_cap(list_limits, "timeline")

	deadlines_all = dashboard_deadlines.get_deadlines(hoje, period_end, LIST_LIMIT_MAX)
	tasks_all = dashboard_timeline.get_tasks(hoje, LIST_LIMIT_MAX)
	payments_all = financeiro.get("pending_payments") or []
	timeline_full = dashboard_timeline.build_timeline(hoje, period_end, deadlines_all, tasks_all)

	return {
		"period_days": period_days,
		"list_limits": list_limits,
		"kpis": kpis,
		"resumo": resumo,
		"financeiro": financeiro,
		"alertas": alertas,
		"timeline": timeline_full[:timeline_cap],
		"deadlines": deadlines_all[:deadlines_cap],
		"tarefas": tasks_all[:tasks_cap],
		"pagamentos": payments_all[:payments_cap],
		"comunicacoes": dashboard_timeline.get_recent_communications(5),
		"horas": dashboard_timeline.get_hours_summary(hoje),
		"list_meta": {
			"timeline": {"showing": min(timeline_cap, len(timeline_full)), "total": len(timeline_full)},
			"pagamentos": {"showing": min(payments_cap, len(payments_all)), "total": len(payments_all)},
		},
	}
