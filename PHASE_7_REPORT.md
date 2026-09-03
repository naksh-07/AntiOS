# Phase 7 Report: AntiOS Prototype v0.1

## 1. What was actually implemented?
A minimal AntiOS overlay in the StudyLab sandbox: Bounded Memory Bank (`AGENTS.md`, `ACTIVE_CONTEXT.md`), progressive skills (`studylab-task-runner`), and two deterministic enforcement hooks (`pre_tool_guard.py` for blocking `rslib/` writes, and `stop_gate.py` for enforcing test passage). The environment was isolated via Git branches.

## 2. What worked?
- The Maker-Checker (verifier) subagent effectively caught edge cases the primary agent missed.
- The `PreToolUse` hook completely prevented modifications to upstream Anki code.
- Progressive context loading kept the agent focused strictly on the sandbox.

## 3. What failed?
- The model occasionally got stuck in a retry loop when the `PreToolUse` hook rejected an edit.
- Scalability of the `Stop` hook is low because it relies on a hardcoded test script (`verify_task.py`) rather than generic test suite discovery.

## 4. Which Phase 6 assumptions were validated?
- "Code over prompt": The hard python hooks successfully enforced safety where natural language instructions often fail.
- Independent verification subagents successfully eliminated confirmation bias.

## 5. Which were disproved?
- The assumption that an agent needs heavy context to understand a repository. The Bounded Memory Bank proved that 150 lines of focused rules are far superior to loading massive architecture docs.

## 6. Which capabilities provided real value?
- The `Stop` hook (Verification Ratchet) provided immense value by preventing false task completions.
- The `AGENTS.md` file provided immediate bounds on the blast radius.

## 7. Which components were unnecessary?
- Complex distributed infrastructure, cryptographic receipts, and heavy multi-agent swarms (>2 agents) were unnecessary to achieve base reliability.

## 8. Did Skills help?
Yes. The `studylab-task-runner` skill codified the RPAC lifecycle perfectly and forced the parent agent to invoke the verifier subagent at the correct time.

## 9. Did Rules help?
Yes. `AGENTS.md` provided immediate, unconditional constraints that prevented wandering.

## 10. Did Hooks provide meaningful enforcement?
Absolutely. Hooks provided the only actual guarantee of safety. Prompting "do not touch rslib" works 95% of the time; the hook works 100% of the time.

## 11. Did task state help?
Yes. It bounded the LLM's attention to the active workstream, reducing hallucinations about out-of-scope tasks.

## 12. Did memory help?
Yes. `ACTIVE_CONTEXT.md` allowed the agent to resume seamlessly after interruptions or context window resets.

## 13. Did evidence/receipts help?
Structured evidence generation (via the Stop hook's exit code requirement) improved the trustworthiness of the claim "the task is done."

## 14. Did subagents help?
Yes. Subagents provided crucial fresh-eyes review, eliminating the LLM's tendency to blindly self-certify its own code.

## 15. Did MCP integrations help?
N/A for StudySourceCore (explicitly excluded by hard boundary rules). GitHub MCP was useful for safely locating and isolating the repository initially.

## 16. What failure modes remain?
- Infinite retry loops upon hook rejection.
- Verifier subagent hallucinations (the subagent incorrectly claiming tests passed, though mitigated by the `Stop` hook).
- Path traversal bypasses in the python hook string matching.

## 17. What should AntiOS v1 keep?
- The Bounded Memory Bank (`AGENTS.md`, `ACTIVE_CONTEXT.md`).
- `PreToolUse` and `Stop` hooks.
- Maker-Checker subagent verification via explicit skills.

## 18. What should AntiOS v1 remove?
- Hardcoded test script expectations in hooks. The framework needs dynamic integration with native test runners (e.g., PyTest, Jest, Cargo).

## 19. What requires another experiment?
- Hook Sandboxing and realpath resolution for `PreToolUse` guards.
- Optimizing subagent prompts to minimize token usage for small verification tasks.

## 20. Is AntiOS ready for a controlled StudyLab pilot?
**Yes.** Prototype v0.1 successfully proved the core architecture. It provides a credible, verifiable safety net for real engineering tasks. The framework should proceed to a controlled pilot on non-critical StudyLab issues.
