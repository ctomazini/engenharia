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


def _period_receivable_label(period_days):
	if period_days == 1:
		return _("A receber hoje")
	return _("A receber no período")


def _period_received_label(period_days):
	return _("Recebidos no período")


def build_attention_tiles(hoje, period_end, period_days, kpis, financeiro):
	tomorrow = add_days(hoje, 1)
	three_days = add_days(hoje, 3)
	previsto = financeiro.get("previsto_periodo") or {"count": 0, "valor": 0}
	parcelas_vencidas = kpis.get("parcelas_vencidas") or {"count": 0, "valor": 0}
	recebidos = kpis.get("received_period") or {"count": 0, "amount": 0}
	pending_work_costs = kpis.get("pending_work_costs") or {"count": 0, "amount": 0}
	permits_hoje = kpis.get("permits_today") or 0
	permits_amanha = kpis.get("permits_tomorrow") or 0

	urgent = [
		_tile(
			kpis.get("overdue_deadlines") or 0,
			"red",
			"alarm-clock",
			_("Prazos vencidos"),
			{
				"doctype": "Deadline",
				"filters": [["status", "=", "Pendente"], ["due_date", "<", hoje]],
			},
			pulse=True,
		),
		_tile(
			kpis.get("urgent_deadlines") or 0,
			"orange",
			"timer",
			_("Prazos em 3 dias"),
			{
				"doctype": "Deadline",
				"filters": [["status", "=", "Pendente"], ["due_date", "between", [hoje, three_days]]],
			},
			pulse=True,
		),
		_tile(
			kpis.get("late_tasks") or 0,
			"orange",
			"list-todo",
			_("Tarefas atrasadas"),
			{
				"doctype": "Task",
				"filters": [["status", "in", ["A fazer", "Fazendo"]], ["due_date", "<", hoje]],
			},
			pulse=True,
		),
		_tile(
			parcelas_vencidas.get("count") or 0,
			"red",
			"circle-dollar-sign",
			_("Parcelas vencidas"),
			{"doctype": "Payment", "filters": [["status", "=", "Vencido"]]},
			meta_currency=flt(parcelas_vencidas.get("valor")),
			pulse=True,
		),
		_tile(
			permits_hoje,
			"orange",
			"clipboard-check",
			_("Protocolos hoje"),
			{
				"doctype": "Permit",
				"filters": [["protocol_date", "=", hoje], ["status", "not in", ["Cancelado"]]],
			},
			pulse=permits_hoje > 0,
		),
		_tile(
			permits_amanha,
			"yellow",
			"calendar-clock",
			_("Protocolos amanhã"),
			{
				"doctype": "Permit",
				"filters": [["protocol_date", "=", tomorrow], ["status", "not in", ["Cancelado"]]],
			},
			pulse=permits_amanha > 0,
		),
		_tile(
			pending_work_costs.get("count") or 0,
			"orange",
			"receipt",
			_("Custos pendentes"),
			{"doctype": "Work Cost", "filters": [["status", "=", "Pendente"]]},
			meta_currency=flt(pending_work_costs.get("amount")),
			pulse=(pending_work_costs.get("count") or 0) > 0,
		),
	]

	period = [
		_tile(
			previsto.get("count") or 0,
			"orange",
			"wallet",
			_period_receivable_label(period_days),
			{
				"doctype": "Payment",
				"filters": [["status", "=", "Pendente"], ["due_date", "between", [hoje, period_end]]],
			},
			meta_currency=flt(previsto.get("valor")),
		),
		_tile(
			recebidos.get("count") or 0,
			"green",
			"trending-up",
			_period_received_label(period_days),
			{
				"doctype": "Payment",
				"filters": [["status", "=", "Recebido"], ["received_date", "between", [hoje, period_end]]],
			},
			meta_currency=flt(recebidos.get("amount")),
		),
	]

	for tile in urgent:
		if tile["count"] == 0 and tile["tone"] in ("red", "orange", "yellow"):
			tile["tone"] = "green"
			tile["pulse"] = False

	return {
		"urgent": urgent,
		"period": period,
		"tiles": urgent + period,
	}
