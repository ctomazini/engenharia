#!/usr/bin/env node
/**
 * Sessão E2E Playwright — app engenharia.
 * Login + navegação UI; criação via frappe.db.insert no contexto autenticado do Desk.
 * (Frappe v16 headless não expõe cur_frm — API client-side é o caminho estável.)
 */
import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const E2E_ROOT = path.dirname(fileURLToPath(import.meta.url));

const BASE = process.env.E2E_BASE_URL || "http://127.0.0.1:8000";
const SITE_HOST = process.env.E2E_SITE_HOST || "engenharia.local";
const USER = process.env.E2E_USER || "Administrator";
const PASS = process.env.E2E_PASS || "playwright_e2e_test";
const RUN_ID = Date.now().toString(36);
const MARKER = `PLAYWRIGHT_${RUN_ID}`;
const DOCX = process.env.E2E_DOCX || path.join(E2E_ROOT, "fixtures", "template.docx");

const OUT_DIR = process.env.E2E_OUT_DIR || path.join(E2E_ROOT, "results", RUN_ID);
fs.mkdirSync(OUT_DIR, { recursive: true });

const results = [];

function log(step, status, detail = "") {
	results.push({ step, status, detail, at: new Date().toISOString() });
	console.log(`${status === "ok" ? "✓" : status === "skip" ? "○" : "✗"} ${step}${detail ? ` — ${detail}` : ""}`);
}

function calcCpfDv(base) {
	let sum = 0;
	for (let i = 0; i < 9; i++) sum += parseInt(base[i], 10) * (10 - i);
	let d1 = 11 - (sum % 11);
	if (d1 >= 10) d1 = 0;
	sum = 0;
	const b10 = base + d1;
	for (let i = 0; i < 10; i++) sum += parseInt(b10[i], 10) * (11 - i);
	let d2 = 11 - (sum % 11);
	if (d2 >= 10) d2 = 0;
	return `${d1}${d2}`;
}

function randomCpf() {
	let base;
	do {
		base = Array.from({ length: 9 }, () => Math.floor(Math.random() * 10)).join("");
	} while (new Set(base).size === 1);
	return base + calcCpfDv(base);
}

function calcCnpjDv(base) {
	const w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
	const w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
	let sum = 0;
	for (let i = 0; i < 12; i++) sum += parseInt(base[i], 10) * w1[i];
	let d1 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
	sum = 0;
	const b13 = base + d1;
	for (let i = 0; i < 13; i++) sum += parseInt(b13[i], 10) * w2[i];
	let d2 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
	return `${d1}${d2}`;
}

function randomCnpj() {
	let base;
	do {
		base = Array.from({ length: 12 }, () => Math.floor(Math.random() * 10)).join("");
	} while (new Set(base).size === 1);
	return base + calcCnpjDv(base);
}

function slug(doctype) {
	return doctype.toLowerCase().replace(/ /g, "-");
}

async function waitDesk(page) {
	await page.waitForFunction(() => window.frappe?.boot && frappe.session?.user !== "Guest", null, {
		timeout: 60000,
	});
	await page.waitForTimeout(400);
}

async function visitNewForm(page, doctype) {
	await page.goto(`${BASE}/app/${slug(doctype)}/new`, { waitUntil: "domcontentloaded" });
	await waitDesk(page);
	await page.waitForSelector(".form-layout", { timeout: 60000 });
}

async function visitDoc(page, doctype, name) {
	await page.goto(`${BASE}/app/${slug(doctype)}/${encodeURIComponent(name)}`, {
		waitUntil: "domcontentloaded",
	});
	await waitDesk(page);
	await page.waitForSelector(".form-layout, .layout-main", { timeout: 60000 });
}

async function uploadDocx(page, filePath, fileName) {
	const b64 = fs.readFileSync(filePath).toString("base64");
	return page.evaluate(
		async ([content, name]) => {
			const file = new File(
				[Uint8Array.from(atob(content), (c) => c.charCodeAt(0))],
				name,
				{ type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }
			);
			const fd = new FormData();
			fd.append("file", file);
			fd.append("is_private", "0");
			fd.append("folder", "Home");
			const resp = await fetch("/api/method/upload_file", {
				method: "POST",
				body: fd,
				headers: { "X-Frappe-CSRF-Token": frappe.csrf_token },
			});
			const json = await resp.json();
			if (!json.message?.file_url) {
				throw new Error(json._server_messages || "Falha no upload");
			}
			return json.message.file_url;
		},
		[b64, fileName]
	);
}

