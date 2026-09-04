# AntiOS Source of Truth Map (`SOURCE_OF_TRUTH_MAP.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team  
**Objective**: Establish the unambiguous canonical authority for every core architectural dimension of AntiOS, eliminating dual-truth risks and documenting divergence vulnerabilities.

---

## 1. Master Source of Truth Matrix

| Architectural Domain | Competing / Divergent Sources | Canonical Source of Truth | Authority Level | Divergence & Conflict Risk |
| :--- | :--- | :--- | :---: | :--- |
| **System Architecture** | `ARCHITECTURE_PROPOSAL.md`<br>`DECISION_REGISTER.md`<br>`PHASE_6_SYNTHESIS.md`<br>`PHASE_9_REPORT.md` | **`DECISION_REGISTER.md`** (Architecture Policy)<br>+ **`PHASE_9_REPORT.md`** (Empirical Boundary) | **POLICY & EMPIRICAL** | `ARCHITECTURE_PROPOSAL.md` lists MCP schema validators and AST parsers as components, but `DECISION_REGISTER.md:L60` formally disproved and rejected them. An agent reading only the proposal assumes nonexistent components exist. |
| **Protected Paths** | `docs/AGENTS.md` (`rslib/`)<br>`pre_tool_guard.py` (`rslib`, `framework`)<br>`ANTIOS_FAILURE_TAXONOMY.md` (`.agents/`) | **`framework/scripts/hooks/pre_tool_guard.py`** | **ENFORCEMENT (CODE)** | `AGENTS.md` only mentions `rslib/`. An agent attempting to modify `framework/` gets denied without understanding why. Furthermore, neither protects `.agents/hooks.json`, creating a silent deletion vulnerability. |
| **Verification Policy** | `docs/AGENTS.md:L21-23` (Test Ratchet)<br>`studylab-task-runner/SKILL.md:L28-31`<br>`stop_gate.py` (Script implementation) | **`framework/scripts/hooks/stop_gate.py`** | **ENFORCEMENT (CODE)** | `SKILL.md` instructs the agent to run `verify_task.py`, but `stop_gate.py` prioritizes `package.json` (`vitest:once`). If `vitest:once` fails while `verify_task.py` passes, the agent is blocked and confused. |
| **Skill Registry** | Platform `<skills>` prompt block<br>`framework/.agents/skills/`<br>`sandbox/StudyLab/.agents/skills/` | **Platform Engine `<skills>` Block** | **RUNTIME REALITY** | Documentation claims `studylab-task-runner` is an active AntiOS skill. In reality, Antigravity does not discover skills inside `framework/`, so the skill is **completely absent from the runtime prompt**. |
| **Task State & Progress** | `docs/ACTIVE_CONTEXT.md`<br>`reports/PHASE_*.md`<br>`git status` / `git log` | **Git Commit Log & Git Status** | **DETERMINISTIC STATE** | `docs/ACTIVE_CONTEXT.md` is frozen at Prototype v0.1 ("Framework Setup"). Resuming agents reading this file suffer amnesia and believe completed work is pending. Git history is the only reliable state. |
| **Current Mission Phase** | `docs/ACTIVE_CONTEXT.md` (Setup)<br>`reports/PHASE_9_REPORT.md` (Pilot)<br>User Request (`Phase 10`) | **Active User Request / Mission Directive** | **HUMAN GOVERNANCE** | The files disagree across 4 distinct phases (Phase 6, Phase 9, Phase 10). Without active human anchoring, autonomous agents hallucinate the current phase. |
| **Agent Behavioral Rules** | Platform `<user_rules>` (Empty)<br>`docs/AGENTS.md` (Global Constitution)<br>Hook Rejection Messages | **`docs/AGENTS.md`** (Intent)<br>+ **Python Hook Rejection Strings** (Enforcement) | **HYBRID** | Rules in `AGENTS.md` without hooks (e.g. Directive 3 "Same Change Set") have 0% enforcement. Only rules backed by Python hooks physically constrain agents. |
| **StudyLab Domain Contract** | `docs/AGENTS.md:L25-27`<br>StudyLab Source $\to$ APKG Schema | **StudyLab Native Codebase (`sandbox/StudyLab/`)** | **DOMAIN CONTRACT** | StudySourceCore is 100% OUT OF SCOPE. The canonical question schema and reviewer invariants reside exclusively in StudyLab's native TypeScript/Rust codebase. |

