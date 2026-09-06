# AntiOS 2.0 Known Limitations & Boundaries (`KNOWN_LIMITATIONS.md`)

**Date**: 2026-09-06  
**Status**: ARCHITECTURE FREEZE CANDIDATE — TRUTHFUL DISCLOSURE  
**Authority**: Master Source of Truth / Level 1 Boundary Specification  

---

## 1. What Has NOT Been Proven?

In adherence to the core AntiOS philosophy of **Truthful Certification**, this document records the explicit limits, non-goals, unproven hypotheses, and operating boundaries of AntiOS 2.0.

AntiOS does not claim to solve every software engineering challenge. What has not been deterministically proven is disclosed below without evasion.

---

## 2. Platform Dependency Boundaries

1. **Host Platform Sovereignty**:
   - AntiOS is **Brain / Governance / Engineering Intelligence**.
   - It is **NOT** a standalone agent execution runtime, terminal multiplexer, or LLM inference server.
   - It requires **Google Antigravity** (or a compatible MCP/agent platform providing stdio tool events and lifecycle hooks) to act as the **Body / Execution Runtime**.
   - If the host platform crashes, fails to invoke hooks, or drops tool execution events, AntiOS cannot unilaterally resurrect execution.

2. **Single-Workspace Working Tree Assumption**:
   - AntiOS 2.0 is designed for a single active project working tree per mission.
   - It has **NOT** been proven to coordinate distributed multi-region git branches simultaneously without an upstream git server resolving merge conflicts.
   - Cross-repository coordination across independent git remotes must be managed via Antigravity's workspace configuration, not by AntiOS Core.

---

## 3. Epistemic & Cognitive Limits

1. **Human Business Intent Cannot Be Automated**:
   - AntiOS cannot invent business domain logic, proprietary pricing formulas, or subjective product decisions from thin air.
   - Ambiguous or contradictory human directives trigger `Stage 3: PLAN` escalation or `REQUIRE_HUMAN_APPROVAL`.
   - AntiOS proves that code matches tests; it cannot prove that the test accurately captures what the human business stakeholder wanted unless verified against acceptance criteria.

2. **Native Toolchain Availability**:
   - The Physical Stop Gate Ratchet requires that project test runners (`pytest`, `npm test`, `cargo test`, `go test`) exist on the host machine.
   - If a project requires a specialized toolchain that is not installed on the host OS, AntiOS correctly fails closed and reports `TOOLING_ENVIRONMENT_MISMATCH`. It will not forge green test runs.

---

## 4. Capability Demarcation: Native vs Simulated vs Harness-Only

| Capability Domain | Operational Mode | What Is Proven vs What Is Constrained |
| :--- | :---: | :--- |
| **Path Protection & Hook Interception** | **`NATIVE`** | Physically intercepts `pre_tool_guard.py` and `stop_gate.py` via Python stdio processes with sub-10ms latency. |
| **Subprocess Test Execution** | **`NATIVE`** | Executes native test commands directly via `subprocess.run` and evaluates exact return codes. |
| **Filesystem & Hash Tracking** | **`NATIVE`** | Computes SHA-256 digests directly on disk; verifies atomic rollbacks during partial write failures. |
| **Multi-Agent Message Passing** | **`SIMULATED`** | In standalone test suites, conversational turn-taking is simulated using structured JSON fixtures; full interactive UX requires Antigravity chat. |
| **Failure Injection Scenarios** | **`HARNESS-ONLY`**| Synthetic drift injection, corrupted state injections, and worker crashes are driven by isolated test harnesses; they do not alter host repositories. |

---

## 5. Explicit Architectural Non-Goals

AntiOS 2.0 intentionally excludes the following architectural patterns:

1. **No Background Daemons**:
   - AntiOS will never run continuous background watchers, systemd services, or memory-polling daemons. All operations are strictly event-driven.
2. **No Vector Databases**:
   - AntiOS rejects vector database infrastructure. Navigation relies on deterministic prefix trees, inverted indices, and multi-index knowledge graphs.
3. **No Autonomous Self-Modifying Governance**:
   - AntiOS rejects autonomous mutation of core governance. All structural evolution requires human-reviewed proposals (`EvolutionProposal`).
4. **No Recursive Agent Swarms**:
   - AntiOS strictly bounds delegation depth to $\le 2$ (Parent $\to$ Child). Swarms of uncoordinated subagents are prohibited.
5. **No Cryptographic Blockchain Receipts**:
   - Proofs use standard SHA-256 hashes grounded in local git history and physical disk bytes.
