# Agentic SOC Runbooks

This repository provides an agentic security operations framework for AI-assisted cybersecurity workflows.

## Overview

Built by and for enterprise security teams, this project standardizes security operations across multiple AI platforms including Claude, Gemini, and Antigravity. It follows a modern agentic hierarchy (`Agent → SubAgent → Workflow → Skills`) to equip LLMs with specialized context and cognitive tools for high-rigor security investigations.

## Key Components

### 1. Agents (`/agents`)
Consolidated, role-based definitions that establish the identity and permissions of the AI assistant.
- **SOC Analysts (Tier 1-3)**: Monitoring, investigation, and expert analysis.
- **Threat Hunter**: Proactive hypothesis-driven hunting.
- **Incident Responder**: Full PICERL lifecycle management and containment.
- **CTI Researcher**: Threat intelligence research and dissemination.
- **Detection Engineer**: Detection lifecycle management.
- **SOC Manager**: Operational oversight and reporting.

### 2. Workflows (`/workflows`)
Orchestrated, multi-step procedures (playbooks) for complex security tasks.
- **Triage**: Default alert triage and quick enrichment.
- **Hunting**: Hypothesis-driven, actor-based, and IOC sweep hunts.
- **Incident Response**: Specialized workflows for ransomware, phishing, and account compromise.

### 3. Skills (`/skills`)
Atomic security capabilities (tools) used by agents to perform specific actions.
- **Enrichment**: GTI and SIEM-based indicator enrichment.
- **Investigation**: Deep-dive IOC analysis and cross-source correlation.
- **Action**: SOAR case management and containment actions.

## Repository Structure

```
ai_runbooks/
├── agents/                        # Single source of truth for security roles
├── workflows/                     # Multi-step security procedures (YAML)
├── skills/                        # Atomic capabilities and tool instructions
├── rules_bank/                    # Master reference directory for runbooks
│   ├── run_books/                 # Procedural guides (Reference)
│   ├── irps/                      # Incident Response Plans (Reference)
│   └── guidelines/                # Best practices and documentation
├── reports/                       # Generated security reports
└── mcp-security/                  # MCP server implementations
```

## Usage

1. **For Security Teams**: Activate the appropriate agent for your task using `/activate-agent <name>`.
2. **For Developers**:
   - Define new roles in `agents/`.
   - Define new procedures in `workflows/`.
   - Add new capabilities in `skills/`.
3. **For AI Assistants**: Use the `/activate-agent` skill to load context and permissions at the start of every session.

## Integration

This project is designed to work with:
- Chronicle SIEM
- SOAR platforms
- Google Threat Intelligence (GTI)
- Security Command Center (SCC)
- Various MCP (Model Context Protocol) tools

## License

This project is licensed under the Apache License 2.0 - see the `LICENSE` file for details.

---

## AI Tool Integration

### Claude Code
- Uses the `.claude/` directory for configuration.
- Reads context from `.claude/agents/` and `.claude/workflows/` symlinks.
- See `CLAUDE.md` for specific guidance.

### Gemini CLI
- Uses the `.gemini/` directory for configuration.
- Uses `save_memory` to persist agent context across turns.
- See `GEMINI.md` for specific guidance.

### Antigravity
- Interacts with the top-level `agents/` directory for persona management and delegation.