---

## 2. Deep Dive: High-Risk Conflict Domains

### Conflict Domain 1: The Verification Ratchet (`SKILL.md` vs `stop_gate.py`)
- **The Divergence**: `studylab-task-runner/SKILL.md` codifies the instruction to create and run `verify_task.py`. However, Phase 8 refactored `stop_gate.py` to auto-discover `package.json` (`vitest:once`) and `pyproject.toml` (`pytest`), with `verify_task.py` as an insecure tertiary fallback.
- **Vulnerability**: If a malicious or lazy agent reads `SKILL.md`, it is guided to create a dummy `verify_task.py` with `sys.exit(0)`. In repos without `package.json`, this succeeds and subverts the entire Stop gate!
- **Resolution**: Deprecate `verify_task.py` in `SKILL.md` and prune lines 58–69 in `stop_gate.py`.

### Conflict Domain 2: Active Working Memory vs Repository Reality
- **The Divergence**:
  ```text
  docs/ACTIVE_CONTEXT.md:
    "Task: Prototype v0.1 Initialization and Sandbox Experiments"
    "- [ ] Implement safety hooks (pre_tool_guard.py, stop_gate.py)"
    "- [ ] Implement RPAC lifecycle skill"
  
  Actual Disk Reality:
    - Safety hooks exist in framework/scripts/hooks/
    - RPAC skill exists in framework/.agents/skills/
    - Phases 7, 8, and 9 are complete with 15 detailed reports
  ```
- **Vulnerability**: Any agent relying on `docs/ACTIVE_CONTEXT.md` as instructed by `AGENTS.md` will believe it must re-implement the framework from scratch.
- **Resolution**: `docs/ACTIVE_CONTEXT.md` must either be automated via pre-commit hooks or re-anchored to reflect the active Phase 10 backlog.

### Conflict Domain 3: Upstream Immutability (Documentation vs Shell Boundary)
- **The Divergence**: `docs/AGENTS.md` states: *"You MUST NOT modify or write to rslib/ or upstream Anki core components."* `DECISION_REGISTER.md` states: *"If an agent tries to execute a dangerous shell command, the hook exits with non-zero status..."*
- **Vulnerability**: `pre_tool_guard.py` only intercepts `write_to_file` and `replace_file_content`. Any agent running PowerShell (`Set-Content`) or Git commands mutates `rslib/` with zero interception.
- **Resolution**: Explicitly classify shell command mutation as an Antigravity Platform Limitation. Enforce upstream protection via OS filesystem file attributes or container read-only mounts.

---

## 3. Hierarchy of Authority Rules for AntiOS

When an agent encounters conflicting signals, it MUST resolve precedence in this exact order:

```text
Rank 1: Deterministic Hook Process Execution (pre_tool_guard.py, stop_gate.py)
        └── Physical OS exit code / process rejection. Cannot be overridden.

Rank 2: Explicit Human User Prompt / Directive
        └── Active conversational mandate. Overrides passive docs and skills.

Rank 3: Git Commit Log & Working Tree Status (git log, git status)
        └── Physical history of the repository. Overrides markdown memory files.

Rank 4: Decision Register (DECISION_REGISTER.md)
        └── Recorded architectural consensus. Overrides speculative proposals.

Rank 5: Progressive Skills (SKILL.md)
        └── Procedural workflows. Overrides passive documentation.

Rank 6: Passive Memory Bank (docs/AGENTS.md, docs/ACTIVE_CONTEXT.md)
        └── Informational context. Must yield to all higher layers.
```
