---
name: document-in-soar
description: "Add a comment to a SOAR case to document findings, actions, or recommendations. Use to maintain audit trail during investigations. Requires CASE_ID and comment text."
required_roles:
  soar: roles/chronicle.editor
personas: [tier1-analyst, tier2-analyst, tier3-analyst, threat-hunter, incident-responder]
---

# Document in SOAR Skill

Add a standardized comment to a SOAR case to document findings, actions taken, or recommendations.

## Inputs

- `CASE_ID` - The SOAR case ID to add the comment to
- `COMMENT_TEXT` - The full text of the comment to be added
- *(Optional)* `ALERT_GROUP_IDENTIFIERS` - Alert group identifiers if required

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
IF "document-in-soar" NOT IN active_agent.permissions.primary_skills
   AND "document-in-soar" NOT IN active_agent.permissions.allowed_skills:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: Permission denied                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  The /document-in-soar skill is forbidden for <active_agent.name>. ║
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

### Step 1: Post Comment

```
secops-soar.post_case_comment(
    case_id=CASE_ID,
    comment=COMMENT_TEXT,
    alert_group_identifiers=ALERT_GROUP_IDENTIFIERS  // if provided
)
```

### Step 2: Verify Status

Check the API response to confirm the comment was posted successfully.

## Required Outputs

| Output | Description |
|--------|-------------|
| `COMMENT_POST_STATUS` | Success/failure status of the comment posting |

## Comment Templates

**Enrichment Summary:**
```
IOC Enrichment for [IOC_VALUE] ([IOC_TYPE]):
- GTI Reputation: [score/classification]
- SIEM Activity: [first/last seen, alert count]
- IOC Match: [Yes/No]
- Assessment: [Low/Medium/High risk]
- Recommendation: [next steps]
```

**Triage Decision:**
```
Alert Triage Complete:
- Classification: [FP/BTP/TP/Suspicious]
- Key Findings: [summary]
- Rationale: [why this classification]
- Action Taken: [closed/escalated]
```

**Investigation Update:**
```
Investigation Update [timestamp]:
- Actions Completed: [list]
- Findings: [summary]
- Next Steps: [planned actions]
```
