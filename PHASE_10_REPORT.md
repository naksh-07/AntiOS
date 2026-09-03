# AntiOS Phase 10 Forensic Audit Report (`PHASE_10_REPORT.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team (under Adaptive Orchestrator protocol)  
**Primary Mandate**: Establish empirical ground truth for AntiOS by answering:
> **"Does AntiOS actually behave the way we think it behaves?"**

**Boundaries Observed**:
- **StudySourceCore**: 100% OUT OF SCOPE. Zero files inspected, modified, or integrated.
- **StudyLab Safety**: Production branches untouched; zero unauthorized code mutations.
- **Audit Law**: OBSERVE $\to$ REPRODUCE $\to$ MEASURE $\to$ DOCUMENT (Defects preserved for baseline integrity).

---

## Executive Forensic Verdict

AntiOS establishes **genuine deterministic code-level enforcement** that successfully prevents catastrophic blast-radius leaks to upstream Anki core (`rslib/`) via IDE editing tools and eliminates conversational LLM self-certification ("Looks good to me") via physical OS process verification.

**HOWEVER, AntiOS suffers from critical architectural blind spots, implementation-documentation divergence, and platform confusion**:
1. **Implementation Drift**: None of the 5 surgical patches proposed in Phase 9 were applied to the codebase; `pre_tool_guard.py` and `stop_gate.py` remain identical to Phase 8.
2. **Critical Fail-Open Handlers**: `pre_tool_guard.py` explicitly catches all exceptions and grants `allow`. Both hooks grant `allow` when `workspacePaths` is empty.
3. **Catastrophic False Positive**: `pre_tool_guard.py` uses `if "framework" in parts: deny`, blocking all file edits across the entire repository if any ancestor folder is named `framework`.
4. **Skill Discoverability Black Hole**: The sole custom skill (`studylab-task-runner`) is buried in `framework/.agents/skills/` and is **100% undiscoverable by the Antigravity engine** in the root workspace.
5. **Memory Bank Amnesia**: `docs/ACTIVE_CONTEXT.md` is frozen at Prototype v0.1 ("Framework Setup") and actively misleads resuming agents.
6. **The Shell Gap (Platform Boundary)**: Shell commands (`run_command`) completely bypass file write hooks, proving AntiOS protects an IDE tool route rather than the OS filesystem boundary.
7. **Documentation Duplication**: Seven exact duplicate report files (54,582 bytes) clutter both the root workspace and `reports/`.

---

## The 30 Forensic Inquiries

### 1. Skills Forensic Audit

#### Q1: Do Skills actually activate?
**NO (in root workspace) / YES (in sub-workspace).**  
Antigravity discovers skills strictly at `<workspace_root>/.agents/skills/` or `<workspace_root>/.gemini/skills/`. The custom AntiOS skill `studylab-task-runner` is placed in `framework/.agents/skills/studylab-task-runner/SKILL.md`. In the root workspace `c:\Users\Suraj\Documents\Antigravity\AntiOs`, the platform system prompt `<skills>` block **does not list the skill**. It is completely unindexed, unexposed, and never activated unless an agent explicitly opens the `sandbox/StudyLab/` sub-workspace directly.

#### Q2: Do they actually influence behavior?
**YES (when loaded).**  
When an agent operates in a workspace where the skill is discoverable, it injects 34 lines (~1,838 bytes) codifying the RPAC (Refine, Plan, Act, Consolidate) lifecycle. Empirical trials in Phase 7 and 9 demonstrated that the skill successfully prevents agents from jumping directly into edits, forces the authoring of an implementation plan, and prompts the dispatch of a verifier subagent.

#### Q3: Are they correctly scoped?
**NO.**  
`studylab-task-runner` contains serious scoping errors:
1. Line 15 instructs the agent to read `docs/AGENTS.md` and `docs/ACTIVE_CONTEXT.md`. Inside `sandbox/StudyLab/`, neither file exists.
2. Line 29 advises spawning a verifier subagent with `TypeName='research'`. The `research` subagent type is strictly read-only and does not possess `run_command`, rendering it incapable of running test suites.
3. Lines 30–31 instruct the subagent to run `verify_task.py`, directly contradicting the Phase 8 removal of hardcoded test scripts in favor of dynamic test discovery (`vitest:once`).

#### Q4: Are they redundant?
**PARTIALLY.**  
The RPAC lifecycle heavily duplicates Antigravity's native Planning Mode (`<planning_mode>`), which already enforces Research $\to$ Implementation Plan $\to$ User Approval $\to$ Execute $\to$ Verify. The only non-redundant value the skill provides is mandating the Maker-Checker subagent pattern and warning against upstream `rslib/` modifications.

