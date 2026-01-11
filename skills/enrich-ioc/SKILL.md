---
name: enrich-ioc
description: "Enrich an IOC (IP, domain, hash, URL) with threat intelligence. Use when you need to look up reputation and context for an indicator using GTI and SIEM. Returns threat intel findings, SIEM entity summary, and IOC match status."
required_roles:
  chronicle: roles/chronicle.viewer
  gti: GTI Standard
personas: [tier1-analyst, tier2-analyst, tier3-analyst, threat-hunter, incident-responder]
---

# Enrich IOC Skill

> **Alias:** This skill can also be invoked as `/ioc-enrich`

Perform standardized enrichment for a single Indicator of Compromise (IOC) using Google Threat Intelligence (GTI) and Chronicle SIEM.

## Inputs

- `IOC_VALUE` - The indicator value (e.g., "198.51.100.10", "evil-domain.com", "abcdef123456...", "http://bad.url/path")
- `IOC_TYPE` - The type: "IP Address", "Domain", "File Hash", or "URL"

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
IF "enrich-ioc" NOT IN active_agent.permissions.primary_skills
   AND "enrich-ioc" NOT IN active_agent.permissions.allowed_skills:
    BLOCK with message:
    ╔════════════════════════════════════════════════════════════════╗
    ║  SKILL BLOCKED: Permission denied                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  The /enrich-ioc skill is forbidden for <active_agent.name>.   ║
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

### Step 1: GTI Enrichment

Based on IOC_TYPE, call the appropriate GTI tool:

| IOC Type | Tool | Example |
|----------|------|---------|
| IP Address | `gti-mcp.get_ip_address_report` | `get_ip_address_report(ip_address="198.51.100.10")` |
| Domain | `gti-mcp.get_domain_report` | `get_domain_report(domain="evil-domain.com")` |
| File Hash | `gti-mcp.get_file_report` | `get_file_report(hash="abcdef123...")` |
| URL | `gti-mcp.get_url_report` | `get_url_report(url="http://bad.url/path")` |

Store key findings in `GTI_FINDINGS`:
- Reputation score
- Classification (malicious, suspicious, clean)
- Key relationships (contacted domains, IPs, etc.)
- Associated malware families or campaigns

**Error Handling:** If GTI fails (quota exceeded, IOC not found), note the limitation and proceed with SIEM enrichment.

### Step 2: SIEM Entity Lookup

```
secops-mcp.lookup_entity(entity_value=IOC_VALUE)
```

Store in `SIEM_ENTITY_SUMMARY`:
- First/last seen timestamps
- Related alerts
- Associated assets/users

### Step 3: SIEM IOC Match Check

```
secops-mcp.get_ioc_matches()
```

Check if IOC_VALUE appears in results. Store Yes/No in `SIEM_IOC_MATCH_STATUS`.

## Required Outputs

**After completing this skill, you MUST report these outputs:**

| Output | Description |
|--------|-------------|
| `GTI_FINDINGS` | Summary of GTI report (reputation, classification, relationships) |
| `SIEM_SUMMARY` | SIEM entity context (first/last seen, related alerts) |
| `IOC_MATCH_STATUS` | Yes/No - whether IOC appears in recent threat feed matches |
| `THREAT_SCORE` | Numerical threat score (0-100) based on GTI reputation |
| `MALICIOUS_CONFIDENCE` | Confidence level: `high`, `medium`, `low`, or `none` |

## Quick Reference

**GTI Tools:**
- `get_ip_address_report(ip_address)`
- `get_domain_report(domain)`
- `get_file_report(hash)`
- `get_url_report(url)`

**SIEM Tools:**
- `lookup_entity(entity_value)`
- `get_ioc_matches()`
