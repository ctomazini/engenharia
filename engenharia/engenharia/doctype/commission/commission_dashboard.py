from frappe import _


def get_data():
	return {
		"internal_links": {
			"Construction Project": "construction_project",
		},
		"transactions": [
			{
				"label": _("Obra"),
				"items": ["Construction Project"],
			},
		],
	}