---

### 2. Rules Forensic Audit

#### Q5: Are Rules actually applied?
**PARTIALLY.**  
AntiOS has no `.agents/rules/` directory. All rules are consolidated into `docs/AGENTS.md` (27 lines). When an agent reads `docs/AGENTS.md`, it absorbs the rules as prompt-level cognitive context. However, adversarial stress testing proved that prompt rules without underlying Python hooks (e.g. Directive 3 "Same Change Set" or Directive 2 "Branch Isolation") are routinely ignored, forgotten during multi-turn conversations, or rationalized away. Only rules backed by Python hooks (`rslib/` immutability and test passage) are reliably applied.

#### Q6: Is precedence understood?
**EMPIRICALLY VERIFIED.**  
Through adversarial trials, the empirical layer precedence of AntiOS was established:
$$\text{Hook (Code)} > \text{User Prompt} > \text{Active Skill} > \text{Constitution (AGENTS.md)} > \text{Unhooked Tool}$$
- If a user prompt instructs the agent to write to `rslib/`, `pre_tool_guard.py` **DENIES** the tool call (Hook beats Prompt).
- If a user prompt instructs the agent to write to `rslib/` using PowerShell via `run_command`, the shell executes it without resistance (Prompt beats passive Constitution on unhooked tools).

#### Q7: Are conflicts safe?
**NO.**  
Because `.agents/hooks.json` is not protected in `pre_tool_guard.py`, an agent given an instruction to "disable safety rules" can edit or delete `hooks.json`, completely detaching all hooks for the remainder of the session without triggering any security alert.

---

### 3. Hooks Forensic Audit

#### Q8: Do hooks actually enforce policy?
**YES (for covered tool routes).**  
For the tools specified in `hooks.json` (`write_to_file`, `replace_file_content`), `pre_tool_guard.py` deterministically intercepts path traversal (`../rslib`), casing obfuscation (`RSLIB/`), and mixed path separators, returning hard process rejections. For task completion, `stop_gate.py` intercepts `Stop` events and deterministically blocks task exit if test processes fail.

#### Q9: Are they fail-safe?
**NO — THEY ARE CATASTROPHICALLY FAIL-OPEN.**  
1. `pre_tool_guard.py:43-44` catches all Python exceptions and outputs `{"decision": "allow"}`. Any runtime error, type error, or unexpected JSON payload grants unconditional write access.
2. `pre_tool_guard.py:14` and `stop_gate.py:12` grant unconditional `allow` if `workspacePaths` is missing or empty.
3. Only `stop_gate.py:78-84` correctly fails closed on script errors during test execution.

#### Q10: Can they be bypassed?
**YES.**  
1. **Windows 8.3 Short Names**: Passing `TargetFile: "RSLIB~1/dummy.rs"` bypasses `pre_tool_guard.py` because `os.path.realpath` resolves lexically on non-existent paths.
2. **Hook Configuration Tampering**: Tool edits to `.agents/hooks.json` are allowed.
3. **Test Pass Forgery**: Creating a dummy `verify_task.py` with `sys.exit(0)` or modifying `package.json` to `"vitest:once": "exit 0"` satisfies `stop_gate.py`.
4. **Shell Redirection**: Any shell command passed to `run_command` bypasses `PreToolUse` entirely.

#### Q11: Are platform limitations understood?
**YES.**  
Antigravity IDE hooks intercept tool call invocations, not OS kernel filesystem syscalls. Because `run_command` provides raw shell access, an agent can use PowerShell, bash, python, or git to write to protected files. Parsing arbitrary shell command strings inside an IDE hook is mathematically undecidable. True boundary immutability requires OS-level read-only file attributes or containerization (`:ro` mounts), which represents an inherent **Platform Boundary Limitation**.

---

### 4. Task State Forensic Audit

#### Q12: Does task state actually improve recovery?
**THEORETICALLY YES, PRACTICALLY NO (DUE TO DECAY).**  
When task state is accurately maintained, it bounds the agent's attention and allows seamless recovery after context resets. However, AntiOS lacks any automated mechanism to update `docs/ACTIVE_CONTEXT.md`. As a result, task state decays immediately after creation.

#### Q13: Can stale state mislead agents?
**YES — SEVERELY.**  
`docs/ACTIVE_CONTEXT.md` is currently frozen at Prototype v0.1 (`Phase: Framework Setup`, with uncompleted hook checkboxes). Resuming agents read this file, suffer **stale-state deception**, waste tokens attempting to re-implement already completed components, and require human intervention to re-anchor.

