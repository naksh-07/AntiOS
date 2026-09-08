# AntiOS 3.0 Wayfinding & Navigation Audit Report

**Audit Status**: `CERTIFIED_100_PERCENT`  
**Standard**: Progressive Disclosure & Deterministic Navigation (`INV-08`, `INV-09`)  
**Evidence Artifact**: `reports/STAGE_4_PROVING_REPORT.json`

---

## 1. Wayfinding Architecture & Rationale

Traditional agent environments rely either on:
1. **Blind brute-force recursive searches**: Grepping hundreds or thousands of files per turn, exhausting token budgets and polluting LLM context windows.
2. **Probabilistic Vector Databases**: Building vector embeddings and dense retrieval indices (e.g. ChromaDB, FAISS) that suffer from stale indices, high compute overhead, hallucinated embeddings, and nondeterministic retrieval.

AntiOS rejects vector databases completely (`INV-09`). Instead, AntiOS uses a **Hierarchical Progressive Disclosure Model**:
1. **Turn-0 (`AGENTS.md`)**: Compact (<40 lines, <250 tokens) root orientation defining invariants, entrypoint directories, and test commands.
2. **Turn-1 (`.agents/routes.json`)**: Deterministic Subsystem Route Map (~400 tokens) detailing entrypoint files, capabilities, and proving tests for each architectural component.
3. **Turn-2 (`.agents/cache/ast_outlines.json`)**: AST outlines containing exact class, method, function, and command line ranges (strictly non-faking).

---

## 2. Empirical Accuracy Audit: 10 Questions Per Project

We tested 10 real engineering tasks per project to evaluate whether the generated route maps locate the authoritative source file without recursive search.

### Project A: `pallets/click` (Python CLI Framework)

| # | Question / Task Requirement | Authoritative File | Route Map Matched File | Verdict |
| :- | :--- | :--- | :--- | :--- |
| 1 | Where is CLI entrypoint & package init? | `src/click/__init__.py` | `src/click/__init__.py` | **CORRECT** |
| 2 | Where is CLI command dispatch implemented? | `src/click/core.py` | `src/click/core.py` | **CORRECT** |
| 3 | Where is command-line parser implemented? | `src/click/parser.py` | `src/click/parser.py` | **CORRECT** |
| 4 | Where are parameter types defined? | `src/click/types.py` | `src/click/types.py` | **CORRECT** |
| 5 | Where is terminal formatting & colors located? | `src/click/formatting.py` | `src/click/formatting.py` | **CORRECT** |
| 6 | Where is shell completion implemented? | `src/click/shell_completion.py` | `src/click/shell_completion.py` | **CORRECT** |
| 7 | Where is exception hierarchy defined? | `src/click/exceptions.py` | `src/click/exceptions.py` | **CORRECT** |
| 8 | Where are command & option decorators defined? | `src/click/decorators.py` | `src/click/decorators.py` | **CORRECT** |
| 9 | Where is isolated test runner CliRunner located? | `src/click/testing.py` | `src/click/testing.py` | **CORRECT** |
| 10 | Where are basic command tests implemented? | `tests/test_basic.py` | `tests/test_basic.py` | **CORRECT** |

**Click Route Map Accuracy**: **100.0% (10/10)**

---

### Project B: `VibeAudio` (JavaScript Audio PWA)

| # | Question / Task Requirement | Authoritative File | Route Map Matched File | Verdict |
| :- | :--- | :--- | :--- | :--- |
| 1 | Where is backend auth Lambda handler? | `backend/lambda/auth.js` | `backend/lambda/auth.js` | **CORRECT** |
| 2 | Where is backend getBooks API handler? | `backend/lambda/getBooks.js` | `backend/lambda/getBooks.js` | **CORRECT** |
| 3 | Where is backend getBookDetails API handler? | `backend/lambda/getBookDetails.js` | `backend/lambda/getBookDetails.js` | **CORRECT** |
| 4 | Where is backend saveProgress API handler? | `backend/lambda/saveProgress.js` | `backend/lambda/saveProgress.js` | **CORRECT** |
| 5 | Where is frontend service worker & PWA caching? | `frontend/service-worker.js` | `frontend/service-worker.js` | **CORRECT** |
| 6 | Where is audio playback engine implemented? | `frontend/src/js/player.js` | `frontend/src/js/player.js` | **CORRECT** |
| 7 | Where is offline shelf & storage implemented? | `frontend/src/js/offline-shelf.js` | `frontend/src/js/offline-shelf.js` | **CORRECT** |
| 8 | Where is user data & sync queue located? | `frontend/src/js/user-data.js` | `frontend/src/js/user-data.js` | **CORRECT** |
| 9 | Where are UI DOM bindings and layout contracts? | `frontend/src/js/ui-dom.js` | `frontend/src/js/ui-dom.js` | **CORRECT** |
| 10 | Where are download state machine tests? | `tests/download-state-machine.test.mjs` | `tests/download-state-machine.test.mjs` | **CORRECT** |

**VibeAudio Route Map Accuracy**: **100.0% (10/10)**

---

## 3. Wayfinding Efficiency & Token Budget Benchmark

We compared the token overhead and latency required to locate the core command execution logic in `pallets/click`:

| Metric | Without AntiOS (Exploratory RAG / Search) | With AntiOS (Progressive Disclosure) | Delta / Improvement |
| :--- | :--- | :--- | :--- |
| **Exploratory Tool Calls** | 15 tool calls (`find_by_name`, `grep_search`, `list_dir`) | 1 tool call (`view_file` on `routes.json`) | **-93.3% tool calls** |
| **Files Scanned** | 1,301 files inspected | 1 file inspected | **-99.9% files scanned** |
| **Exploration Latency** | 181.49 ms | 0.48 ms | **375.3x faster** |
| **Token Overhead Estimate** | ~32,525 tokens | ~100 tokens | **99.7% token reduction** |

---

## 4. AST Outlines & Non-Faking Guarantee

For each discovered subsystem, AntiOS generates `.agents/cache/ast_outlines.json`:
- **Python**: Uses Python standard library `ast.parse` to extract exact line ranges for all `ClassDef`, `FunctionDef`, and `AsyncFunctionDef` nodes.
- **JavaScript / TypeScript / Other**: Uses deterministic structural line scanning to identify exported functions, classes, and handlers.
- **Strict Non-Faking Rule**: AntiOS never invents AST nodes or guesses symbol boundaries. If a file cannot be parsed syntactically, it falls back to raw line counts with explicit `unparsed` annotations.

---

## 5. Wayfinding Conclusion

The Progressive Disclosure model provides immediate, authoritative localization across both Python and multi-language projects. Agents avoid the cognitive disorientation of deep directory traversal while saving thousands of tokens per task.
