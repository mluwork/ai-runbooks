## Step 0: Pre-Flight Check (Mandatory)

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
IF "<this-skill>" NOT IN active_agent.permissions.primary_skills
   AND "<this-skill>" NOT IN active_agent.permissions.allowed_skills:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: Permission denied                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  The /<this-skill> skill is forbidden for <active_agent.name>. ║
    ║                                                                ║
    ║  Reason: Access restricted by agent role definition.           ║
    ║                                                                ║
    ║  Permitted alternatives for your role:                         ║
    ║    - <list from active_agent.permissions.primary_skills>       ║
    ║                                                                ║
    ║  To use this skill, escalate to an authorized agent.           ║
    ╚════════════════════════════════════════════════════════════════╝
```
