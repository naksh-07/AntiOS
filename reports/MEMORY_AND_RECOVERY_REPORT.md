# Memory and Recovery Report

## Evidence / Receipts

### Observation
Phase 7 generated detailed evidence artifacts and `verify_task.py` expected them. We evaluated whether cryptographic receipts or heavy evidence tracking is required.

### Analysis
- **Minimal Evidence**: Task definition, touched files, test run output, and final exit code.
- **Detailed Evidence**: Hashing files, creating cryptographic signatures, tracking every tool call.

Detailed evidence creates a large token overhead and massive noise in the context window. Unless we are dealing with untrusted third-party agents in a zero-trust environment, cryptographic receipts offer no measurable value over simply checking if `npm run test` exits with `0` on the current working tree.

### Conclusion
**KEEP MINIMAL EVIDENCE**. AntiOS will rely on standard Git working tree status and native test exit codes as the primary evidence of task completion. No cryptographic or bloated JSON receipt systems will be implemented.

## Documentation Drift

### Observation
Can we deterministically detect if code changed but docs did not?

### Analysis
Building a deterministic tool to link code to docs is an unsolved AI problem and requires complex semantic heuristics. However, we have an independent Maker-Checker (verifier subagent). The verifier can simply be instructed: "Check if the code changes require documentation updates."
This leverages the LLM's semantic understanding without building brittle deterministic rules.

### Conclusion
Documentation drift detection belongs in the **SKILL / SUBAGENT** layer, not the deterministic Hook layer.