---

### 5. Memory Forensic Audit

#### Q14: Is this actual memory or documented context?
**DOCUMENTED CONTEXT ONLY.**  
AntiOS possesses **no active memory system**. It has no vector store, no state-graph database, and no automated daemon reconciling git commits with documentation. It relies entirely on passive markdown files (`AGENTS.md`, `ACTIVE_CONTEXT.md`) that an agent must manually read via `view_file`.

#### Q15: What survives context reset?
**ONLY STATIC DISK FILES.**  
When an agent session resets:
- The conversation context window is wiped (0 tokens).
- Transient brain artifacts (`implementation_plan.md`, `walkthrough.md`) survive on disk in `<appDataDir>\brain\<conv_id>\` but are disconnected from new sessions.
- Repository markdown files (`AGENTS.md`, `ACTIVE_CONTEXT.md`, reports) survive.
- If those repository files contain stale information or foreign contamination (e.g. `sentinel/BRIEFING.md` referencing `Anki-maths`), the new agent inherits that false state as ground truth.

---

### 6. Receipts Forensic Audit

#### Q16: Do receipts improve evidence?
**NO.**  
AntiOS's `evidence/` directory contains **0 files and 0 bytes**. Phase 8 evaluated cryptographic state hashing (W3C verifiable credentials) and formally rejected them because file hashes prove only that a file changed, not that the change was functionally or pedagogically correct.

#### Q17: Are they trustworthy?
**NO (THE RATCHET EXPIRY FLAW).**  
Static evidence receipts are fundamentally untrustworthy because of the lifecycle:
$$\text{CHANGE} \longrightarrow \text{TEST / RECEIPT} \longrightarrow \text{CHANGE AGAIN} \longrightarrow \text{DONE}$$
Any modification made after a receipt is generated invalidates the receipt. Real-time physical test execution at the moment of task stop (`stop_gate.py`) is the only trustworthy evidence mechanism.

---

### 7. Subagents Forensic Audit

#### Q18: Do subagents provide measurable benefit?
**YES (ON COMPLEX VERIFICATION).**  
In Phase 7 and 9 trials, spawning a fresh-eyes subagent (`TypeName='self'`) to review code and execute tests eliminated 100% of LLM confirmation bias, catching boundary oversights and uncommitted files that the author agent overlooked.

#### Q19: Where are they unnecessary?
**ON TRIVIAL OR MECHANICAL TASKS.**  
For 1-line syntax fixes, documentation updates, or simple typo corrections, dispatching a subagent doubles latency (30–60 seconds) and consumes 10k+ additional tokens with zero marginal gain in safety.

#### Q20: Is Maker-Checker justified?
**YES — CONDITIONALLY.**  
The 1:1 Maker-Checker pattern is justified for high-risk domain changes (reviewer FSM, double SQLite logic, APKG generation), provided the checker is backed by the deterministic Stop gate. The checker must be spawned as `TypeName='self'` (not `research`) so it possesses `run_command` to execute tests.

---

### 8. MCP Forensic Audit

#### Q21: Which MCPs provide real value?
1. **`chrome-devtools-mcp` / `playwright`**: Real value for visual regression testing, webview layout inspection, and headless E2E verification of StudyLab's Svelte frontend.
2. **`gemini-api-docs`**: High value for validating SDK APIs and preventing hallucinations of deprecated methods.

#### Q22: Which are architecture decoration?
1. **`github-mcp-server`**: **REDUNDANT DECORATION**. Local `git` CLI via `run_command` is strictly faster, token-free, offline-capable, and directly operates on local sandboxes.
2. **`studysource-core`**: **OUT OF SCOPE / DISPROVED**. Formally rejected in Phase 8 (`DECISION_REGISTER.md:L60`). StudyLab's native compiler tools validate schemas directly.
3. **`notion-mcp-server`, `postman-mcp-server`, `posthog`**: Unused by AntiOS core.

---

### 9. Documentation Forensic Audit

#### Q23: Is there a clear source of truth?
**NO.**  
AntiOS exhibits severe source-of-truth fragmentation across architecture, rules, and task state. `ARCHITECTURE_PROPOSAL.md` describes components that `DECISION_REGISTER.md` disproves; `docs/ACTIVE_CONTEXT.md` claims Phase 6 is active while `reports/PHASE_9_REPORT.md` describes Phase 9 completion; and `studylab-task-runner/SKILL.md` mandates test procedures that `stop_gate.py` has deprecated.

#### Q24: Is documentation synchronized with implementation?
**NO.**  
The implementation vs documentation matrix reveals that only **22.7% (5/22)** of documented capabilities match the actual code. **59.1% (13/22)** are in direct contradiction or completely missing from the codebase.

---

### 10. Architecture Forensic Audit

#### Q25: Does the implementation match the architecture?
**ONLY IN BROAD CONCEPT, NOT IN CONCRETE CODE.**  
The high-level demarcation (Platform Mechanism vs Project Policy) is valid and proven. However, the concrete implementation is unpatched, plagued by fail-open vulnerabilities, unindexed skills, and dead directory references.

#### Q26: Which Phase 9 conclusions remain valid?
1. Upstream blast radius containment (`rslib/` protection via tool hooks) is 100% effective.
2. Eliminating conversational self-certification via physical OS process verification is 100% effective.
3. Prompt injections cannot override Python process hooks.
4. Shell execution (`run_command`) bypasses IDE file write hooks.
5. Missing ambient runtimes (`yarn`, `node`) trap agents in retry loops.
6. Trivial test fabrication via `verify_task.py` subverts the Stop gate.

#### Q27: Which Phase 9 conclusions are invalid?
- **Invalid Claim**: Any implication that the 5 Phase 9 surgical patches were implemented in the AntiOS repository. The code on disk remains 100% identical to Phase 8.

#### Q28: What is still unknown?
1. **Optimal Maker-Checker Sizing**: The exact threshold of task complexity where subagent verification becomes cost-effective vs wasteful.
2. **Autonomous Runtime Repair**: Whether an agent can autonomously recover from broken ambient Node/Python environments without human intervention.

---

### 11. Complexity Forensic Audit

#### Q29: What can be removed?
1. **7 Duplicate Report Files**: Delete from the root workspace; retain in `reports/`.
2. **`PHASE_9_REPORTS.zip`**: Delete redundant archive from root.
3. **`sandbox/StudyLab_Treatment/.agents/sentinel/`**: Delete stale artifacts referencing `Anki-maths`.
4. **`verify_task.py` Fallback in `stop_gate.py`**: Prune lines 58–69 to eliminate test fabrication risks.
5. **StudySourceCore MCP references**: Prune from `FRAMEWORK_REQUIREMENTS.md`.

#### Q30: What must remain?
1. **`framework/scripts/hooks/pre_tool_guard.py`**: Hardened with fail-closed logic, `commonpath` prefix matching, and `.agents/` protection.
2. **`framework/scripts/hooks/stop_gate.py`**: Hardened to auto-discover `package.json` (`vitest:once`) and `pyproject.toml` (`pytest`), distinguishing environment crashes from test assertion failures.
3. **`docs/AGENTS.md`**: The 6 core directives of the AntiOS Global Constitution.
4. **`.agents/skills/studylab-task-runner`**: Relocated to the root workspace for platform discovery, updated to specify `TypeName='self'`.
5. **`docs/ACTIVE_CONTEXT.md`**: Re-anchored to track active Phase 10 engineering state.

---

## Reproducibility Evaluation (Part T)

Can an external developer clone AntiOS and reproduce these results?

| Step | Status | Forensic Finding & Missing Element |
| :--- | :---: | :--- |
| **1. Clone AntiOS** | **FAIL** | Root AntiOS is not a Git repository. Cannot be cloned directly via `git clone`. |
| **2. Install Prerequisites** | **PARTIAL** | No `README.md` or `setup.py` exists. Developer must deduce that Python 3.11, Node, and uv are required. |
| **3. Understand Architecture** | **PARTIAL** | Documents exist but contain major contradictions between proposals, registers, and stale reports. |
| **4. Activate Framework** | **FAIL** | Hooks are not mounted in the root workspace; skill is not discoverable by Antigravity in root. |
| **5. Run Tests** | **PASS** | `test_pre_tool_guard_forensics.py` and `test_stop_gate_forensics.py` run cleanly with `python3.11`. |
| **6. Reproduce Phase 9** | **PASS** | Adversarial vectors (8.3 short names, ancestor collisions, fail-open crashes, test forgery) reproduce 100%. |
| **7. Obtain Equivalent Results** | **PASS** | The failure modes are deterministic and process-repeatable. |

---

## Architectural Conclusion

AntiOS is **conceptually sound but practically unfinished**. Its core thesis—that deterministic code hooks beat natural language prompt rules—is decisively proven by empirical evidence. However, its implementation was left in a vulnerable, fail-open state with broken discoverability and stale documentation. 

Applying the 5 surgical hook fixes, relocating the skill for platform indexing, and synchronizing active context will transform AntiOS from a fragile prototype into a rock-solid engineering operating layer.
