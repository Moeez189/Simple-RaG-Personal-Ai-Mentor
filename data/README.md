# Knowledge base guidelines (RAG)

Improvement status: see [`../IMPROVEMENTS.md`](../IMPROVEMENTS.md) (section **1. Data & document quality** is ✅ done).

Follow these rules when adding or editing files under `data/`. After any change, re-ingest from the project root:

```bash
uv run python -m scripts.ingest
```

## File naming

- Use clear, stable names: `Flutter_Notes.md`, `React_Native_Interview_Knowledge_Base.md`
- Prefer words over abbreviations; use underscores instead of spaces in filenames
- One main topic per file when possible

## Heading rules (required for good retrieval)

| Level | Use for | Example |
|-------|---------|---------|
| `#` | Document title (once per file) | `# Flutter Notes` |
| `##` | **One interview concept** | `## Debouncing` |
| `###` | Optional sub-detail under a single concept | `## Debouncing` → `### Example` |

### One concept per `##` section

- **Do:** `## Debouncing` with only debouncing content
- **Do not:** `## Advanced JavaScript` with debouncing, throttling, and currying in one section

If you have several concepts, use several `##` headings—not one `##` with many `###` children.

### Stable, searchable headings

- Use the term you would ask in chat: `## useState`, `## RecyclerView`, `## Debouncing`
- Avoid numbered-only titles: prefer `## React vs React Native` over `## 1. React vs React Native`
- Keep headings short (2–6 words)

## Chunk-friendly writing

Chunking uses **300 characters** with **50 overlap**. Help the splitter:

- Keep paragraphs to **2–5 lines**
- One idea per paragraph
- Put code examples directly under the concept they illustrate
- Separate sections with `---` only when changing major topics

## Supported formats

- `.md` (preferred — best header splitting)
- `.txt`, `.pdf`, `.docx`

## Check structure before ingest

```bash
uv run python -m scripts.check_data_quality
```

Fix any reported errors, then run ingest.

## Golden Q&A (after ingest)

Add one entry to [`tests/golden_qa.json`](../tests/golden_qa.json) per new `##` topic, then:

```bash
uv run python -m unittest tests.test_golden_retrieval tests.test_golden_e2e -v
```
