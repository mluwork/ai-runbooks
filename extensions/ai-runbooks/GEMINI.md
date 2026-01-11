# AI Runbooks Extension

This extension provides a comprehensive set of Security Operations Agent Skills for triage, investigation, threat hunting, and incident response. It is designed to be platform-agnostic, supporting standard security workflows.

## Skills

### Triage
- **/triage-alert** — Triage a security alert or case (Tier 1).
- **/triage-suspicious-login** — Investigate suspicious authentication.
- **/triage-malware** — Analyze suspected malicious files.

### Investigation
- **/deep-dive-ioc** — Exhaustive analysis of critical IOCs (Tier 2+).
- **/correlate-ioc** — Find related alerts and cases.
- **/pivot-on-ioc** — Explore GTI relationships.
- **/enrich-ioc** — Basic threat intelligence enrichment.
- **/find-relevant-case** — Search for related SOAR cases.

### Threat Hunting
- **/hunt-threat** — Hypothesis-driven threat hunting.
- **/hunt-apt** — Hunt for specific threat actors.
- **/hunt-ioc** — Sweep environment for specific indicators.
- **/hunt-lateral-movement** — Detect lateral movement techniques.
- **/hunt-credential-access** — Detect credential theft techniques.

### Incident Response
- **/respond-ransomware** — Ransomware PICERL workflow.
- **/respond-malware** — Malware containment and eradication.
- **/respond-phishing** — Phishing response workflow.
- **/respond-compromised-account** — Account compromise response.

### Operations & Utility
- **/activate-persona** — Set active role and permissions.
- **/run-workflow** — Execute deterministic workflow chains.
- **/check-duplicates** — Identify duplicate cases.
- **/document-in-soar** — Add findings to cases.
- **/close-soar-artifact** — Close cases/alerts.
- **/generate-report** — Create markdown reports.
- **/confirm-action** — Human-in-the-loop confirmation.

## Setup

1.  **Activate a Persona**:
    Start by setting your operational role to load appropriate permissions and workflows.
    ```bash
    /activate-persona tier1-analyst
    ```

2.  **Run a Skill**:
    Execute skills directly or via workflows.
    ```bash
    /triage-alert CASE_ID=12345
    ```

## Permissions

Skills enforce a security model based on the active persona.
- **Tier 1**: Triage, Enrichment, Case Mgmt.
- **Tier 2**: Deep Investigation, Pivoting.
- **Threat Hunter**: Proactive Hunting.
- **Incident Responder**: Containment & Eradication.

See `skills/activate-persona/SKILL.md` for details.
