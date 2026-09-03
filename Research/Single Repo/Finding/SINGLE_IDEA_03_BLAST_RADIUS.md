# SINGLE IDEA FORENSIC REPORT: 03 — AST / DEPENDENCY GRAPH + BLAST RADIUS

## 1. Idea Identity
- **Idea Name**: Static Dependency Graph & Transitive Blast-Radius Calculation
- **Primary Mechanism**: Codebase scanning, import specifier resolution, reverse-index graph construction, Breadth-First Search (BFS) transitive reachability analysis, and snapshot diffing for breaking change detection.
- **Core Concept**: Answering the fundamental question *"Can an agent know what else might break before modifying a file?"* by computing downstream dependents, identifying circular dependencies, and flagging high-risk coupling before edits occur.

---

## 2. Source Repository
- **Repository**: `RavByte-AI/agent-memory-system`
- **URL**: https://github.com/RavByte-AI/agent-memory-system
- **Authors**: Gaurav Singh (`@gauravchadhry`), RavByte Technologies
- **License**: MIT License
- **Technologies**: Node.js (ESM), TypeScript 5.7, `fast-glob`, `commander`, `zod`, `vitest`.

---

## 3. Revision / Commit
- **Inspected Branch**: `main`
- **Commit SHA**: `1f728726de140e1e2bcde745495696d3ace2aac8`
- **Commit Date**: 2026-03-24
- **Commit Title**: `Merge pull request #1 from shivansh2511/phase-2-repository-credibility`

---

## 4. Problem Being Solved
When autonomous coding agents modify files in an unfamiliar codebase, they suffer from **blind modification risk**:
1. **Hidden Downstream Breakages**: Editing a shared utility or data model breaks downstream consumers that the agent is completely unaware of.
2. **Infinite Token Exploration**: Without a dependency map, an agent must grep the entire codebase or load dozens of files into context to understand what depends on what.
3. **Silent Breaking Changes**: Removing or renaming an exported function often goes unnoticed until runtime or late in CI if typecheck coverage is incomplete.
4. **Architectural Coupling Blindness**: Agents cannot distinguish low-risk leaf components from high-risk central hubs with dozens of transitive dependents.

---

## 5. Original Implementation
The repository attempts to solve this via a dedicated graph analysis subsystem in `src/graph/`:

