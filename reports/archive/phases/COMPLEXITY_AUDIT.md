# Complexity Audit

## Artifact / Schema Validation

### Observation
We investigated whether AntiOS requires a native schema validator for StudyLab artifacts (such as checking JSON schemas or APKG internal consistency).

### Analysis
- StudyLab already contains domain-specific scripts (e.g., `generate_apkg.py`, `qa_forensic.py`) that construct and inherently validate the artifacts.
- Duplicating validation logic into AntiOS creates a heavy maintenance burden and violates the principle of Bounded Context. AntiOS should not know what a "card" or an "APKG" is.
- AntiOS's responsibility is orchestration and enforcement (e.g., ensuring a verification step occurs). The actual verification logic belongs entirely to StudyLab.

### Decision: DEFER / REJECT
We will NOT build schema validators into AntiOS. StudyLab will own its own domain validation. AntiOS will use generic `stop_gate.py` to enforce that StudyLab's native validation passes.

---

## Blast Radius / AST Analysis

### Observation
Prior art frameworks often include complex dependency mapping or AST parsing to determine 'blast radius'.

### Analysis
- **Manual/LLM Reasoning**: Very fast, but subject to hallucinations and false negatives on large codebases.
- **Tool-Assisted (Native)**: Using 	sc, svelte-check, and itest provides 100% accurate blast radius analysis with zero false positives for type errors, natively maintained by the language ecosystem.
- **Tool-Assisted (AntiOS AST Parser)**: High complexity, high maintenance burden, redundant with 	sc.

### Decision: REJECT
Do not build dependency graph tools into AntiOS. We rely on StudyLab's native compiler (	sc/svelte-check) and test runners to enforce blast radius safety. This keeps AntiOS lightweight.
