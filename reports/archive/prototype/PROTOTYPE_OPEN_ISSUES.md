# Prototype Open Issues (v0.1)

## Bugs
- `PreToolUse` hook currently performs simple string matching (`rslib/`). This can be bypassed with path traversals (e.g., `../StudyLab/rslib`). Needs realpath resolution in v1.0.
- `Stop` hook relies on `verify_task.py` which must be manually seeded. A generic test discovery mechanism is missing.

## Architectural Uncertainties
- **Subagent Delegation Overhead**: Spawning a fresh subagent for verification consumes significant token budget. Can we optimize this for smaller tasks?
- **Active Context Decay**: As tasks grow complex, `ACTIVE_CONTEXT.md` tends to exceed the 50-line limit naturally. Should we allow hierarchical task files?

## Missing Capabilities
- **Artifact/Schema Validation**: Due to the hard boundary exclusion of `StudySourceCore`, we lack deterministic JSON/APKG schema validation. A lightweight native StudyLab schema validator must be created.
- **Auto-Recovery from Blocks**: When an agent hits a `PreToolUse` deny, it occasionally gets stuck in a loop of retrying the exact same edit.

## Ideas Requiring More Research
- **Cryptographic Receipts**: Do we need to hash the file states to prevent the LLM from lying about "Same Change Set" synchronicity?
- **Hook Sandboxing**: Running hook scripts as plain Python has security implications if the model maliciously rewrites the hook before triggering it. Hook files might need to be read-only or permission-gated.
