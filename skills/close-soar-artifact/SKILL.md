---
name: close-soar-artifact
description: "Close a SOAR case or alert with proper reason and documentation. Use when triage determines an alert is FP/BTP or investigation is complete. Requires artifact ID, type, closure reason, and root cause."
required_roles:
  soar: roles/chronicle.editor
personas: [tier1-analyst, tier2-analyst, tier3-analyst, incident-responder]
---

# Close SOAR Artifact Skill

Close a SOAR case or alert with the required reason, root cause, and justification comment.

## Inputs

- `ARTIFACT_ID` - The ID of the case or alert to close
- `ARTIFACT_TYPE` - Either "Case" or "Alert"
- `CLOSURE_REASON` - Must be one of:
  - `MALICIOUS` - Confirmed threat
  - `NOT_MALICIOUS` - False positive or benign
  - `MAINTENANCE` - System/maintenance activity
  - `INCONCLUSIVE` - Unable to determine
  - `UNKNOWN` - Unknown/other
- `ROOT_CAUSE` - Must match a predefined SOAR root cause (use `get_case_settings_root_causes` to list options)
- `CLOSURE_COMMENT` - Detailed justification for closure
- *(Optional)* `ALERT_GROUP_IDENTIFIERS` - Alert group identifiers
- *(Optional, for alerts)* `ASSIGN_TO_USER` - User to assign closed alert to
- *(Optional, for alerts)* `TAGS` - Comma-separated tags

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
IF "close-soar-artifact" NOT IN active_agent.permissions.primary_skills
   AND "close-soar-artifact" NOT IN active_agent.permissions.allowed_skills:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: Permission denied                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  The /close-soar-artifact skill is forbidden for <active_agent.name>. ║
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

### Step 1: Execute Closure

**For Cases:**
```
secops-soar.siemplify_close_case(
    case_id=ARTIFACT_ID,
    reason=CLOSURE_REASON,
    root_cause=ROOT_CAUSE,
    comment=CLOSURE_COMMENT,
    alert_group_identifiers=ALERT_GROUP_IDENTIFIERS
)
```

**For Alerts:**
```
secops-soar.siemplify_close_alert(
    alert_id=ARTIFACT_ID,
    reason=CLOSURE_REASON,
    root_cause=ROOT_CAUSE,
    comment=CLOSURE_COMMENT,
    assign_to_user=ASSIGN_TO_USER,
    tags=TAGS
)
```

## Required Outputs

| Output | Description |
|--------|-------------|
| `CLOSURE_STATUS` | Success/failure status of the closure |

## Common Closure Patterns

| Scenario | Reason | Typical Root Cause |
|----------|--------|-------------------|
| False Positive | `NOT_MALICIOUS` | "Legit action", "Normal behavior" |
| Duplicate | `NOT_MALICIOUS` | "Similar case is already under investigation" |
| Benign True Positive | `NOT_MALICIOUS` | "Legit action" |
| Confirmed Threat (remediated) | `MALICIOUS` | Varies by threat type |
| Unable to determine | `INCONCLUSIVE` | "Insufficient data" |

## Get Valid Root Causes

If unsure of valid root cause values:
```
secops-soar.get_case_settings_root_causes()
```
