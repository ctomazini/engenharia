# Documentos da obra

Dois fluxos distintos convivem no app:

| Fluxo | DocType | Saída |
| --- | --- | --- |
| **Geração Word** | Document Template + Document Kit | `.docx` preenchido via docxtpl |
| **Repositório de arquivos** | Project Document | PDF, DWG, plantas, memoriais anexados |

## Document Category

Cadastro rígido (`category_name` único). Seed em `setup/seed.py`:

Memorial, ART, Protocolo, Planta, Laudo, Contrato, Orçamento, Foto, Declaração, Alvará, Outro.

Sidebar: **Cadastros → Categorias de Documento**.

## Project Document

Satélite de **Construction Project**.

| Campo | Descrição |
| --- | --- |
| `category` | Link → Document Category |
| `version_label` | Ex.: Rev 01 |
| `title_descriptor` | Complemento opcional |
| `title` | Composição automática (read-only) |
| `status` | Rascunho, Enviado, Aprovado… |
| `source` | Manual, Gerado pelo App, Importado |
| `related_permit` | Link opcional → Permit |
| `document` | Anexo (File) |

**ID:** `DOC-{YYYY}-{####}`

### Naming (`project_document_naming.py`)

**Título exibido:**

`{Obra} — {Categoria} — {Versão}[ — {Descritor}]`

**Arquivo físico:**

`{slug_obra}_{slug_categoria}_{slug_versao}_{slug_descritor}.ext`

Renomeação via `shutil.move` no `validate()` quando categoria, versão ou descritor mudam.

Documentos gerados pelo app (`documents.py`) inferem categoria do template e usam o mesmo padrão de filename.

## Hub — aba Documentos

- Painel `documents_panel` em `hub.js`
- Contagens em `project_hub.py` → `get_project_hub_data`
- Botão **+ Documento** e lista com links para formulários

## Migração

`patches/v16_0/migrate_project_document_category_to_link.py` — converte categorias texto livre antigas para Link.

## Testes

- `tests/test_project_document.py`
- `tests/test_project_hub.py` (contagens de documentos)
