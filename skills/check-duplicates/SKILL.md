---
name: check-duplicates
description: "Check for duplicate or similar SOAR cases. Use before deep analysis to avoid investigating the same incident twice. Takes a CASE_ID and returns list of similar cases."
required_roles:
  soar: roles/chronicle.editor
personas: [tier1-analyst, tier2-analyst, tier3-analyst]
---

# Check Duplicates Skill

Identify potentially duplicate or similar existing SOAR cases before starting deep analysis.

## Inputs

- `CASE_ID` - The ID of the current case to check
- `ALERT_GROUP_IDENTIFIERS` - Alert group identifiers for the case
- *(Optional)* `DAYS_BACK` - How many days to search back (default: 7)
- *(Optional)* `INCLUDE_OPEN` - Include open cases (default: true)
- *(Optional)* `INCLUDE_CLOSED` - Include closed cases (default: false)

## Pre-Flight Check (Mandatory)

> **This check runs BEFORE any skill logic. Do not skip.**

### 0.1 Agent Verification
```
IF active_agent IS NULL:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: No active agent                                ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  You must activate an agent before using skills.               ║
    ║                                                                ║
    ║  Run: /activate-agent <agent-name>                             ║
    ║                                                                ║
    ║  Available agents:                                             ║
    ║    tier1-soc-analyst, tier2-soc-analyst, threat-hunter, etc.   ║
    ╚════════════════════════════════════════════════════════════════╝
```

### 0.2 Permission Validation
```
IF "check-duplicates" NOT IN active_agent.permissions.primary_skills
   AND "check-duplicates" NOT IN active_agent.permissions.allowed_skills:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: Permission denied                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  The /check-duplicates skill is forbidden for <active_agent.name>. ║
    ║                                                                ║
    ║  Reason: Access restricted by agent role definition.           ║
    ║                                                                ║
    ║  Permitted alternatives for your role:                         ║
    ║    - <list from active_agent.permissions.primary_skills>       ║
    ║                                                                ║
    ║  To use this skill, escalate to an authorized agent.           ║
    ╚════════════════════════════════════════════════════════════════╝
```

## Workflow

### Step 1: Execute Similarity Check

```
secops-soar.siemplify_get_similar_cases(
    case_id=CASE_ID,
    alert_group_identifiers=ALERT_GROUP_IDENTIFIERS,
    days_back=DAYS_BACK,
    include_open_cases=INCLUDE_OPEN,
    include_closed_cases=INCLUDE_CLOSED
)
```

### Step 2: Process Results

Extract the list of similar case IDs from the response.

## Required Outputs

| Output | Description |
|--------|-------------|
| `SIMILAR_CASE_IDS` | List of case IDs identified as potentially similar/duplicate |
| `SIMILARITY_CHECK_STATUS` | Success/failure status of the check |

## Usage Pattern

```
1. Check duplicates BEFORE enrichment
2. If duplicates found:
   - Review similar case(s)
   - If confirmed duplicate: close as duplicate
   - If related but distinct: note correlation, continue
3. If no duplicates: proceed with analysis
```

## When Duplicates Are Found

If `SIMILAR_CASE_IDS` is not empty:

1. Document: "Closing as duplicate of [Similar Case ID]"
2. Close with:
   - Reason: `NOT_MALICIOUS`
   - Root cause: `Similar case is already under investigation`
