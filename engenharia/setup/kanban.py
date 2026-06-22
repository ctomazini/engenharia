import frappe


def ensure_engenharia_kanban_board():
	"""Sincroniza label UI do Kanban de tarefas (slug interno permanece Engenharia Obras)."""
	if not frappe.db.exists("Kanban Board", "Engenharia Obras"):
		return

	current = frappe.db.get_value("Kanban Board", "Engenharia Obras", "kanban_board_name")
	if current == "Tarefas da Obra":
		return

	frappe.db.set_value(
		"Kanban Board",
		"Engenharia Obras",
		"kanban_board_name",
		"Tarefas da Obra",
		update_modified=False,
	)
	frappe.db.commit()  # setup: sincroniza label do Kanban no migrate
