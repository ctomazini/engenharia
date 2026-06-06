import click
import frappe
from frappe.commands import pass_context


@click.command("seed-demo")
@click.option("--site", required=True, help="Site name")
@pass_context
def seed_demo(context, site):
	"""Popula o site com dados de demonstração realistas."""
	frappe.init(site=site)
	frappe.connect()
	from engenharia.setup.demo_data import setup

	setup()
	frappe.db.commit()
	frappe.destroy()
	click.echo("✅ Demo data criada com sucesso.")


@click.command("clear-demo")
@click.option("--site", required=True, help="Site name")
@pass_context
def clear_demo(context, site):
	"""Remove todos os dados de demonstração."""
	frappe.init(site=site)
	frappe.connect()
	from engenharia.setup.demo_data import teardown

	teardown()
	frappe.db.commit()
	frappe.destroy()
	click.echo("🗑️ Demo data removida.")


commands = [seed_demo, clear_demo]
