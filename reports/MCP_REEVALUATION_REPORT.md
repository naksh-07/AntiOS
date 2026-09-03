# MCP Re-evaluation Report

## Objective
Evaluate the necessity of various MCPs (Model Context Protocol servers), specifically the GitHub MCP.

## Analysis
- **GitHub MCP**: Originally used to discover, clone, and branch the repository. However, in an isolated sandbox environment, the repository is already present locally. Standard git CLI commands (`run_command` with `git branch`, `git checkout`) are universally supported, faster, and do not require remote API calls or authentication tokens to be managed by the agent.
- **File System / Execution MCPs**: Antigravity natively provides `view_file`, `replace_file_content`, and `run_command`. Using an external MCP for these tasks adds latency and point of failure.

## Conclusion
**REMOVE/DEFER GitHub MCP**. For bounded StudyLab tasks, standard `git` CLI via `run_command` is strictly superior in speed, safety (local sandbox only), and simplicity. MCPs should only be introduced when interacting with truly external APIs (e.g., issue trackers) that lack a good CLI.
