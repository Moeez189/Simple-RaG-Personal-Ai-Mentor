# RAG improvement roadmap

Track progress for **personal-ai-mentor** (simple RAG, not agent RAG).

**Legend:** ✅ Done · 🔄 In progress · ⬜ Not started

**Last updated:** 2026-05-20

---

## Overall rating (simple RAG)

| Stage | Score | Status |
|-------|-------|--------|
| Starting point | ~6.5 / 10 | — |
| After data quality + Chroma-first + golden tests | **~7.5 / 10** | ✅ Current |
| Target (rerank + metadata + full eval) | ~8.5 / 10 | ⬜ Future |

---

## 1. Data & document quality (highest impact)

| # | Task | Status | What was done |
|---|------|--------|----------------|
| 1.1 | One concept per `##` section | ✅ Done | Restructured `Flutter_Notes.md` and `React_Native_Interview_Knowledge_Base.md` |
| 1.2 | Stable, searchable headings (`## Debouncing`, not `## 24. ...`) | ✅ Done | Promoted `###` → `##`, removed numbered headings |
| 1.3 | Chunk-friendly paragraphs (2–5 lines) | ✅ Done | Split large sections (Closures, Arrow Functions, `this`) |
| 1.4 | Data guidelines doc | ✅ Done | [`data/README.md`](data/README.md) |
| 1.5 | Validate before ingest | ✅ Done | `uv run python -m scripts.check_data_quality` |
| 1.6 | Re-ingest workflow documented | ✅ Done | Documented in [`README.md`](README.md) and `data/README.md` |
| 1.7 | Exclude `data/README.md` from index | ✅ Done | Filter in `app/loaders/document_loader.py` |
| 1.8 | Fix `clean_text` (preserve newlines for markdown) | ✅ Done | `app/utils/preprocess.py` |

**Commands after editing notes:**

```bash
uv run python -m scripts.check_data_quality
uv run python -m scripts.ingest
```

---

## 2. Golden Q&A evaluation set

| # | Task | Status | What was done |
|---|------|--------|----------------|
| 2.1 | Golden question list | ✅ Done | [`tests/golden_qa.json`](tests/golden_qa.json) (**31 cases**) |
| 2.2 | Retrieval tests (no LLM) | ✅ Done | [`tests/test_golden_retrieval.py`](tests/test_golden_retrieval.py) |
| 2.3 | CLI eval script | ✅ Done | `uv run python -m scripts.run_golden_eval` (+ `--e2e`) |
| 2.4 | Document workflow in README | ✅ Done | Step 4 in [`README.md`](README.md) |
| 2.5 | End-to-end golden tests (mocked LLM) | ✅ Done | [`tests/test_golden_e2e.py`](tests/test_golden_e2e.py) |
| 2.6 | Live E2E with Ollama (optional) | ✅ Done | [`tests/test_golden_e2e_live.py`](tests/test_golden_e2e_live.py) — `OLLAMA_GOLDEN_E2E=1` |
| 2.7 | Shared eval helpers | ✅ Done | [`tests/golden_helpers.py`](tests/golden_helpers.py) |
| 2.8 | Expand golden set for current corpus | ✅ Done | RN + Flutter topics (hooks, async, layout, etc.) |

**When you add a new `##` topic in `data/`, add one row to `golden_qa.json`:**

```json
{
  "id": "my_topic",
  "question": "My Topic",
  "expect": "retrieve",
  "context_must_contain": ["keyword"]
}
```

---

## 3. Retrieval: Chroma-first + lexical boost

| # | Task | Status | What was done |
|---|------|--------|----------------|
| 3.1 | Always query Chroma (not lexical-only first) | ✅ Done | `retrieve_relevant_documents()` in `app/chat/chatbot.py` |
| 3.2 | Merge vector + lexical scores | ✅ Done | `_merge_results()` ranks `lexical*10 + vector` |
| 3.3 | Relevance gate (block unrelated vector hits) | ✅ Done | `_passes_relevance_gate()` |
| 3.4 | Public `retrieve_relevant_documents` for tests | ✅ Done | Exported for unit/golden tests |
| 3.5 | Single retrieval source (remove live re-split at query time) | ⬜ Not started | Still uses `_get_local_chunks()` + Chroma |
| 3.6 | Show `source` metadata in Gradio UI | ⬜ Not started | Helps debug wrong answers |
| 3.7 | Cross-encoder / reranker on top-k | ⬜ Not started | Improves chunk ranking before LLM |
| 3.8 | Tune `TOP_K`, `VECTOR_RELEVANCE_THRESHOLD` via golden set | ⬜ Not started | Data-driven tuning |

---

## 4. Generation & UX

| # | Task | Status | What was done |
|---|------|--------|----------------|
| 4.1 | Strict RAG prompt + exact fallback | ✅ Done | `ask_question()` in `chatbot.py` |
| 4.2 | Greeting shortcut (no LLM) | ✅ Done | `GREETING_MESSAGES` |
| 4.3 | Typo / fuzzy keyword refinement | ✅ Done | `_refine_keyword`, `_refine_question` |
| 4.4 | Use chat history for follow-up questions | ⬜ Not started | Gradio `history` ignored in `gradio_ui.py` |
| 4.5 | Conversation memory in retrieval query | ⬜ Not started | e.g. “give an example” after “abstraction” |

---

## 5. Operations & project hygiene

| # | Task | Status | What was done |
|---|------|--------|----------------|
| 5.1 | Use project venv (`uv run`) not system `python3` | ✅ Done | Documented in README |
| 5.2 | Ingest empty-chunk guard | ✅ Done | `scripts/ingest.py` raises if 0 chunks |
| 5.3 | Initial git commit baseline | ⬜ Not started | Enables revert / PR workflow |
| 5.4 | `.env` / secrets not committed | ⬜ Verify | Check `.gitignore` before first commit |

---

## 6. Agent RAG (out of scope for now)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.1 | Multi-step agent / tool loop | ⬜ Not started | Would be a different architecture |
| 6.2 | LangGraph / ReAct planner | ⬜ Not started | Not needed for personal interview prep |

---

## Suggested order for remaining work

1. ⬜ **3.6** — Show source file in chat UI (quick win)
2. ⬜ **2.6** — Add golden cases when you add new `data/` files
3. ⬜ **3.5** — Rely on Chroma only at query time (simpler, faster)
4. ⬜ **3.7** — Reranker (bigger retrieval gain)
5. ⬜ **4.4** — Chat history for follow-ups
6. ⬜ **5.3** — Git commit baseline

---

## Quick reference

| Goal | Command |
|------|---------|
| Check markdown structure | `uv run python -m scripts.check_data_quality` |
| Re-build vector DB | `uv run python -m scripts.ingest` |
| Golden retrieval eval | `uv run python -m scripts.run_golden_eval` |
| Golden mocked E2E | `uv run python -m scripts.run_golden_eval --e2e` |
| Golden unit tests | `uv run python -m unittest tests.test_golden_retrieval tests.test_golden_e2e -v` |
| Golden live Ollama E2E | `OLLAMA_GOLDEN_E2E=1 uv run python -m unittest tests.test_golden_e2e_live -v` |
| All tests | `uv run python -m unittest discover -s tests -v` |
| Run app | `uv run main.py` |

---

## How to update this file

When you finish a task:

1. Change ⬜ or 🔄 to ✅ in the table above
2. Add a short note under “What was done” if helpful
3. Bump **Last updated** date
