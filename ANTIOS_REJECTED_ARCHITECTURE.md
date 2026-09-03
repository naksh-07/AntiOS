# AntiOS v1 Rejected Architecture Ledger (`ANTIOS_REJECTED_ARCHITECTURE.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Formally document and permanently classify all speculative, disproved, redundant, or insecure architectural patterns that were evaluated and rejected during Phases 6–10.

> **Purpose for Future Agents**:  
> *Do NOT rediscover or reintroduce these components.*  
> *Every component listed below was tested, found wanting, and formally excised. The empirical rationales below are permanent.*

---

## 1. Master Rejected Architecture Ledger

| # | Rejected Component / Pattern | Phase Evaluated | Verdict | Empirical Rationale for Rejection |
| :-: | :--- | :---: | :---: | :--- |
| **1** | **Cryptographic Execution Receipts** | Phase 8 & 10 | **PERMANENTLY REJECTED** | Evaluated storing SHA-256 state hashes in `evidence/`. Proved that file hashes only prove state changed, not that the change was functionally or pedagogically correct. Suffers fatal **Ratchet Expiry**: subsequent edits invalidate earlier hashes. Real-time OS process verification at task completion replaces static receipts. |
| **2** | **Custom AST Blast-Radius Engine** | Phase 8 & 10 | **PERMANENTLY REJECTED** | Proposed building an AST regex parser to map downstream dependencies. Disproved: regex AST parsers give false confidence and miss dynamic imports. Native TypeScript compiler (`tsc`) and Vitest module graphs provide 100% accurate, zero-maintenance dependency analysis. |
| **3** | **AntiOS Schema Validators** | Phase 8 & 10 | **PERMANENTLY REJECTED** | Proposed duplicating StudyLab's 20-field question schema in AntiOS Python scripts. Disproved: duplicates domain truth, creates synchronization lag, and violates Bounded Context. StudyLab's native compiler (`generate_apkg.py`) natively validates artifacts during build. |
| **4** | **Arbitrary `verify_task.py` Fallback** | Phase 9 & 10 | **PERMANENTLY REJECTED** | Hardcoded script fallback in `stop_gate.py` allowed trivial test forgery (`import sys; sys.exit(0)`), completely bypassing verification. All verification must execute through registered, native project test suites. |
| **5** | **Large Hierarchical Agent Swarms** | Phase 6 & 7 | **PERMANENTLY REJECTED** | Evaluated multi-tier agent trees (>3 agents). Proved to introduce massive coordination latency (120s+), context fragmentation, and runaway token bills without improving final code quality on bounded software tasks. Shallow hierarchy (1 Maker, 1 Checker, Depth $\le 2$) is strictly enforced. |
| **6** | **Redundant GitHub MCP Usage** | Phase 8 & 10 | **PERMANENTLY REJECTED (for local work)** | Using GitHub MCP for local git operations (status, diff, commit, checkout) was slow, required WAN network roundtrips, consumed unnecessary tokens, and failed on unpushed local sandboxes. Local `git` CLI via `run_command` is strictly superior. |
| **7** | **StudySourceCore MCP Integration** | Phase 8, 10 & 11 | **PERMANENTLY EXCISED & OUT OF SCOPE** | StudySourceCore is an external project. Domain contracts belong to StudyLab. Integrating StudySourceCore violated project scope and added fragile stdio dependencies. Strictly forbidden from inspection, cloning, or integration. |
| **8** | **Custom Agent Runtime / Orchestrator Daemon** | Phase 6 & 10 | **PERMANENTLY REJECTED** | Building custom agent runner processes, thread pools, or background IPC daemons duplicates Antigravity's native platform primitives (`invoke_subagent`, `schedule`). AntiOS defines *when* and *why* to delegate, not *how* agents run. |
| **9** | **Vector Memory Databases (Chroma/Pinecone)** | Phase 6 & 10 | **PERMANENTLY REJECTED** | Vector memory adds opaque retrieval failures, embedding model dependencies, and zero transparency. Bounded, version-controlled markdown files (`ACTIVE_CONTEXT.md`, `AGENTS.md`) provide complete transparency, git-diffability, and zero infrastructure overhead. |
| **10** | **Custom Execution Journals / State Databases** | Phase 6 & 10 | **PERMANENTLY REJECTED** | Custom state logging databases duplicate Antigravity's native, persistent, chronological `transcript.jsonl` audit stream. |
| **11** | **LLM-as-a-Judge Semantic Drift Checkers** | Phase 6 & 9 | **PERMANENTLY REJECTED** | Using non-deterministic LLM calls as blocking CI/Stop gates introduces flakiness, high token costs, and prompt-injection risks. Enforced via Same Change Set rule and human review instead. |
| **12** | **Fail-Open Hook Error Handling** | Phase 9 & 10 | **PERMANENTLY REJECTED** | The prototype pattern `except Exception as e: return allow` represented a catastrophic security failure. Strict **Fail-Closed** logic is permanently mandated. |

---

## 2. Rationale Summary for Architectural Memory

```text
       ┌────────────────────────────────────────────────────────┐
       │             WHY THESE WERE PERMANENTLY CUT             │
       ├────────────────────────────────────────────────────────┤
       │ 1. Duplicated Antigravity: Daemons, swarms, journals   │
       │ 2. Duplicated Toolchain:   AST parsers, regex checkers │
       │ 3. Duplicated StudyLab:    Schema validators, compiler │
       │ 4. Vulnerable to Bypasses: verify_task.py, fail-open   │
       │ 5. Wasteful Overhead:      Vector DBs, GitHub MCP      │
       └────────────────────────────────────────────────────────┘
```
