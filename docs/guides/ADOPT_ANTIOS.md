# Universal Project Adoption Guide (`docs/guides/ADOPT_ANTIOS.md`)

This guide walks through the step-by-step process of adopting **AntiOS** to govern any target software repository.

---

## 1. Prerequisites

- Python 3.8+ installed on the host system.
- Target repository cloned locally and accessible on disk.
- AntiOS installed or cloned alongside or within the workspace.

---

## 2. Adoption Workflow

Adopting AntiOS is a deterministic, 5-step automated sequence:

```
[Target Repo] 
      |
      v  Step 1: Inspect
[inspect_repo.py] -> Detect language, manifests, existing runners
      |
      v  Step 2: Propose
[adapt_project.py --dry-run] -> Formulate AdaptationProposal
      |
      v  Step 3: Apply
[adapt_project.py --apply] -> Generate antios.config.json & .agents/
      |
      v  Step 4: Verify
[navigate_repo.py --list] -> Confirm subsystem map & tool routing
      |
      v  Step 5: Audit
[check_changeset.py] -> Validate Same Change Set policy compliance
```

### Step 1: Inspect Target Repository
Run the deterministic repository inspector against the target repository root:
```bash
python framework/scripts/tools/inspect_repo.py /path/to/target_repo
```
This scans for:
- Workspace topology (standalone vs monorepo)
- Existing git state and manifests (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`)
- Available test runners and linters on host PATH
- Existing AntiOS configuration or hook setups

### Step 2: Generate Adaptation Proposal
Analyze the adaptation requirements without touching the filesystem:
```bash
python framework/scripts/tools/adapt_project.py /path/to/target_repo --dry-run
```
AntiOS will inspect detected traits and formulate an `AdaptationProposal` detailing:
- Recommended test runners and commands
- Protected domain cores (critical models, schemas, or upstream logic)
- Protected zones (build outputs, vendor directories, virtual environments)
- Recommended skill bindings

### Step 3: Apply the Adapter
Generate the canonical `antios.config.json` configuration in the target repository:
```bash
python framework/scripts/tools/adapt_project.py /path/to/target_repo --apply
```
This safely creates:
1. `antios.config.json` at the target repository root.
2. Hook bindings in `.agents/hooks.json` directing `PreToolUse` and `Stop` to AntiOS scripts.
3. Essential documentation scaffolds (`docs/ACTIVE_CONTEXT.md`, `docs/AGENTS.md`).

### Step 4: Verify Navigation & Subsystems
Verify that AntiOS accurately maps the target repository subsystems:
```bash
python framework/scripts/tools/navigate_repo.py --repo-root /path/to/target_repo --list
```
Ensure that entrypoints, test suites, and blast radius mappings match project reality.

### Step 5: Run Verification Gate
Test that the newly configured Stop Gate can successfully execute the project's native tests:
```bash
python framework/scripts/hooks/stop_gate.py
```
If all tests pass, the repository is officially under AntiOS governance!

---

## 3. Polyglot & Multi-Stack Adoption

AntiOS includes built-in discovery rules for:
- **Python**: pytest, unittest, flake8, ruff, black, mypy, uv, poetry
- **TypeScript / JavaScript**: vitest, jest, mocha, npm test, eslint, prettier, tsc
- **Rust**: cargo test, cargo clippy, cargo build
- **Go**: go test, golangci-lint, go build

For custom or proprietary stacks, manually edit `antios.config.json` to define custom runner commands and timeouts. See the [Project Adapter Guide](PROJECT_ADAPTER.md) for full configuration details.
