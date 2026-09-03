# Release & Maintenance Workflow (`RELEASE_MAINTENANCE`)

Preparing version releases, updating dependencies, security patches, and repository hygiene.

## 1. Entry Conditions
- Milestone completion, dependency update mandate, or security patch requirement.

## 2. Lifecycle Progression
1. **INTAKE**: Review release milestone objectives, changelog items, and dependency alerts.
2. **UNDERSTAND**: Identify versioning scheme (SemVer), migration notes, and compatibility matrices.
3. **INVESTIGATE**: Run audit tools, check lockfile status, and verify clean git status.
4. **PLAN**: Draft release plan with risk tier HIGH. Define rollback checkpoints.
5. **IMPLEMENT**: Apply manifest version bumps, lockfile updates, and changelog consolidation.
6. **TEST**: Execute full multi-platform test suites across all configured test runners.
7. **VERIFY**: Mandatory Maker-Checker dispatch (`antios-verifier`) to validate clean working tree and tests.
8. **REVIEW**: Inspect release diff for extraneous changes.
9. **CONSOLIDATE**: Finalize release notes; update `docs/ACTIVE_CONTEXT.md`.
10. **COMPLETE**: Stop Gate runs all tests; exit code 0 permits completion.

## 3. Recovery Paths
- **Dependency Incompatibility**: Rollback manifest/lockfile bump to last clean commit.
