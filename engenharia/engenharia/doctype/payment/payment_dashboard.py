from frappe import _


def get_data():
	return {
		"internal_links": {
			"Construction Project": "project",
			"Engineering Contract": "contract",
		},
		"transactions": [
			{
				"label": _("Obra"),
				"items": ["Construction Project"],
			},
			{
				"label": _("Contrato"),
				"items": ["Engineering Contract"],
			},
		],
	}
