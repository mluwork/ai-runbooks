# Agentic Workflow Architecture & Design

## 1. Executive Summary

This document describes the **Agentic Security Operations Center (SOC)** framework implemented in this repository. The architecture is designed to orchestrate Large Language Model (LLM) agents through standardized, auditable, and secure security workflows.

The core design philosophy rests on a hierarchical model: **Agent → Workflow → Skill → Tool**. This ensures that autonomous agents operate within strict behavioral guardrails, using only authorized capabilities, while following deterministic procedures for complex tasks.

## 2. Core Concepts

### 2.1 The Agent (Persona)
An **Agent** represents a specific security role (e.g., *Tier 1 Analyst*, *Threat Hunter*). It is the single source of truth for identity and permissions.
*   **Definition**: `agents/<agent-name>.md`
*   **Responsibility**: Defines *who* is acting.
*   **Components**:
    *   **Objective**: High-level mission statement.
    *   **Permissions**: Allowlist of enabled `skills` (capabilities).
    *   **Workflow Authorization**: List of `workflows` the agent is allowed to execute.
    *   **Critical Instructions**: Inviolate rules (e.g., "Do not perform active containment without approval").

### 2.2 The Skill (Capability)
A **Skill** is an atomic, reusable capability (e.g., *Triage Alert*, *Enrich IOC*, *Search Logs*).
*   **Definition**: `skills/<skill-name>/SKILL.md`
*   **Responsibility**: Defines *what* can be done.
*   **Mechanism**: Contains natural language instructions, input requirements, and—crucially—a **Pre-Flight Check** that enforces security boundaries.

### 2.3 The Workflow (Procedure)
A **Workflow** is a multi-step procedure that chains multiple skills together to achieve a complex goal (e.g., *Ransomware Investigation*, *Phishing Response*).
*   **Definition**: `workflows/<category>/<workflow-name>.yaml` (or `.md`)
*   **Responsibility**: Defines *how* a process is executed.
*   **Mechanism**: Structured as a sequence of steps, orchestrated by the generic `/run-workflow` skill.

## 3. Architecture & Directory Structure

```text
.
├── agents/                  # IDENTITY Definitions
│   ├── tier1-soc-analyst.md
│   └── threat-hunter.md
├── workflows/               # PROCEDURAL Logic
│   ├── triage/
│   │   └── default-triage.yaml
│   └── response/
├── skills/                  # ATOMIC Capabilities
│   ├── triage-alert/
│   │   └── SKILL.md
│   ├── enrich-ioc/
│   └── run-workflow/        # The Orchestrator Skill
├── rules_bank/              # KNOWLEDGE Base
│   └── runbooks/
└── reports/                 # OUTPUT Artifacts
```

## 4. Execution Model

The framework uses a **Permission-Based Execution Model**. Agents cannot simply "do" things; they must invoke Skills, and those Skills verify the Agent's authority before executing.

### 4.1 The Security Boundary (Pre-Flight Check)

Every `SKILL.md` includes a mandatory "Pre-Flight Check" section. This is pseudo-code or logic that the LLM *must* strictly evaluate before proceeding.

**Example Logic:**
```text
IF active_agent IS NULL:
    BLOCK execution
IF skill_name NOT IN active_agent.permissions:
    BLOCK execution with "Permission Denied"
```

This mechanism ensures that a *Tier 1 Analyst* cannot execute a *Host Isolation* skill, even if they know the skill exists, because the *Host Isolation* skill's pre-flight check will fail against the Tier 1 Agent's permission set.

### 4.2 Workflow Orchestration

Workflows are not executed implicitly. They are executed via the `/run-workflow` skill.

1.  **Trigger**: User or Agent invokes `/run-workflow name="default-triage"`.
2.  **Orchestrator Validation**:
    *   The `run-workflow` skill starts.
    *   **Check 1**: Is the agent allowed to use `run-workflow`?
    *   **Check 2**: Is the specific workflow (`default-triage`) listed in the agent's authorized workflows?
    *   **Check 3 (Deep Verification)**: Does the agent have permissions for *every single skill* required by the workflow?
3.  **Execution**: If all checks pass, the orchestrator converts the YAML steps into a prompt chain and guides the agent through the process.

## 5. Design Patterns

### 5.1 Symlink Configuration
To support multiple LLM frontends (e.g., Gemini CLI, Claude Code), the repository uses symlinks (e.g., `.claude/agents -> ../agents`). This ensures a **Single Source of Truth**. Updates to `agents/` immediately propagate to all tool configurations.

### 5.2 Context Persistence
For CLI tools (like `gemini-cli`), the agent's context (the "Persona") is loaded at the start of a session (e.g., via `@agents/tier1-soc-analyst.md`). This persistence is critical for maintaining the "Role" across multiple turns of a conversation.

### 5.3 Human-in-the-Loop
Critical actions (like containment or external communications) can be flagged in the Agent definition as requiring confirmation. The `confirm-action` skill facilitates this interaction, ensuring the LLM pauses for explicit user approval.

## 6. Platform Implementation

While the core architecture (Agents/Workflows/Skills) is platform-agnostic, the implementation details vary slightly by LLM interface.

### 6.1 Feature Matrix

| Feature | Claude Code | Gemini CLI | Antigravity |
| :--- | :--- | :--- | :--- |
| **Agent Discovery** | Symlinked `.claude` directory | CLI flag `-p` or aliases | Native `agents/` directory |
| **Persistence** | Session-based | `save_memory` / manual context | Native Agent State |
| **Orchestrator** | `subagent_type` logic | Local CLI logic | Agentic Mode |
| **Workflow Path** | `.claude/workflows` | `workflows/` | `workflows/` |

### 6.2 Implementation Notes

*   **Claude Code**: Relies heavily on directory structure. The `.claude` directory contains symlinks to the top-level `agents` and `workflows` to ensure the tool can "see" the authorized actions.
*   **Gemini CLI**: Typically uses a "bootstrap" approach where the agent file is loaded into context at the start of the session.
*   **Antigravity**: Designed as a first-class citizen; can read the `agents` directory directly and maintain state via `task_boundary`.

## 7. Documentation

For detailed usage instructions, command references, and setup guides, please refer to the **[User Guide](user_guide.md)**.
