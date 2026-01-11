---
name: find-relevant-case
description: "Search for existing SOAR cases related to specific indicators or entities. Use to find correlation with other investigations before starting new analysis. Takes search terms and returns matching case IDs."
required_roles:
  soar: roles/chronicle.editor
personas: [tier1-analyst, tier2-analyst, tier3-analyst, incident-responder]
---

# Find Relevant Case Skill

Identify existing SOAR cases that may be related to the current investigation based on IOCs, hostnames, usernames, or other entities.

## Inputs

- `SEARCH_TERMS` - List of values to search for (e.g., `["198.51.100.10", "mikeross-pc", "jsmith"]`)
- *(Optional)* `CASE_STATUS_FILTER` - Filter by status: "Opened", "Closed" (default: "Opened")
- *(Optional)* `TIME_FRAME_HOURS` - Lookback period for case creation/update
- *(Optional)* `MAX_RESULTS` - Maximum cases to return

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
IF "find-relevant-case" NOT IN active_agent.permissions.primary_skills
   AND "find-relevant-case" NOT IN active_agent.permissions.allowed_skills:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: Permission denied                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  The /find-relevant-case skill is forbidden for <active_agent.name>. ║
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

### Step 1: Construct Search Filter

Build a filter for `list_cases` based on search terms and filters.

**Note:** The `list_cases` tool may have limited ability to search within case entities. If direct entity search isn't supported, use broader filters and refine results.

### Step 2: Execute Search

```
secops-soar.list_cases(
    filter=constructed_filter,
    limit=MAX_RESULTS
)
```

### Step 3: Process Results

Extract case IDs and basic details (DisplayName, Priority) from results.

### Step 4: (Optional) Refine Results

If too many results, use `get_case_full_details` on a subset to verify entity presence:

```
secops-soar.get_case_full_details(case_id=candidate_case_id)
```

## Required Outputs

| Output | Description |
|--------|-------------|
| `RELEVANT_CASE_IDS` | List of case IDs that match the search |
| `RELEVANT_CASE_SUMMARIES` | Brief summaries (ID, name, priority) |
| `FIND_CASE_STATUS` | Success/failure status of the search |

## Limitations & Workarounds

The `list_cases` tool may not support direct entity searching. Alternatives:

1. **Broader filters** - Use time range, alert type, then manually review
2. **SIEM correlation** - Search SIEM for entity, check if events belong to a SOAR case
3. **Multiple searches** - Search each term separately, combine results
