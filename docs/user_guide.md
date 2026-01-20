# Agentic SOC Framework: User Guide

## 1. Introduction
This guide corresponds to the **Agentic SOC Framework**, a system where you perform security operations by collaborating with AI agents that assume specific roles (Personas).

Instead of memorizing hundreds of tool commands, you interact with an **Agent** (like a Tier 1 Analyst) who knows how to use the tools for you. You provide high-level objectives, and the Agent executes the technical steps, following strict security protocols.

## 2. Platform Setup & Interaction

The way you interact with the agent depends on your platform.

| Interface | Activation | Interaction Style |
| :--- | :--- | :--- |
| **Claude Code** | `/activate-agent <name>` | **Slash Commands** for everything (Workflows & Skills). |
| **Gemini CLI** | `gemini` (Interactive) | **Slash Commands** for Workflows.<br>**Natural Language** for Skills. |
| **Antigravity** | Auto-detected | Native Agentic Mode. |

### 2.1 Gemini CLI: Interactive Mode
To start an interactive session:
```bash
gemini
```
*Tip: You can pre-load an agent with `gemini -p "@agents/tier1-soc-analyst.md"`.*

**Key Difference: Slash Commands vs. Natural Language**
*   **Workflows**: Appear as slash commands (e.g., `/default-triage`). Use these to trigger complex runbooks.
*   **Skills**: Do **not** appear as slash commands. You must ask the agent to perform the action using natural language.

**Example Comparison:**
*   *Workflow*: You type `/triage-alert CASE_ID=123`.
*   *Skill*: You type "Please enrich IP 1.2.3.4" (instead of `/enrich-ioc`).

> **Note**: For deep architectural details and platform differences, see [architecture_design.md](architecture_design.md).

---

## 3. Persona Walkthrough: Tier 1 SOC Analyst
**Role**: First line of defense.
**Focus**: Speed, accuracy, triage, and noise reduction.
**Constrains**: Cannot perform proactive hunting or deep forensic containment without escalation.

### 3.1 Start of Shift: Activating Your Persona
You sit down at your terminal. The first step is to "put on your uniform" by identifying yourself to the AI.

**Claude Code:**
```bash
/activate-agent tier1-soc-analyst
```
**Gemini CLI:**
```text
(User): Activate the Tier 1 SOC Analyst persona.
(Agent): Activated. I have loaded the Tier 1 skill set.
```

---

### 3.2 Task 1: Triage a Phishing Alert
An alert pops up in the queue: `Suspicious Email Reported (Case ID: 49201)`.

**Step 1: Initiate Triage Workflow**
Trigger the standard runbook.

**Claude Code:**
```bash
/run-workflow default-triage CASE_ID=49201
```
**Gemini CLI:**
```text
/default-triage CASE_ID=49201
```

**AI Agent Action (Automated):**
1.  **Checks Permissions**: Verifies you are allowed to triage.
2.  **Context**: Pulls alert details from SOAR. Finds subject "Urgent Invoice" and sender `bad-actor@evil.com`.
3.  **Enrichment**:
    *   Checks `events` logs for `evil.com`.
    *   Queries GTI (Threat Intel) for domain reputation.
4.  **Correlation**: Checks if `bad-actor@evil.com` has targeted other users.

**AI Output:**
> *Triage Complete for Case 49201.*
> * **Classification**: Suspicious
> * **Findings**: Domain `evil.com` created 2 days ago. Hosted on known bad subnet. 3 other users received similar emails.
> * **Recommendation**: Escalate to Tier 2 for campaign analysis.

---

### 3.3 Task 2: Closing a False Positive
Next alert: `High CPU Usage - Server DB-01 (Case ID: 49205)`.

**Step 1: Rapid Investigation**
You ask the agent to check the specific entity.

**Claude Code:**
```bash
/enrich-ioc IOC_VALUE=DB-01 IOC_TYPE=hostname
```
**Gemini CLI:**
```text
Can you get the details for hostname DB-01?
```

**AI Output:**
> *Hostname: DB-01. Role: Database Server. Known scheduled backup window: 02:00 UTC (Current time .*

**Step 2: Close Case**
It's a backup job. You close it.

**Claude Code:**
```bash
/close-soar-artifact ARTIFACT_ID=49205 ...
```
**Gemini CLI:**
```text
Close case 49205 as a False Positive. Root cause is Scheduled Maintenance.
```

---

### 3.4 Task 3: Escalating a Confirmed Threat
Back to the phishing case (49201). The agent recommended escalation. You agree.

**Claude Code:**
```bash
/document-in-soar CASE_ID=49201 NOTE="Confirmed credential harvesting..."
```
**Gemini CLI:**
```text
Add a note to case 49201: "Confirmed credential harvesting campaign. Domain is fresh and widely targeted. Escalating to Tier 2."
```

**AI Output:**
> *Note added to Case 49201.*

---

## 4. Persona Walkthrough: Threat Hunter
**Role**: Proactive detective.
**Focus**: Finding threats that triggered no alerts.

### 4.1 Scenario: Hypothesis Hunting
You read a report about a new lateral movement technique using `psexec` with a specific flag.

**User Input:**
```bash
/activate-agent threat-hunter
```

**User Input:**
```bash
/hunt-lateral-movement TOOL_NAME=psexec TIME_RANGE=24h
```
*(Gemini User: "Hunt for lateral movement using tool psexec over the last 24h")*

**AI Agent Action:**
1.  **Generates Query**: Writes a complex YARA-L or SQL query to find `psexec` executions with the suspicious arguments.
2.  **Sweeps Environment**: Runs queries across all endpoints.
3.  **Filters**: Removes known admin activity (based on `admin_allowlist`).

**AI Output:**
> *Hunt Complete. Found 3 executions of 'psexec -s' from workstation 'WS-DEV-99' to 'DC-01'. User: 'jdoe'.*

**Claude Code:**
```bash
/deep-dive-ioc IOC_VALUE=WS-DEV-99
```
**Gemini CLI:**
```text
Perform a deep dive on workstation WS-DEV-99.
```

The Threat Hunter agent has permission to pull deep forensic artifacts (prefetch, shimcache) that the Tier 1 analyst could not access.

---

## 5. Command Reference

### Global Commands
| Command | Description |
| :--- | :--- |
| `/activate-agent <name>` | Switch persona (e.g., `tier1-soc-analyst`, `threat-hunter`). |
| `/run-workflow <name>` | Run a multi-step playbook (e.g., `default-triage`). |
| `/confirm-action` | Approve a pending critical action. |
| `/generate-report` | Summarize findings into a PDF/Markdown report. |

### Common Triage Skills
| Skill | Example Usage |
| :--- | :--- |
| `/enrich-ioc` | `IOC_VALUE=1.2.3.4 IOC_TYPE=ip` |
| `/check-duplicates` | `CASE_ID=12345` |
| `/triage-alert` | `ALERT_ID=abc-123` |

### Investigation Skills
| Skill | Example Usage |
| :--- | :--- |
| `/deep-dive-ioc` | `IOC_VALUE=malware.exe` |
| `/hunt-threat` | `THREAT_ACTOR="APT29"` |
| `/respond-phishing` | `MESSAGE_ID=...` |

## 6. Troubleshooting

*   **"Permission Denied"**: You are likely in a lower-tier persona (e.g., Tier 1) trying to run high-side commands (e.g., `hunt-apt`). Run `/activate-agent` to escalate (requires approval).
*   **"Workflow Failed"**: Check if one of the atomic skills in the workflow chain failed pre-flight checks.
