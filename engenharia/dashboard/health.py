from frappe import _
from frappe.utils import flt


def build_operational_health(kpis, centro_atencao, financeiro):
	vencidos = (kpis.get("parcelas_vencidas") or {}).get("count") or 0
	prazos = (centro_atencao.get("prazos_vencidos") or 0) + (centro_atencao.get("prazos_proximos_3d") or 0)
	tarefas = (centro_atencao.get("tarefas_atrasadas") or 0) + min(
		centro_atencao.get("tarefas_pendentes") or 0, 5
	)
	penalty = vencidos * 12 + prazos * 6 + tarefas * 4
	taxa = flt(financeiro.get("taxa_recebimento") or kpis.get("taxa_recebimento") or 0)
	bonus = min(taxa / 5, 10)
	score = max(0, min(100, round(100 - penalty + bonus)))

	if score >= 85:
		tone = "green"
		label = _("Excelente")
	elif score >= 70:
		tone = "blue"
		label = _("Boa")
	elif score >= 50:
		tone = "orange"
		label = _("Atenção")
	else:
		tone = "red"
		label = _("Crítica")

	return {
		"score": score,
		"tone": tone,
		"label": label,
		"breakdown": [
			{"label": _("Parcelas vencidas"), "count": vencidos, "tone": "red" if vencidos else "green"},
			{"label": _("Prazos críticos"), "count": prazos, "tone": "orange" if prazos else "green"},
			{"label": _("Tarefas em risco"), "count": tarefas, "tone": "orange" if tarefas else "green"},
			{
				"label": _("Taxa de recebimento"),
				"count": f"{taxa}%",
				"tone": "green" if taxa >= 80 else "orange" if taxa >= 50 else "red",
			},
		],
	}
