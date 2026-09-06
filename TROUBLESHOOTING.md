# AntiOS Diagnostics & Troubleshooting Guide

This guide describes how to diagnose, repair, and troubleshoot AntiOS instances.

---

## 1. Quick Diagnostics: `antios doctor`

When experiencing issues, runtime blocks, or suspected drift, run `antios doctor`:

```bash
antios doctor
# Or machine-readable JSON:
antios doctor --json
```

`antios doctor` inspects:
- **Installation Integrity**: Validates `.antios/manifest.json` and artifact presence.
- **Version Alignment**: Checks framework vs instance version synchrony.
- **Adapter Configuration**: Verifies `antios.config.json` existence and policy validity.
- **Runtime Closure**: Audits `.antios/runtime/` for framework source leaks.
- **Git State**: Checks branch, head commit, and working tree cleanliness.
- **Project Drift**: Evaluates drift across 10 canonical domains via `ProjectDriftEngine`.
- **Active Context Bounds**: Validates `docs/ACTIVE_CONTEXT.md` is within the $\le 60$ lines budget (`INV-09`).

### Secret Redaction Guarantee
`antios doctor` automatically passes all findings through an automated redaction filter. GitHub tokens (`gho_*`), API keys, and credential strings are **never** printed to the console or logs.

---

## 2. Compact Status: `antios status`

To get an instant operational summary:

```bash
antios status
```

Answers the 8 core operational questions:
- What version am I running?
- Is AntiOS installed correctly?
- Is this project adapted?
- Is the project healthy?
- Is drift detected?
- Are durable proofs valid?
- Is the runtime engine healthy?
- Are updates available?
- Is human intervention required?

---

## 3. Conservative Repair: `antios repair`

AntiOS repairs are conservative and proposal-governed:

```
DETECT  ──>  EXPLAIN  ──>  PROPOSE  ──>  VERIFY  ──>  APPLY
```

### Step 1: Check for Drift without Modifying
```bash
antios repair --check
```

### Step 2: Inspect the Repair Plan
```bash
antios repair --plan
```
Lists exactly which missing or damaged generated/managed files will be restored.

### Step 3: Apply Repair
```bash
antios repair --apply
```
Restores missing managed files while strictly preserving user-modified assets.

---

## 4. Common Diagnostic Findings & Remediation

| Finding | Severity | Cause | Remediation |
| :--- | :--- | :--- | :--- |
| `Manifest Existence` | `WARNING` | Project is not initialized | Run `antios install` |
| `Version Consistency` | `INFO` | Instance is older than framework | Run `antios update` |
| `Runtime Closure` | `WARNING` | AST import of absent framework | Run `antios repair` |
| `Active Context Bounds` | `WARNING` | Context exceeded 60 lines | Run context distillation |
| `Git Working Tree` | `INFO` | Uncommitted modifications | Commit or stash changes |
| `Test Ownership Drift` | `CRITICAL`| Test runner missing in config | Update `test_runners` in `antios.config.json` |
