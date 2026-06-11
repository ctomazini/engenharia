import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.project_document_naming import (
	compose_project_document_filename,
	compose_project_document_title,
	rename_attached_file,
)


class ProjectDocument(Document):
	def validate(self):
		self._sync_customer_from_project()
		self._compose_title()
		self._validate_permit_project()
		self._sync_file_name()

	def after_insert(self):
		self._sync_file_name(persist=True)

	def _sync_customer_from_project(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value(
				"Construction Project", self.project, "customer"
			)

	def _compose_title(self):
		self.title = compose_project_document_title(
			self.project,
			self.category,
			self.version,
			self.title_descriptor,
		)

	def _validate_permit_project(self):
		if not self.related_permit:
			return

		permit_project = frappe.db.get_value("Permit", self.related_permit, "project")
		if permit_project and permit_project != self.project:
			frappe.throw(
				_("O protocolo {0} pertence à obra {1}, não à obra {2}.").format(
					self.related_permit,
					permit_project,
					self.project,
				),
				title=_("Protocolo inválido"),
			)

	def _sync_file_name(self, persist: bool = False):
		if not self.file:
			return

		file_doc = frappe.get_doc("File", {"file_url": self.file})
		original_name = file_doc.file_name or self.file.split("/")[-1]
		new_name = compose_project_document_filename(
			self.project,
			self.category,
			self.version,
			self.title_descriptor,
			original_name,
		)
		new_file_url = rename_attached_file(file_doc, new_name)
		if not new_file_url:
			return

		self.file = new_file_url
		if persist and self.name:
			frappe.db.set_value(
				"Project Document",
				self.name,
				"file",
				new_file_url,
				update_modified=False,
			)
