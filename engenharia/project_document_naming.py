"""Composição de título e nome de arquivo para Project Document."""

from __future__ import annotations

import os
import re
import shutil
import unicodedata

import frappe
from frappe.core.doctype.file.utils import generate_file_name, get_safe_file_name
from frappe.utils import cint, get_files_path


def slug_part(value: str, fallback: str = "doc") -> str:
	if not value:
		return fallback
	normalized = unicodedata.normalize("NFKD", str(value))
	ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
	slug = re.sub(r"[^\w\-]+", "_", ascii_text.strip())
	slug = re.sub(r"_+", "_", slug).strip("_")
	return slug or fallback


def compose_project_document_title(
	project_name: str,
	category: str,
	version: str | None = None,
	title_descriptor: str | None = None,
) -> str:
	parts = [project_name or "", category or "Outro"]
	if version:
		parts.append(version)
	if title_descriptor and title_descriptor.strip():
		parts.append(title_descriptor.strip())
	return " — ".join(part for part in parts if part)


def compose_project_document_filename(
	project_name: str,
	category: str,
	version: str | None = None,
	title_descriptor: str | None = None,
	original_file_name: str = "",
) -> str:
	_, ext = os.path.splitext(original_file_name or "")
	ext = ext.lower()
	if not ext and original_file_name and original_file_name.startswith("."):
		ext = original_file_name.lower()
	if not ext:
		ext = ".pdf"
	parts = [
		slug_part(project_name, "obra"),
		slug_part(category, "outro"),
	]
	if version:
		parts.append(slug_part(version, "rev"))
	if title_descriptor and title_descriptor.strip():
		parts.append(slug_part(title_descriptor.strip(), "desc"))
	return "_".join(parts) + ext


def _file_url_for(file_name: str, is_private: int | bool) -> str:
	if cint(is_private):
		return f"/private/files/{file_name}"
	return f"/files/{file_name}"


def rename_attached_file(file_doc, new_file_name: str) -> str | None:
	"""Rename file on disk and sync File.file_name / file_url. Returns new URL if changed."""
	if not new_file_name:
		return None

	safe_name = get_safe_file_name(new_file_name)
	old_file_url = file_doc.file_url or ""

	if file_doc.exists_on_disk():
		current_basename = os.path.basename(file_doc.get_full_path())
	else:
		current_basename = old_file_url.split("/")[-1] if old_file_url else (file_doc.file_name or "")

	if current_basename == safe_name and file_doc.file_name == safe_name:
		return None

	is_private = cint(file_doc.is_private)
	unique_name = safe_name
	new_path = get_files_path(unique_name, is_private=is_private)

	if file_doc.exists_on_disk():
		old_path = file_doc.get_full_path()
		if os.path.realpath(old_path) != os.path.realpath(new_path):
			if os.path.exists(new_path):
				unique_name = generate_file_name(name=safe_name, is_private=is_private)
				new_path = get_files_path(unique_name, is_private=is_private)
			shutil.move(old_path, new_path)
	elif os.path.exists(new_path):
		unique_name = generate_file_name(name=safe_name, is_private=is_private)
		new_path = get_files_path(unique_name, is_private=is_private)

	new_file_url = _file_url_for(unique_name, is_private)

	file_doc.file_name = unique_name
	file_doc.file_url = new_file_url
	# sistema renomeia File filho após validação do documento pai
	file_doc.save(ignore_permissions=True)
	return new_file_url if new_file_url != old_file_url else None
