# AntiOS v1 Verification Model & Ratchet Architecture (`ANTIOS_VERIFICATION_MODEL.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Define the evidence hierarchy, test ratchet mechanics, Maker-Checker risk tiers, and subagent delegation policy, establishing trustworthy, reproducible verification while permanently eliminating dangerous ad-hoc test scripts.

---

## 1. The Evidence Trust Hierarchy

A central failure of unassisted LLMs is **conversational self-certification** ("I have reviewed the code and confirmed it works"). AntiOS v1 codifies four strict, epistemological verification levels:

```text
┌──────────────┬────────────────────────┬─────────────────────────────────────┐
│ LEVEL        │ EVIDENCE TYPE          │ OPERATIONAL DEFINITION              │
├──────────────┼────────────────────────┼─────────────────────────────────────┤
│ 1. CLAIMED   │ Pure Natural Language  │ Agent asserts "All tests pass" or   │
│              │ (Trust: ZERO)          │ "Functionality is verified" in text.│
├──────────────┼────────────────────────┼─────────────────────────────────────┤
│ 2. OBSERVED  │ Passive Static Reading │ Agent viewed file contents, diffs,  │
│              │ (Trust: LOW)           │ or compiler logs via read tools.    │
├──────────────┼────────────────────────┼─────────────────────────────────────┤
│ 3. EXECUTED  │ Direct Subprocess Run  │ Test runner or compiler command was │
│              │ (Trust: MEDIUM)        │ launched and emitted process logs.  │
├──────────────┼────────────────────────┼─────────────────────────────────────┤
│ 4. VERIFIED  │ Deterministic Ratchet  │ Native test suite executed against  │
│              │ (Trust: COMPLETE)      │ the FINAL working tree with exit 0. │
└──────────────┴────────────────────────┴─────────────────────────────────────┘
```

### Definitional Rules:
- **`CLAIMED`**: Conversational claims carry 0 evidentiary weight. The Stop gate ignores chat text entirely.
- **`OBSERVED`**: Useful for orientation, but observing code does not guarantee runtime validity.
- **`EXECUTED`**: Demonstrates that code was run at some point in time, but vulnerable to post-execution mutations.
- **`VERIFIED`**: The ONLY state accepted for task completion. Satisfied strictly when:
  1. A registered, native project test suite (`vitest:once`, `pytest`, `cargo test`) executes.
  2. The process returncode is physically `0`.
  3. The execution occurs against the **exact working tree** submitted at turn completion.

---

## 2. Permanent Excise of Insecure Verification Patterns

### Elimination of `verify_task.py`
- **Forensic Evidence (Phase 9 Attack 4.3 & Phase 10 Finding F-06)**:
  - Prototype `stop_gate.py` executed any `verify_task.py` found in the root.
  - An agent could fabricate a dummy script containing `import sys; sys.exit(0)`, completely subverting the Stop gate without testing application code.
- **v1 Policy**:
  - `verify_task.py` fallback is **PERMANENTLY REMOVED** from `stop_gate.py`.
  - All verification must run through registered project test suites (`package.json`, `pyproject.toml`, or project toolchains).
  - Arbitrary agent-authored root scripts are NEVER trusted as verification evidence.

---

## 3. The Working-Tree Verification Ratchet

### The Problem: Ratchet Expiry
$$\text{CHANGE} \longrightarrow \text{TEST} \longrightarrow \text{MUTATE AGAIN} \longrightarrow \text{DONE}$$
If an agent executes tests, modifies a file afterward (e.g. adding a comment, refactoring an import, or tweaking formatting), and marks the task done, the earlier test evidence has **expired**. Unobserved syntax or regression errors can slip into production.

### The v1 Ratchet Mechanism: Atomic Completion Verification
AntiOS v1 implements the smallest, most reliable mechanism without building a complex coverage engine:
1. **Stop Gate Execution**: The verification ratchet is mounted on Antigravity's native `Stop` event.
2. **Atomic Run-at-Stop**: When the agent attempts to stop or complete its turn, `stop_gate.py` executes the native test runner **at the moment of the stop attempt**.
3. **Zero Gap**: Because `stop_gate.py` runs synchronously on the final working tree immediately prior to task exit, there is zero time window for post-test mutations. If any file was changed after prior testing, the Stop gate verifies the change before allowing exit.

---

## 4. Maker-Checker Policy (Risk-Tiered Verification)

Independent verification eliminates confirmation bias, but spawning subagents on trivial tasks adds 30–60s latency and token overhead. AntiOS v1 establishes a **Risk-Tiered Maker-Checker Policy**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MAKER-CHECKER MATRIX                             │
├─────────────┬───────────────────────────────┬───────────────────────────────┤
│ RISK TIER   │ TASK CHARACTERISTICS          │ VERIFICATION REQUIREMENT      │
├─────────────┼───────────────────────────────┼───────────────────────────────┤
│ LOW RISK    │ • Typos & markdown formatting │ Solo Execution Allowed.       │
│             │ • Minor doc updates           │ Local compiler / syntax check.│
│             │ • Non-functional comments     │ No fresh subagent required.   │
├─────────────┼───────────────────────────────┼───────────────────────────────┤
│ MEDIUM RISK │ • Non-critical bug fixes      │ Conditional Checker.          │
│             │ • Isolated UI adjustments     │ Parent runs native test suite.│
│             │ • Standard feature additions  │ Checker spawned if complex.   │
├─────────────┼───────────────────────────────┼───────────────────────────────┤
│ HIGH RISK   │ • Reviewer FSM & transitions  │ MANDATORY MAKER-CHECKER.      │
│             │ • Double SQLite storage       │ Fresh subagent (TypeName=self)│
│             │ • APKG packaging boundary     │ must audit working tree and   │
│             │ • Security hooks & policy     │ execute native test suites.   │
└─────────────┴───────────────────────────────┴───────────────────────────────┘
```

### The Verifier Subagent Contract:
1. **Runtime Type**: Must be spawned with **`TypeName='self'`** (inherits execution tools). Spawning with `research` is strictly prohibited because `research` has no `run_command` and cannot execute tests.
2. **Context Segregation**: The verifier receives a fresh, isolated context window containing only the acceptance criteria, task objective, and diff summary—bypassing the parent agent's reasoning rationalizations.
3. **Required Verifier Actions**:
   - Inspect `git status` and `git diff` for untracked or accidental file modifications.
   - Execute native test commands directly via `run_command`.
   - Verify that documentation was updated in the **Same Change Set**.
   - Output structured verdict: `PASS`, `FAIL`, or `BLOCK`.

---

## 5. Subagent Delegation Policy (AntiOS Multi-Agent Bounds)

AntiOS v1 rejects multi-tier agent swarms (>2-3 agents) based on Phase 6 and 7 findings. We define **WHEN to delegate**, leaving **HOW to run** to Antigravity:

### Delegation Rules:
1. **Shallow Depth Law**: Subagent nesting depth must NEVER exceed 2 ($\text{Parent} \to \text{Child}$). Children must not spawn grand-children.
2. **Max Workforce Sizing**: Max 1 active concurrent subagent per verification task.
3. **Explicit Handoff Payload**: Every subagent dispatch must provide:
   - Target task and acceptance criteria.
   - Paths modified by Maker.
   - Explicit test commands to execute.
4. **Failure Handling**:
   - If a subagent crashes, times out, or hallucinates, the parent agent must inspect the raw test logs directly or re-execute the test.
   - The Stop gate provides the deterministic backstop: even if a subagent falsely reports "pass", `stop_gate.py` will physically re-execute tests upon task completion.
