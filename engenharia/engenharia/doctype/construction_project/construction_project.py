from frappe.model.document import Document

from engenharia.titles import apply_title_post_insert, recompose_title


class ConstructionProject(Document):
	def validate(self):
		self._compose_title()

	def _compose_title(self):
		recompose_title(self)

	def after_insert(self):
		apply_title_post_insert(self)
