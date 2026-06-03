import frappe
from frappe import _
from frappe.utils import add_days, cint, get_first_day, get_last_day, today

from engenharia.dashboard import agenda as dashboard_agenda
from engenharia.dashboard import attention as dashboard_attention
from engenharia.dashboard import deadlines as dashboard_deadlines
from engenharia.dashboard import financial as dashboard_financial
from engenharia.dashboard import health as dashboard_health
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
	periodo_dias=None,
	list_limit=5,
	list_limits=None,
):
	if not frappe.has_permission("Construction Project", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	limit_start = cint(limit_start)
	limit_page_length = min(cint(limit_page_length or 20), 100)
	period_days = _normalize_period_days(periodo_dias if periodo_dias is not None else period_days)
	list_limits = _normalize_list_limits(list_limits, list_limit)

	hoje = today()
	period_end = add_days(hoje, period_days)
	month_start = get_first_day(hoje)
	month_end = get_last_day(hoje)

	kpis = dashboard_kpis.build_kpis(hoje, period_end, month_start, month_end)
	financeiro = dashboard_financial.build_financial(hoje, period_end, kpis)
	resumo = dashboard_kpis.build_summary(hoje, kpis, period_days)
	alertas = dashboard_deadlines.build_alerts(hoje, period_end)
	centro_atencao = dashboard_deadlines.build_centro_atencao(hoje, period_end, kpis, financeiro)
	atencao = dashboard_attention.build_attention_tiles(hoje, period_end, period_days, kpis, financeiro)
	saude_operacional = dashboard_health.build_operational_health(kpis, centro_atencao, financeiro)

	deadlines_cap = _list_cap(list_limits, "deadlines")
	tasks_cap = _list_cap(list_limits, "tasks")
	payments_cap = _list_cap(list_limits, "payments")
	parcelas_cap = _list_cap(list_limits, "parcelas")
	despesas_cap = _list_cap(list_limits, "despesas")
	timeline_cap = _list_cap(list_limits, "timeline")
	comunicacoes_cap = _list_cap(list_limits, "comunicacoes")

	deadlines_all = dashboard_deadlines.get_deadlines(hoje, period_end, LIST_LIMIT_MAX)
	tasks_all = dashboard_timeline.get_tasks(hoje, LIST_LIMIT_MAX)
	payments_all = financeiro.get("pending_payments") or []
	parcelas_all = payments_all
	despesas_all = dashboard_financial.get_pending_reimbursables(LIST_LIMIT_MAX)
	agenda_full = dashboard_agenda.build_agenda(hoje, period_end, deadlines_all, tasks_all, payments_all)
	agenda_days = dashboard_agenda.build_day_strip(hoje, period_days, agenda_full)
	comunicacoes_all = dashboard_timeline.get_recent_communications(LIST_LIMIT_MAX)

	horas_semana = dashboard_timeline.get_hours_summary(hoje)
	horas_periodo = dashboard_timeline.get_hours_period(hoje, period_end)
	total_despesas_mes = dashboard_financial.get_total_reimbursables_month(month_start, month_end)

	list_meta = {
		"timeline": {"showing": min(timeline_cap, len(agenda_full)), "total": len(agenda_full)},
		"pagamentos": {"showing": min(payments_cap, len(payments_all)), "total": len(payments_all)},
		"parcelas": {"showing": min(parcelas_cap, len(parcelas_all)), "total": len(parcelas_all)},
		"despesas": {"showing": min(despesas_cap, len(despesas_all)), "total": len(despesas_all)},
		"comunicacoes": {
			"showing": min(comunicacoes_cap, len(comunicacoes_all)),
			"total": len(comunicacoes_all),
		},
		"deadlines": {"showing": min(deadlines_cap, len(deadlines_all)), "total": len(deadlines_all)},
		"tasks": {"showing": min(tasks_cap, len(tasks_all)), "total": len(tasks_all)},
	}

	return {
		"period_days": period_days,
		"periodo_dias": period_days,
		"list_limit": list_limits.get("timeline", 5),
		"list_limits": list_limits,
		"list_meta": list_meta,
		"kpis": kpis,
		"resumo": resumo,
		"financeiro": financeiro,
		"alertas": alertas,
		"centro_atencao": centro_atencao,
		"atencao": atencao,
		"saude_operacional": saude_operacional,
		"agenda_days": agenda_days,
		"timeline": agenda_full[:timeline_cap],
		"agenda": agenda_full[:timeline_cap],
		"parcelas": parcelas_all[:parcelas_cap],
		"pagamentos": payments_all[:payments_cap],
		"despesas_pendentes": despesas_all[:despesas_cap],
		"total_despesas_mes": total_despesas_mes,
		"comunicacoes_pendentes": comunicacoes_all[:comunicacoes_cap],
		"ultimas_comunicacoes": comunicacoes_all[:comunicacoes_cap],
		"horas_semana": horas_semana,
		"horas_periodo": horas_periodo,
		"horas": horas_semana,
		"deadlines": deadlines_all[:deadlines_cap],
		"prazos": deadlines_all[:deadlines_cap],
		"tarefas": tasks_all[:tasks_cap],
	}