async function insertDoc(page, doc, resave = false) {
	const result = await page.evaluate(
		async ([payload, needsResave]) => {
			try {
				const inserted = await frappe.db.insert(payload);
				if (needsResave) {
					const full = await frappe.db.get_doc(payload.doctype, inserted.name);
					await frappe.call("frappe.client.save", { doc: full });
				}
				return { ok: true, name: inserted.name };
			} catch (e) {
				return {
					ok: false,
					error: e?.message || e?.exc || String(e),
					server: frappe.last_response?._server_messages || "",
				};
			}
		},
		[doc, resave]
	);
	if (!result?.ok) {
		throw new Error(`${result?.error || "insert failed"} ${result?.server || ""}`.trim());
	}
	return result.name;
}

async function runStep(page, name, fn) {
	try {
		const detail = await fn();
		log(name, "ok", detail || "");
		return true;
	} catch (err) {
		log(name, "fail", (err?.message || String(err)).slice(0, 280));
		await page.screenshot({ path: path.join(OUT_DIR, `${name.replace(/\W+/g, "_")}.png`), fullPage: true }).catch(() => {});
		return false;
	}
}

async function main() {
	const browser = await chromium.launch({ headless: true });
	const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
	await page.route("**/*", async (route) => {
		await route.continue({ headers: { ...route.request().headers(), host: SITE_HOST } });
	});

	const state = {
		customerName: `${MARKER} Cliente PF`,
		projectName: null,
		supplierName: `${MARKER} Fornecedor`,
		costCategory: `${MARKER} Materiais`,
		stageType: `${MARKER} Fundação`,
		permitType: `${MARKER} Alvará`,
		publicAgency: `${MARKER} Prefeitura`,
		technicalItem: `${MARKER} Concreto`,
		documentTemplate: `${MARKER} Template ART`,
		documentKit: `${MARKER} Kit Obra`,
		projectStageName: null,
		projectItemName: null,
		contractName: null,
		customerId: null,
		customerCpf: randomCpf(),
		supplierCnpj: randomCnpj(),
	};
	const due1 = new Date(Date.now() + 86400000 * 30).toISOString().slice(0, 10);
	const due2 = new Date(Date.now() + 86400000 * 60).toISOString().slice(0, 10);

	await runStep(page, "login", async () => {
		await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
		await page.fill("#login_email", USER);
		await page.fill("#login_password", PASS);
		await page.click(".btn-login");
		await page.waitForURL(/\/(app|desk)/, { timeout: 60000 });
		await waitDesk(page);
		return USER;
	});

	await runStep(page, "cost-category", async () => {
		await visitNewForm(page, "Cost Category");
		const name = await insertDoc(page, { doctype: "Cost Category", category_name: state.costCategory });
		await visitDoc(page, "Cost Category", name);
		return name;
	});

	await runStep(page, "stage-type", async () => {
		await visitNewForm(page, "Stage Type");
		const name = await insertDoc(page, {
			doctype: "Stage Type",
			stage_name: state.stageType,
			default_order: 1,
		});
		await visitDoc(page, "Stage Type", name);
		return name;
	});

	await runStep(page, "permit-type", async () => {
		await visitNewForm(page, "Permit Type");
		const name = await insertDoc(page, { doctype: "Permit Type", type_name: state.permitType });
		await visitDoc(page, "Permit Type", name);
		return name;
	});

	await runStep(page, "public-agency", async () => {
		await visitNewForm(page, "Public Agency");
		const name = await insertDoc(page, {
			doctype: "Public Agency",
			agency_name: state.publicAgency,
			sphere: "Municipal",
			city: "Porto Alegre",
		});
		await visitDoc(page, "Public Agency", name);
		return name;
	});

	await runStep(page, "supplier", async () => {
		await visitNewForm(page, "Supplier");
		const name = await insertDoc(page, {
			doctype: "Supplier",
			supplier_name: state.supplierName,
			cnpj: state.supplierCnpj,
			category: "Material",
		});
		await visitDoc(page, "Supplier", name);
		return name;
	});

	await runStep(page, "document-template", async () => {
		if (!fs.existsSync(DOCX)) throw new Error(`docx ausente: ${DOCX}`);
		await visitNewForm(page, "Document Template");
		const fileUrl = await uploadDocx(page, DOCX, "playwright-template.docx");
		const name = await insertDoc(page, {
			doctype: "Document Template",
			template_name: state.documentTemplate,
			document_type: "Relatório",
			description: `${MARKER} template E2E`,
			document_file: fileUrl,
			enabled: 1,
		});
		await visitDoc(page, "Document Template", name);
		return name;
	});

	await runStep(page, "technical-item", async () => {
		await visitNewForm(page, "Technical Item");
		const name = await insertDoc(page, {
			doctype: "Technical Item",
			item_name: state.technicalItem,
			category: "Estrutural",
			data_type: "Número",
			default_unit: "m³",
			fields: [
				{
					doctype: "Technical Item Field",
					field_key: "volume",
					label: "Volume",
					data_type: "Número",
					sort_order: 1,
				},
			],
		});
		await visitDoc(page, "Technical Item", name);
		return name;
	});

	await runStep(page, "customer", async () => {
		await visitNewForm(page, "Customer");
		state.customerId = await insertDoc(page, {
			doctype: "Customer",
			person_type: "Pessoa Física",
			customer_name: state.customerName,
			cpf: state.customerCpf,
		});
		await visitDoc(page, "Customer", state.customerId);
		return state.customerId;
	});

	await runStep(page, "construction-project", async () => {
		await visitNewForm(page, "Construction Project");
		state.projectName = await insertDoc(page, {
			doctype: "Construction Project",
			customer: state.customerId,
			city: "Porto Alegre",
			status: "Em andamento",
			observations: `${MARKER} obra E2E`,
		});
		await visitDoc(page, "Construction Project", state.projectName);
		return state.projectName;
	});

	await runStep(page, "project-stage", async () => {
		await visitNewForm(page, "Project Stage");
		state.projectStageName = await insertDoc(page, {
			doctype: "Project Stage",
			project: state.projectName,
			stage_type: state.stageType,
			status: "Em andamento",
			progress: 30,
			stage_value: 25000,
			order: 1,
		});
		await visitDoc(page, "Project Stage", state.projectStageName);
		return state.projectStageName;
	});

	await runStep(page, "project-item", async () => {
		await visitNewForm(page, "Project Item");
		state.projectItemName = await page.evaluate(
			async ([project, technicalItem, label, stage]) => {
				try {
					return await frappe
						.call({
							method: "engenharia.engenharia.doctype.construction_project.construction_project.create_project_item",
							args: {
								project,
								technical_item: technicalItem,
								instance_label: label,
								stage,
							},
						})
						.then((r) => r.message);
				} catch (e) {
					throw new Error(e?.message || frappe.last_response?._server_messages || String(e));
				}
			},
			[state.projectName, state.technicalItem, `${MARKER} Laje térreo`, state.projectStageName]
		);
		await visitDoc(page, "Project Item", state.projectItemName);
		return state.projectItemName;
	});

	await runStep(page, "engineering-contract", async () => {
		await visitNewForm(page, "Engineering Contract");
		state.contractName = await insertDoc(
			page,
			{
				doctype: "Engineering Contract",
				project: state.projectName,
				base_value: 50000,
				current_value: 50000,
				first_installment_date: due1,
				installment_count: 2,
				observations: `${MARKER} contrato honorários`,
				installments: [
					{
						doctype: "Engineering Contract Installment",
						due_date: due1,
						amount: 25000,
						description: `${MARKER} parcela 1`,
						status: "Pendente",
					},
					{
						doctype: "Engineering Contract Installment",
						due_date: due2,
						amount: 25000,
						description: `${MARKER} parcela 2`,
						status: "Pendente",
					},
				],
			},
			true
		);
		await visitDoc(page, "Engineering Contract", state.contractName);
		return state.contractName;
	});

	await runStep(page, "payment-sync", async () => {
		const count = await page.evaluate(async (project) => {
			const rows = await frappe.db.get_list("Payment", {
				filters: { project },
				fields: ["name"],
				limit: 20,
			});
			return rows.length;
		}, state.projectName);
		if (count < 1) throw new Error(`Nenhum Payment para ${state.projectName}`);
		await page.goto(`${BASE}/app/payment?project=${encodeURIComponent(state.projectName)}`, {
			waitUntil: "domcontentloaded",
		});
		await waitDesk(page);
		return `${count} pagamento(s)`;
	});

	await runStep(page, "commission", async () => {
		await visitNewForm(page, "Commission");
		const name = await insertDoc(page, {
			doctype: "Commission",
			construction_project: state.projectName,
			commission_type: "Pré-Moldado",
			supplier_name: state.supplierName,
			description: `${MARKER} comissão fornecedor`,
			total_value: 5000,
		});
		await visitDoc(page, "Commission", name);
		return name;
	});

	await runStep(page, "subcontract", async () => {
		await visitNewForm(page, "Subcontract");
		const name = await insertDoc(page, {
			doctype: "Subcontract",
			project: state.projectName,
			supplier: state.supplierName,
			funded_by: "Escritório",
			cost_category: state.costCategory,
			total_value: 8000,
			description: `${MARKER} Serviço pedreiro`,
		});
		await visitDoc(page, "Subcontract", name);
		return name;
	});

	await runStep(page, "work-cost", async () => {
		await visitNewForm(page, "Work Cost");
		const name = await insertDoc(page, {
			doctype: "Work Cost",
			project: state.projectName,
			funded_by: "Escritório",
			cost_category: state.costCategory,
			supplier: state.supplierName,
			amount: 1500,
			description: `${MARKER} Compra material`,
			status: "Pago",
		});
		await visitDoc(page, "Work Cost", name);
		return name;
	});

	await runStep(page, "reimbursable-expense", async () => {
		await visitNewForm(page, "Reimbursable Expense");
		const name = await insertDoc(page, {
			doctype: "Reimbursable Expense",
			project: state.projectName,
			cost_category: state.costCategory,
			amount: 350,
			description: `${MARKER} Taxa cartório`,
			status: "A reembolsar",
		});
		await visitDoc(page, "Reimbursable Expense", name);
		return name;
	});

	await runStep(page, "permit", async () => {
		await visitNewForm(page, "Permit");
		const name = await insertDoc(page, {
			doctype: "Permit",
			project: state.projectName,
			permit_type: state.permitType,
			public_agency: state.publicAgency,
			permit_number: `AC-${RUN_ID}`,
			status: "Em análise",
			protocol_date: new Date().toISOString().slice(0, 10),
		});
		await visitDoc(page, "Permit", name);
		return name;
	});

	await runStep(page, "deadline", async () => {
		await visitNewForm(page, "Deadline");
		const name = await insertDoc(page, {
			doctype: "Deadline",
			project: state.projectName,
			description: `${MARKER} Prazo ART`,
			due_date: new Date(Date.now() + 86400000 * 14).toISOString().slice(0, 10),
			deadline_type: "Projeto",
		});
		await visitDoc(page, "Deadline", name);
		return name;
	});

	await runStep(page, "task", async () => {
		await visitNewForm(page, "Task");
		const name = await insertDoc(page, {
			doctype: "Task",
			subject: `${MARKER} Tarefa visita obra`,
			project: state.projectName,
			status: "A fazer",
		});
		await visitDoc(page, "Task", name);
		return name;
	});

	await runStep(page, "construction-measurement", async () => {
		await visitNewForm(page, "Construction Measurement");
		const name = await insertDoc(page, {
			doctype: "Construction Measurement",
			project: state.projectName,
			measurement_date: new Date().toISOString().slice(0, 10),
			reference_period: "Junho/2026",
			measurement_items: [
				{
					doctype: "Construction Measurement Item",
					project_stage: state.projectStageName,
					current_pct: 35,
				},
			],
		});
		await visitDoc(page, "Construction Measurement", name);
		return name;
	});

	await runStep(page, "time-log", async () => {
		await visitNewForm(page, "Time Log");
		const name = await insertDoc(page, {
			doctype: "Time Log",
			project: state.projectName,
			activity: `${MARKER} Visita técnica`,
			duration_minutes: 120,
		});
		await visitDoc(page, "Time Log", name);
		return name;
	});

	await runStep(page, "communication-log", async () => {
		await visitNewForm(page, "Communication Log");
		const name = await insertDoc(page, {
			doctype: "Communication Log",
			project: state.projectName,
			subject: `${MARKER} Alinhamento com cliente`,
			communication_type: "WhatsApp",
			summary: "Cliente confirmou cronograma.",
		});
		await visitDoc(page, "Communication Log", name);
		return name;
	});

	await runStep(page, "document-kit", async () => {
		await visitNewForm(page, "Document Kit");
		const name = await insertDoc(page, {
			doctype: "Document Kit",
			kit_name: state.documentKit,
			description: `${MARKER} kit documentos obra`,
			templates: [
				{
					doctype: "Document Kit Item",
					document_template: state.documentTemplate,
					sort_order: 1,
				},
			],
		});
		await visitDoc(page, "Document Kit", state.documentKit);
		return name;
	});

	await runStep(page, "dashboard", async () => {
		await page.goto(`${BASE}/app/eng-dashboard`, { waitUntil: "domcontentloaded" });
		await waitDesk(page);
		await page.waitForSelector(".eng-dash-root", { timeout: 90000 });
		await page.waitForSelector(".eng-dash-content", { timeout: 90000 });
		return "eng-dashboard OK";
	});

	await browser.close();

	const passed = results.filter((r) => r.status === "ok").length;
	const failed = results.filter((r) => r.status === "fail").length;
	const summary = { marker: MARKER, passed, failed, total: results.length, results, state };
	fs.writeFileSync(path.join(OUT_DIR, "summary.json"), JSON.stringify(summary, null, 2));
	console.log(
		`\n--- RESUMO ---\nMarcador: ${MARKER}\nPassou: ${passed}/${results.length} | Falhou: ${failed}\nRelatório: ${path.join(OUT_DIR, "summary.json")}`
	);
	process.exit(failed > 0 ? 1 : 0);
}

main().catch((err) => {
	console.error(err);
	process.exit(1);
});
