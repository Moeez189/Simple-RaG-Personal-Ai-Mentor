# Personal AI Mentor

RAG-based interview prep for mobile development (Flutter, React Native, JavaScript).

**Improvement tracker:** see [`IMPROVEMENTS.md`](IMPROVEMENTS.md) for what is ✅ done and what is still ⬜ planned.

## Run the application

```bash
uv run main.py
```

## Data workflow (do this after editing notes)

1. Edit files under `data/` using the rules in [`data/README.md`](data/README.md)
2. Check structure:

```bash
uv run python -m scripts.check_data_quality
```

3. Re-build the vector index:

```bash
uv run python -m scripts.ingest
```

4. Run golden Q&A checks:

```bash
# Retrieval + fallback (uses Chroma if present)
uv run python -m scripts.run_golden_eval

# Include mocked end-to-end answer checks
uv run python -m scripts.run_golden_eval --e2e

# All golden unit tests (fast, mocked vector store)
uv run python -m unittest tests.test_golden_retrieval tests.test_golden_e2e -v
```

Optional live Ollama E2E (requires `llama3:8b` running):

```bash
OLLAMA_GOLDEN_E2E=1 uv run python -m unittest tests.test_golden_e2e_live -v
```

Golden questions: [`tests/golden_qa.json`](tests/golden_qa.json) — add a row per new topic. See [`IMPROVEMENTS.md`](IMPROVEMENTS.md) section 2.

## Document formatting for RAG

<!-- Use this prompt that meets the rag hierarchy for your document -->
<------ 
You are a document structuring assistant for a Retrieval-Augmented Generation (RAG) system.

I will give you an unstructured or semi-structured Markdown document. Your task is to convert it into a clean, hierarchical Markdown document optimized for LangChain splitting using:

MarkdownHeaderTextSplitter with headers: #, ##, ###
RecursiveCharacterTextSplitter with:
chunk_size = 300
chunk_overlap = 50
separators: "\n\n", "\n", ". ", "? ", "! ", " "
🎯 OBJECTIVE

Rewrite and structure the document so it becomes RAG-ready, meaning:

It can be split cleanly by Markdown headers first
Then safely chunked into small semantic pieces
Each chunk stays meaningful and context-rich
📌 STRICT STRUCTURE RULES
1. Create proper Markdown hierarchy
Use:
# → Main topic
## → Subtopic
### → Detailed concept
Do NOT skip levels
Do NOT use random heading styles
2. Break content into single-concept sections

Each ## section must contain ONLY one concept.

Each ### section must:

Represent one idea only
Not mix unrelated topics
Be self-contained

Example:

❌ Wrong: “Redux and Navigation”
✅ Correct: separate into two ## sections
3. Fix unstructured content

If the input is messy:

Merge related sentences into correct sections
Split long paragraphs into logical sections
Create missing headers where needed
4. Optimize for chunking

Rewrite content so that:

Paragraphs are short (2–5 lines max)
No long dense explanations
Ideas are clearly separated
Content can safely fit into 300-character chunks
5. Preserve meaning and technical depth
Do NOT remove important information
Keep all technical explanations and examples
Maintain interview-level detail
6. Improve clarity

You may:

Rename unclear headings
Reorder sections logically (basic → advanced)
Improve readability and structure
7. Remove redundancy
Remove repeated explanations
Merge overlapping content
8. Make sections self-contained

Each section must make sense independently when retrieved by a RAG system.

📤 OUTPUT FORMAT

Return ONLY the final structured Markdown document.

Do NOT include explanations, comments, or reasoning.

-------->