### A. The Parser Tier (`src/graph/parser.ts`)
Despite architectural claims of "AST analysis", the implementation uses a **heuristic regular expression engine**:
- **Imports Extraction (`extractRawImports`)**:
  - ES Modules / CommonJS: `/\bfrom\s+['"]([^'"]+)['"]/g`, `/\bimport\s*\(\s*['"]([^'"]+)['"]\s*\)/g`, `/\brequire\s*\(\s*['"]([^'"]+)['"]\s*\)/g`.
  - Python: `/^from\s+(\.+[\w.]*|[\w.]+)\s+import/gm`, `/^import\s+([\w.,\s]+)/gm`.
  - Go: `/import\s+(?:"([^"]+)"|`([^`]+)`|\(\s*([\s\S]*?)\s*\))/g`.
  - Markdown: Wiki-links `\[\[...\]\]` and relative Markdown links `\[...\]\(...\)`.
- **Import Resolution (`resolveImport`)**: Resolves relative paths (`./foo.js` -> `./foo.ts`, `./bar` -> `./bar/index.ts`).
- **Export Extraction (`extractExports`)**: Matches `export function`, `export class`, `export const`, `export interface`.
- **Function Extraction (`extractFunctions`)**: Matches function signatures and calculates cyclomatic complexity heuristics.

### B. The Graph Builder (`src/graph/builder.ts`)
- Uses `fast-glob` to gather files (default max: 1000 files).
- Builds `edges: GraphEdge[]` where each edge records `source`, `target`, and `kind: "import"`.
- Builds `FileNode` instances with detected architectural layer (`ui`, `services`, `utils`, `data`, `config`, `test`).
- Computes repository health scores and grades (`A` through `F`).

### C. The Blast Radius Engine (`src/graph/blast-radius.ts`)
- **Reverse Index (`buildReverseIndex`)**: Inverts the forward import graph into a map of `target -> Set<sources that import target>`.
- **Transitive Reachability (`computeBlastRadius`)**: Executes a standard BFS traversal starting from `rootFile` using the reverse index up to `maxDepth = 10`.
- **Cycle Detection (`detectCircularDependencies`)**: Uses DFS with an active recursion stack to locate dependency cycles.
- **Layer Violation Detection (`detectLayerViolations`)**: Checks whether lower layers (e.g. `utils`) import higher layers (e.g. `ui`).

### D. Snapshot Diffing & Breaking Changes (`src/graph/snapshot.ts`)
- Saves graph state to `memory/repository-graph.json`.
- `diffSnapshots(before, after)` compares exported symbols across commits to flag `removed-export` breaking changes.

---

## 6. Execution / Data Flow

```text
[Local Codebase Files]
          ↓
       (INPUT)
          ↓
[1. fast-glob File Discovery] ──> collects up to maxFiles (1000)
          ↓
[2. Regex Heuristic Parser]   ──> parser.ts extracts imports & exported symbols
          ↓
[3. Import Resolver]          ──> resolveImport maps relative specs to repo paths
          ↓
[4. Graph Assembler]          ──> builder.ts builds edges[] & FileNode[]
          ↓
[5. Reverse Indexer]          ──> buildReverseIndex inverts target -> callers
          ↓
[6. BFS Blast Radius]         ──> computeBlastRadius traverses downstream dependents
          ↓
       (OUTPUT)
          ↓
[7. Artifact Generation]      ──> writes memory/repository-graph.json (~1760 tokens)
                              ──> writes memory/architecture-flow.md
          ↓
      (CONSUMER)
          ↓
[AI Agent / CLI Tool]         ──> runs: agent-memory graph blast-radius -f <file>
                              ──> receives: "Changing X could break N downstream file(s)"
```

---

## 7. Required Dependencies
1. **Node.js**: Version `>= 20.0.0` (ESM native).
2. **NPM Libraries**: `commander` (CLI), `fast-glob` (filesystem scanning), `zod` (schema validation).
3. **Build / Dev Tooling**: `tsx` (TypeScript runtime execution), `vitest` (unit testing).

---

## 8. Verification Evidence (The Forensic Smoking Guns)
We executed the implementation live in the research workspace and conducted an exhaustive line-by-line inspection of the algorithm:

### A. Live Execution Verification
1. **Graph Building**:
   Ran `npx tsx src/cli/index.ts graph build` on the AMS repository itself:
   - Output: `Analysed 103 files, 87 edges. Health: B (84/100) | 0 cycles`. Generated `memory/repository-graph.json` and `memory/architecture-flow.md`.
2. **Blast Radius CLI Execution**:
   Ran `npx tsx src/cli/index.ts graph blast-radius -f src/types.ts`:
   - Output: `[i] Changing src/types.ts could break 13 downstream file(s): src/index.ts, src/agent-log/store.ts, src/cli/index.ts, src/generator/generate.ts...`
3. **Test Suite Execution**:
   Ran `npm test`: 6 test files passed (82 tests); **1 test failed** (`analyzeRepository (integration) > depth=full includes function extraction` threw `AssertionError: expected 16 to be greater than 20` due to Windows filesystem sorting truncating `src/` files under `maxFiles: 50`).

### B. Critical Forensic Findings (Why Accuracy Fails)
1. **NOT AN AST PARSER**: Despite claims of AST analysis, `src/graph/parser.ts:L4-10` is explicitly documented and implemented as a regex-based heuristic scanner. It does not parse AST trees, cannot resolve scopes, and cannot handle complex expressions.
2. **UNPOPULATED SYMBOL EDGES**:
   In `src/graph/builder.ts:L126`:
   ```typescript
   edges.push({ source: file.path, target: resolved, kind: "import", symbols: [], weight: 1 });
   ```
   **`symbols: []` is hardcoded as an empty array.** The scanner *never* extracts or records which specific symbols are imported on any edge!
3. **MOCK-MASKED TEST ILLUSION**:
   In `src/graph/snapshot.ts:L75-77`:
   ```typescript
   const affectedFiles = after.edges
     .filter((e) => e.target === file && e.symbols.includes(symbol ?? ""))
     .map((e) => e.source);
   ```
   Because `e.symbols` is always empty in real parsed code, `affectedFiles` is **ALWAYS EMPTY (`[]`)**!
   The test in `tests/graph.test.ts:L367` passed ONLY because the test fixture manually injected a hardcoded mock edge:
   `edges: [{ source: "a.ts", target: "b.ts", kind: "import", symbols: ["helper"], weight: 1 }]`!
   In actual practice on any real codebase, `diffSnapshots` reports `0 affected callers` for all removed exports!
4. **DEAD FUNCTION CALL GRAPH**:
   In `src/graph/types.ts:L25`, `FunctionNode` defines `calledBy: string[]`. However, `parser.ts` always initializes it to `[]` (lines 208, 218, 228, 238), and it is **never populated anywhere else in the entire repository**. Consequently, `queryCallers(fnName)` in `query.ts:L95` always returns an empty list!
5. **PATH ALIAS BLINDNESS**:
   In `src/graph/parser.ts:L69`:
   ```typescript
   if (!specifier.startsWith(".") && !specifier.startsWith("/")) return null;
   ```
   Any modern project using TypeScript path aliases (e.g. `@/components/Button`, `~/utils`, `@shared/schema`) immediately returns `null`. The graph records **zero edges** for all aliased imports!

---

## 9. Failure Modes
1. **Coarse File-Level False Positives**: Because edges lack symbol granularity, modifying a single private helper in `utils.ts` flags every file that imports `utils.ts` as broken, even if they only import an unrelated constant.
2. **Severe False Negatives via Path Aliases & Dynamic Imports**: Projects using `tsconfig.json` path mappings produce an almost completely disconnected graph with zero downstream dependents.
3. **False Confidence in Breaking Changes**: An agent querying whether removing an export will break anything is told: `Update all callers of "symbol" in 0 file(s)`, creating catastrophic false confidence that causes breaking changes to land.
4. **Stale Graph Desynchronization**: The graph is stored as static JSON (`repository-graph.json`). If an agent creates, renames, or deletes files during a task without running `agent-memory graph build`, subsequent queries reflect obsolete state.
5. **Arbitrary Truncation via `maxFiles`**: On codebases with >1000 files, files beyond the cutoff are silently dropped, causing blast-radius queries to miss massive subtrees.

---

## 10. Strengths
- **Speed & Simplicity**: Runs in ~1-2 seconds with zero native compilation or heavyweight database daemons (no Neo4j, SQLite, or C++ binaries).
- **Clean Algorithmic Concept**: The reverse-index BFS traversal (`target -> Set<callers>`) is the mathematically correct primitive for downstream impact analysis.
- **Compact Agent Memory Artifact**: The generated `memory/repository-graph.json` and summary format (~1760 tokens) provides a high-level topographical map that fits within small context windows.

---

## 11. Weaknesses
- **Heuristic Regex Fragility**: Fails on multi-line imports, comments containing import syntax, conditional imports, and dynamic loading.
- **Incomplete / Hollow Implementation**: Symbol-level tracking and caller tracking are unpopulated stubs masked by artificial test mocks.
- **Zero Language Intelligence**: Lacks type inference, meaning re-exports (`export * from './module'`) and interface implementations are invisible.

---

## 12. Complexity
**MEDIUM**
- Algorithmic logic is lightweight (pure TypeScript).
- Maintenance complexity is high due to regex edge cases across multiple languages (TS, Python, Go).

---

## 13. StudyLab Relevance
- **Implementation Relevance**: **LOW / REJECT** (The regex parser and fake symbol tracking cannot be trusted in a production engineering framework).
- **Conceptual Relevance**: **HIGH** (The *idea* of calculating blast radius before modifying core mathematical models, Anki database schemas, or LaTeX converters is crucial).

---

## 14. Potential StudyLab Adaptation
*(Conceptual only — not implemented)*:
StudyLab should **NOT** adopt the `agent-memory-system` implementation. Instead, StudyLab should adapt the *concept* using reliable, deterministic primitives:

### A. Compiler/LSP-Backed Code Blast Radius
Instead of regex heuristics, leverage native language compilers:
- For TypeScript: Use the official TypeScript Compiler API (`ts.createProgram`) or `oxc`/`swc` to extract exact symbol-level import edges and path aliases.
- For Python: Use Python's standard library `ast.parse` to extract exact `ImportFrom` nodes.
- For Test Impact: Use test runner native dependency graphs (e.g. `vitest related <file>` or `pytest-testmon`) to identify the exact subset of tests to execute.

### B. Domain-Specific Curriculum & Theorem Blast Radius
For StudyLab's core educational domain, implement a **Pedagogical Prerequisite Graph**:
- Map mathematical concepts: `Definition 1.1 -> Theorem 2.4 -> Lemma 2.5 -> Flashcard Deck X`.
- If an agent modifies `Definition 1.1` (e.g., changing the definition of a vector space), the blast-radius engine identifies every dependent theorem, proof, flashcard, and quiz question that must be re-verified.

---

## 15. What Must Be Preserved
The **conceptual primitive of reverse-index dependency mapping and transitive blast-radius calculation** (`target -> Set<callers>`). Giving an agent visibility into downstream impact before it edits a file is an indispensable safety pattern.

---

## 16. What Could Be Simplified / Replaced
- **Discard the entire regex parser (`src/graph/parser.ts`)**: Replace with native AST parsers (`ts.createProgram`, Python `ast`).
- **Discard the fake symbol diffing in `snapshot.ts`**: Replace with compiler typechecking (`tsc --noEmit`, `pyright`).
- **Eliminate arbitrary file capping (`maxFiles`)**: Use streaming or module-scoped analysis.

---

## 17. Adoption Status
- **Implementation**: **REJECT** (Brittle regex parsing, hollow symbol tracking, high false-negative risk).
- **Concept**: **ADAPT CANDIDATE** (Rebuild as a compiler-backed LSP tool and a curriculum prerequisite graph for StudyLab).

---

## 18. Confidence
**HIGH (100%)**
- Verified through live CLI execution, full test suite evaluation, and deep code auditing.
- Smuggle-masked mocks in `tests/graph.test.ts:367` and unpopulated `symbols: []` in `builder.ts:126` confirmed by forensic grep.

---

## 19. Evidence Index
- Repository Root: `c:\Users\Suraj\Documents\Antigravity\Rough-Work\prior-art-lab\repos\agent-memory-system`
- Commit SHA: `1f728726de140e1e2bcde745495696d3ace2aac8`
- Regex Parser: `src/graph/parser.ts:L1-318` (see L4-10 for regex admission; L69 for path alias rejection; L208/218/228/238 for empty `calledBy: []`)
- Graph Builder: `src/graph/builder.ts:L1-200` (see L126 for hardcoded empty `symbols: []`)
- Blast Radius Algorithm: `src/graph/blast-radius.ts:L1-89` (see L8-14 for `buildReverseIndex`; L17-35 for `computeBlastRadius`)
- Query API: `src/graph/query.ts:L1-128` (see L42-53 for `queryBlastRadius`; L90-100 for dead `calledBy` check)
- Snapshot Diffing: `src/graph/snapshot.ts:L1-130` (see L75-77 for broken symbol matching)
- CLI Entry Point: `src/cli/index.ts:L407-421` (`graph blast-radius` command)
- Test Suite: `tests/graph.test.ts:L1-513` (see L367 for hardcoded test mock masking parser deficiency)
