---
name: activate-agent
description: Activate a security agent to establish role context and permissions
trigger: /activate-agent <agent-name>
inputs:
  - AGENT_NAME (required): Name of agent to activate
---

# Skill: Activate Agent

Use this skill at the beginning of a session or when switching roles to load the appropriate agent context, permissions, and workflows.

## Input
- `AGENT_NAME`: The agent identifier (e.g., `tier1-soc-analyst`)

## Execution

### Step 1: Load Agent Definition
1. Read `agents/${AGENT_NAME}.md`.
2. Parse the YAML frontmatter to extract the agent's identity, permissions, and IAM requirements.
3. Parse the Markdown body to extract the `Objective`, `Critical Instructions`, and `Standard Procedures`.

### Step 2: Detect Privilege Change
Compare the `target_agent.privilege_level` with the `current_agent.privilege_level` (if any).

- If `current_agent` is NULL → change_type = "INITIAL_ACTIVATION"
- If `target_level` > `current_level` → change_type = "ESCALATION"
- If `target_level` < `current_level` → change_type = "DOWNGRADE"
- If `target_level` == `current_level` → change_type = "LATERAL_MOVE"

### Step 3: Handle Escalation
If `change_type` is **ESCALATION**, you MUST display a warning and wait for user confirmation:

```
╔════════════════════════════════════════════════════════════════╗
║  ⚠️  PRIVILEGE ESCALATION DETECTED                             ║
╠════════════════════════════════════════════════════════════════╣
║  Current Agent: <current_agent.name> (Level <current_level>)   ║
║  Target Agent:  <target_agent.name> (Level <target_level>)     ║
║                                                                ║
║  This grants access to higher-privilege skills and potentially ║
║  containment actions.                                          ║
║                                                                ║
║  Type "CONFIRM" to proceed, or anything else to cancel.        ║
╚════════════════════════════════════════════════════════════════╝
```

**If the user does not type "CONFIRM", ABORT the activation.**

### Step 4: Activate Context
1. Update the system prompt context with the contents of the agent file.
2. Adopt the instructions and constraints defined in the `Critical Instructions` section immediately.
3. Display the activation success message:

```
╔════════════════════════════════════════════════════════════════╗
║  ✓ Agent Activated: <display_name>                             ║
╠════════════════════════════════════════════════════════════════╣
║  Privilege Level: <level>                                      ║
║  Escalation Path: <escalation_path>                            ║
║                                                                ║
║  Primary Skills: <list primary_skills>                         ║
║  Available Workflows: <list workflows>                         ║
╚════════════════════════════════════════════════════════════════╝
```

### Step 5: Persist State (Gemini CLI)
Call the `save_memory` tool to persist the active agent for recall in future turns:
- `save_memory(fact="Active Agent is [agent-name] with privilege level [level]")`

## Completion Criteria
- The agent file has been read and parsed.
- Escalation confirmation was obtained (if required).
- The `save_memory` tool was called to persist the state.
- The assistant is now operating under the constraints of the new agent.
