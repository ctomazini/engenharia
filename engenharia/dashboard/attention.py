from frappe import _
from frappe.utils import add_days, cint, flt


def _tile(count, tone, icon, label, deep_link, meta=None, meta_currency=None, pulse=False):
	return {
		"count": cint(count),
		"tone": tone,
		"icon": icon,
		"label": label,
		"deep_link": deep_link,
		"meta": meta,
		"meta_currency": meta_currency,
		"pulse": bool(pulse and cint(count)),
	}


def _prazos_tile(overdue, urgent, hoje, three_days):
	total = cint(overdue) + cint(urgent)
	if not total:
		return None
	meta = _("{0} vencidos · {1} em 3 dias").format(cint(overdue), cint(urgent))
	tone = "red" if overdue else "orange"
	if overdue:
		filters = [["status", "=", "Pendente"], ["due_date", "<", hoje]]
	else:
		filters = [["status", "=", "Pendente"], ["due_date", "between", [hoje, three_days]]]
	return _tile(
		total,
		tone,
		"alarm-clock",
		_("Prazos"),
		{"doctype": "Deadline", "filters": filters},
		meta=meta,
		pulse=True,
	)


def _protocolos_tile(permits_hoje, permits_amanha, hoje, tomorrow):
	total = cint(permits_hoje) + cint(permits_amanha)
	if not total:
		return None
	meta = _("{0} hoje · {1} amanhã").format(cint(permits_hoje), cint(permits_amanha))
	tone = "orange" if permits_hoje else "yellow"
	filters = (
		[["protocol_date", "=", hoje], ["status", "not in", ["Cancelado"]]]
		if permits_hoje
		else [["protocol_date", "=", tomorrow], ["status", "not in", ["Cancelado"]]]
	)
	return _tile(
		total,
		tone,
		"clipboard-check",
		_("Alvarás e Protocolos"),
		{"doctype": "Permit", "filters": filters},
		meta=meta,
		pulse=True,
	)


def build_attention_tiles(hoje, period_end, period_days, kpis, financeiro, include_financial=True):
	del period_end, period_days, financeiro

	tomorrow = add_days(hoje, 1)
	three_days = add_days(hoje, 3)
	parcelas_vencidas = kpis.get("parcelas_vencidas") or {"count": 0, "valor": 0}
	pending_work_costs = kpis.get("pending_work_costs") or {"count": 0, "amount": 0}
	overdue_deadlines = cint(kpis.get("overdue_deadlines") or 0)
	urgent_deadlines = cint(kpis.get("urgent_deadlines") or 0)
	late_tasks = cint(kpis.get("late_tasks") or 0)
	permits_hoje = cint(kpis.get("permits_today") or 0)
	permits_amanha = cint(kpis.get("permits_tomorrow") or 0)

	candidates = [
		_prazos_tile(overdue_deadlines, urgent_deadlines, hoje, three_days),
		_tile(
			late_tasks,
			"orange",
			"list-todo",
			_("Tarefas atrasadas"),
			{
				"doctype": "Task",
				"filters": [["status", "in", ["A fazer", "Fazendo"]], ["due_date", "<", hoje]],
			},
			pulse=True,
		)
		if late_tasks
		else None,
		_tile(
			parcelas_vencidas.get("count") or 0,
			"red",
			"circle-dollar-sign",
			_("Parcelas vencidas"),
			{"doctype": "Payment", "filters": [["status", "=", "Vencido"]]},
			meta_currency=flt(parcelas_vencidas.get("valor")),
			pulse=True,
		)
		if include_financial and cint(parcelas_vencidas.get("count") or 0)
		else None,
		_protocolos_tile(permits_hoje, permits_amanha, hoje, tomorrow),
		_tile(
			pending_work_costs.get("count") or 0,
			"orange",
			"receipt",
			_("Custos pendentes"),
			{
				"doctype": "Work Cost",
				"filters": [["status", "in", ["Open", "Partially Paid"]], ["funded_by", "=", "Escritório"]],
			},
			meta_currency=flt(pending_work_costs.get("amount")),
			pulse=True,
		)
		if include_financial and cint(pending_work_costs.get("count") or 0)
		else None,
	]

	tiles = [tile for tile in candidates if tile]
	all_clear = not tiles

	return {
		"tiles": tiles,
		"all_clear": all_clear,
		"empty_label": _("Nada exige ação agora"),
		"ok_summary": _("Resto em dia ✓"),
	}
