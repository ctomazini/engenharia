# Documentos da obra

Dois fluxos distintos convivem no app:

| Fluxo | DocType / API | Saída |
| --- | --- | --- |
| **Geração Word** | Document Template + Document Kit → `documents.generate_project_documents` | `.docx` preenchido via docxtpl — **download no browser** (não persiste) |
| **Repositório de arquivos** | Project Document | PDF, DWG, plantas, memoriais — **somente upload manual** |

## Geração Word (download direto)

1. Na obra: **Gerar documentos** (templates ou kit).
2. O backend renderiza em memória e devolve `file_name` + `file_content` (base64).
3. O browser baixa o `.docx` automaticamente.
4. **Não** cria `File` anexado à obra nem registro `Project Document`.
5. Para arquivar na obra: **+ Documento** → upload manual (`source`: Upload Manual).

Nome do arquivo gerado segue `project_document_naming.compose_project_document_filename` (categoria inferida do template).

Registros antigos com `source` = *Gerado pelo App* podem existir em bases migradas antes desta mudança.

## Document Category

Cadastro rígido (`category_name` único). Seed em `setup/seed.py`:

Memorial, ART, Protocolo, Planta, Laudo, Contrato, Orçamento, Foto, Declaração, Alvará, Outro.

Sidebar: **Cadastros → Categorias de Documento**.

## Project Document

Satélite de **Construction Project** — repositório de arquivos da obra (upload manual).

| Campo | Descrição |
| --- | --- |
| `category` | Link → Document Category |
| `version_label` | Ex.: Rev 01 |
| `title_descriptor` | Complemento opcional |
| `title` | Composição automática (read-only) |
| `status` | Rascunho, Enviado, Aprovado… |
| `source` | Upload Manual, Digitalizado (*Gerado pelo App* legado) |
| `related_permit` | Link opcional → Permit |
| `file` | Anexo (File) |

**ID:** `DOC-{YYYY}-{####}`

### Naming (`project_document_naming.py`)

**Título exibido:**

`{Obra} — {Categoria} — {Versão}[ — {Descritor}]`

**Arquivo físico:**

`{slug_obra}_{slug_categoria}_{slug_versao}_{slug_descritor}.ext`

Renomeação via `shutil.move` no `validate()` quando categoria, versão ou descritor mudam.

## Hub — aba Documentos

- Painel `documents_panel` em `hub.js`
- Contagens em `project_hub.py` → `get_project_hub_data`
- Botão **+ Documento** e lista com links para formulários

## Migração

`patches/v16_0/migrate_project_document_category_to_link.py` — converte categorias texto livre antigas para Link.

## Testes

- `tests/test_documents.py` (geração sem persistência)
- `tests/test_project_document.py`
- `tests/test_project_hub.py` (contagens de documentos)
