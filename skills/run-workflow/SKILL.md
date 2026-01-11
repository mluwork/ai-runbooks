---
name: run-workflow
description: Execute a predefined security workflow (procedural guide)
trigger: /run-workflow <workflow-name> [INPUTS]
inputs:
  - WORKFLOW_NAME (required): Name of the workflow to run
  - ... (other inputs as required by the workflow)
---

# Skill: Run Workflow

This skill acts as a **Procedural Guide**. It loads a workflow definition and converts it into step-by-step instructions for the LLM to follow.

## Execution

### Step 1: Pre-Flight Check (Mandatory)
Perform the standard agent verification and permission validation.
- Ensure `run-workflow` is permitted for the active agent.

### Step 2: Load Workflow
1. Locate the workflow file in `workflows/` (e.g., `workflows/triage/default-triage.yaml`).
2. Read and parse the YAML content.

### Step 3: Validate Permissions
Verify that:
1. The workflow is listed in `active_agent.workflows`.
2. ALL skills defined in the workflow's `chain` are either in `active_agent.permissions.primary_skills` or `active_agent.permissions.allowed_skills`.

**If ANY skill in the chain is forbidden, BLOCK the entire workflow.**

### Step 4: Generate Procedural Prompt
Convert the YAML chain into a natural language procedure. For example:

```
You are executing the [Display Name] workflow.
Follow these steps precisely:

Step 1: Run [Skill 1] with [Inputs].
        Capture: [Outputs].
...
Step N: Run [Skill N] with [Inputs].

Report progress after each step. Ask for confirmation before critical actions (e.g., escalation, containment).
```

### Step 5: Guided Execution
Execute the generated procedure, providing feedback to the user as each step completes.

## Completion Criteria
- The workflow file was parsed.
- Chain-wide permission validation passed.
- The procedural prompt was generated and adopted.
- The workflow execution has started.