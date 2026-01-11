# LLM Agent Instructions

This file provides comprehensive guidance for AI assistants (Claude, Gemini, Antigravity, etc.) working with this security operations repository. It serves as the primary orientation document for understanding the agentic architecture, capabilities, and specialized workflows.

## Project Overview

This is an agentic security operations (SOC) framework designed to guide LLM agents through standardized security workflows. The repository follows a hierarchical structure: `Agent → SubAgent → Workflow → Skills → MCP/Tools`.

## Repository Structure

- `agents/` - **Single Source of Truth** for security roles (Agents). Contains Markdown files with YAML frontmatter defining objectives, permissions, and instructions.
- `workflows/` - Multi-step security procedures (playbooks) defined in YAML.
- `skills/` - Atomic security capabilities (tools). Each skill is a self-contained directory with a `SKILL.md` instruction file.
- `rules_bank/` - Master reference directory for runbooks, guidelines, and documentation.
- `reports/` - Generated security reports and investigation findings.
- `.claude/`, `.gemini/` - Tool-specific configurations using symlinks to the top-level `agents/` and `workflows/` directories.

## Agentic Hierarchy

### 1. Agents (`agents/`)
Agents define the **Identity** and **Permissions** of the AI assistant. Each agent file includes:
- **Critical Instructions**: Behavioral constraints prioritized by the LLM.
- **Objective**: The primary mission of the role.
- **Permissions**: Primary, allowed, and forbidden skills.
- **Workflows**: Authorized multi-step procedures.

**Available Agents:**
`tier1-soc-analyst`, `tier2-soc-analyst`, `tier3-soc-analyst`, `threat-hunter`, `incident-responder`, `cti-researcher`, `detection-engineer`, `soc-manager`, `ciso`, `compliance-manager`, `information-architect`, `red-team`.

### 2. Workflows (`workflows/`)
Workflows define the **Logic** for complex operations. They are orchestrated using the `/run-workflow` skill.
- **Triage**: `default-triage`, `quick-enrichment`.
- **Hunting**: `hypothesis-hunt`, `threat-actor-hunt`, `ioc-sweep`.
- **Incident Response**: `ransomware-incident`, `phishing-incident`, `account-compromise`.

### 3. Skills (`skills/`)
Skills define the **Capabilities**. Every skill performs a "Pre-Flight Check" against the active agent context to ensure authorization before execution.

## Operations

### Activating an Agent
Use the `/activate-agent` skill to establish your role and permissions for the session:
```
/activate-agent tier1-soc-analyst
```
*Note: Escalating to a higher privilege level (e.g., Level 1 → Level 4) requires explicit user confirmation.*

### Executing a Workflow
Use the `/run-workflow` skill to execute guided procedures:
```
/run-workflow default-triage CASE_ID=12345
```

### Generic Skills
Execute atomic skills directly if authorized by your agent:
```
/enrich-ioc IOC_VALUE=evil.com IOC_TYPE=domain
```

## Security Model

1. **Agent as Context**: Your role is defined by the loaded agent file. Follow its `Critical Instructions` strictly.
2. **Pre-Flight Checks**: Every skill validates that it is listed in your agent's `primary_skills` or `allowed_skills`.
3. **Privilege Levels**: Agents are ranked from Level 1 (Triage) to Level 4 (Incident Response).
4. **Containment**: Only Level 3+ agents can execute containment actions (e.g., host isolation).

## Multi-LLM Integration

- **Claude Code**: Accesses agents via `.claude/agents/` symlinks. Uses the `subagent_type` mapping.
- **Gemini CLI**: Uses `save_memory` to persist agent context across turns. Recommended to re-include agent file for long investigations: `gemini -p "@agents/tier1-soc-analyst.md ..."`
- **Antigravity**: Uses the top-level `agents/` directory to manage persona selection.

## Essential Context Sources

- **`LLMS-THESAURUS.md`**: Controlled vocabulary and security terminology definitions.
- **`LLMS-SITEMAP.md`**: Structural navigation and content relationships.
- **`agent_tool_mapping.md`**: Maps runbook actions to specific MCP tools.

## Report Generation

- **ALWAYS** write reports to the `./reports/` directory.
- Format: `<report_type>_<identifier>_<timestamp>.md`.
- Follow templates in `rules_bank/reporting_templates.md`.