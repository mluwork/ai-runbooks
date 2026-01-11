#!/usr/bin/env python3
"""
Security Model Verification Script

Validates consistency between:
- Persona YAML manifests (skills/_personas/*.yaml)
- Skill definitions (skills/*/SKILL.md)
- CLAUDE.md documentation

Usage:
    python scripts/verify_security_model.py
    python scripts/verify_security_model.py --verbose  # Show all checks
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    passed: bool
    category: str
    message: str
    severity: str  # "error", "warning", "info"


@dataclass
class SecurityModelVerifier:
    """Verifies security model consistency across personas, skills, and docs."""

    skills_dir: Path
    verbose: bool = False
    results: list[ValidationResult] = field(default_factory=list)
    personas: dict[str, Any] = field(default_factory=dict)
    skills: dict[str, Any] = field(default_factory=dict)

    # Privilege levels for escalation detection
    PRIVILEGE_LEVELS = {
        "tier1-analyst": 1,
        "tier2-analyst": 2,
        "threat-hunter": 2.5,
        "cti-researcher": 2.5,
        "detection-engineer": 2.5,
        "tier3-analyst": 3,
        "soc-manager": 3,
        "incident-responder": 4,
    }

    def verify_all(self) -> list[ValidationResult]:
        """Run all verification checks."""
        self._load_personas()
        self._load_skills()

        # Cross-reference checks
        self._check_persona_skill_references()
        self._check_skill_persona_references()
        self._check_privilege_level_consistency()
        self._check_workflow_skill_permissions()
        self._check_iam_requirements_consistency()
        self._check_pre_flight_checks()
        self._check_skill_completeness()

        return self.results

    def _load_personas(self) -> None:
        """Load all persona YAML files."""
        personas_dir = self.skills_dir / "_personas"
        if not personas_dir.exists():
            self.results.append(
                ValidationResult(
                    passed=False,
                    category="structure",
                    message=f"Personas directory not found: {personas_dir}",
                    severity="error",
                )
            )
            return

        for yaml_file in personas_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    persona = yaml.safe_load(f)
                    if persona and "name" in persona:
                        self.personas[persona["name"]] = persona
                        if self.verbose:
                            self.results.append(
                                ValidationResult(
                                    passed=True,
                                    category="load",
                                    message=f"Loaded persona: {persona['name']}",
                                    severity="info",
                                )
                            )
            except yaml.YAMLError as e:
                self.results.append(
                    ValidationResult(
                        passed=False,
                        category="parse",
                        message=f"Failed to parse {yaml_file.name}: {e}",
                        severity="error",
                    )
                )

    def _load_skills(self) -> None:
        """Load all skill SKILL.md files and extract metadata."""
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name.startswith("_"):
                continue  # Skip _personas, _workflows, _roles

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            try:
                content = skill_file.read_text()
                # Extract YAML frontmatter
                match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                if match:
                    frontmatter = yaml.safe_load(match.group(1))
                    if frontmatter:
                        skill_name = frontmatter.get("name", skill_dir.name)
                        self.skills[skill_name] = {
                            "frontmatter": frontmatter,
                            "content": content,
                            "path": skill_file,
                        }
                        if self.verbose:
                            self.results.append(
                                ValidationResult(
                                    passed=True,
                                    category="load",
                                    message=f"Loaded skill: {skill_name}",
                                    severity="info",
                                )
                            )
            except (OSError, yaml.YAMLError) as e:
                self.results.append(
                    ValidationResult(
                        passed=False,
                        category="parse",
                        message=f"Failed to parse {skill_file}: {e}",
                        severity="error",
                    )
                )

    def _check_persona_skill_references(self) -> None:
        """Verify all skills referenced in personas exist."""
        for persona_name, persona in self.personas.items():
            skills_config = persona.get("skills", {})
            all_skills = (
                skills_config.get("primary", [])
                + skills_config.get("allowed", [])
                + skills_config.get("forbidden", [])
            )
            for skill in all_skills:
                if skill not in self.skills:
                    self.results.append(
                        ValidationResult(
                            passed=False,
                            category="persona_skill_ref",
                            message=(
                                f"Persona '{persona_name}' references "
                                f"non-existent skill '{skill}'"
                            ),
                            severity="error",
                        )
                    )

    def _check_skill_persona_references(self) -> None:
        """Verify all personas referenced in skills exist."""
        for skill_name, skill in self.skills.items():
            personas_list = skill.get("frontmatter", {}).get("personas", [])
            if personas_list == ["all"] or personas_list == "all":
                continue
            for persona in personas_list:
                if persona not in self.personas and persona not in self.PRIVILEGE_LEVELS:
                    self.results.append(
                        ValidationResult(
                            passed=False,
                            category="skill_persona_ref",
                            message=(
                                f"Skill '{skill_name}' references "
                                f"non-existent persona '{persona}'"
                            ),
                            severity="warning",
                        )
                    )

    def _check_privilege_level_consistency(self) -> None:
        """Verify privilege levels are properly defined for all personas."""
        for persona_name in self.personas:
            if persona_name not in self.PRIVILEGE_LEVELS:
                self.results.append(
                    ValidationResult(
                        passed=False,
                        category="privilege_level",
                        message=(
                            f"Persona '{persona_name}' has no defined "
                            "privilege level in PRIVILEGE_LEVELS"
                        ),
                        severity="warning",
                    )
                )

    def _check_workflow_skill_permissions(self) -> None:
        """Verify workflows only use permitted skills."""
        for persona_name, persona in self.personas.items():
            skills_config = persona.get("skills", {})
            allowed_skills = set(
                skills_config.get("primary", []) + skills_config.get("allowed", [])
            )
            forbidden_skills = set(skills_config.get("forbidden", []))

            workflows = persona.get("workflows", {})
            for workflow_name, workflow in workflows.items():
                chain = workflow.get("chain", [])
                chain_skills = self._extract_skills_from_chain(chain)

                for skill in chain_skills:
                    if skill in forbidden_skills:
                        self.results.append(
                            ValidationResult(
                                passed=False,
                                category="workflow_permission",
                                message=(
                                    f"Workflow '{workflow_name}' in "
                                    f"'{persona_name}' uses forbidden "
                                    f"skill '{skill}'"
                                ),
                                severity="error",
                            )
                        )
                    elif skill not in allowed_skills and skill not in [
                        "STOP",
                        "escalate_to_tier2",
                        "recommend_escalation",
                        "document_findings",
                    ]:
                        self.results.append(
                            ValidationResult(
                                passed=False,
                                category="workflow_permission",
                                message=(
                                    f"Workflow '{workflow_name}' in "
                                    f"'{persona_name}' uses skill '{skill}' "
                                    "not in primary/allowed"
                                ),
                                severity="warning",
                            )
                        )

    def _extract_skills_from_chain(self, chain: list) -> set[str]:
        """Extract all skill names from a workflow chain."""
        skills = set()
        for step in chain:
            if isinstance(step, dict):
                if "skill" in step:
                    skills.add(step["skill"])
                elif "decision" in step:
                    branches = step["decision"].get("branches", {})
                    for branch_steps in branches.values():
                        if isinstance(branch_steps, list):
                            for branch_step in branch_steps:
                                if isinstance(branch_step, dict) and "skill" in branch_step:
                                    skills.add(branch_step["skill"])
                                elif isinstance(branch_step, str):
                                    skills.add(branch_step)
                elif "on_duplicate" in step:
                    for dup_step in step["on_duplicate"]:
                        if isinstance(dup_step, str):
                            skills.add(dup_step)
            elif isinstance(step, str):
                skills.add(step)
        return skills

    def _check_iam_requirements_consistency(self) -> None:
        """Verify IAM requirements align with skill needs."""
        # Check that personas with hunting skills have appropriate GTI license
        hunting_skills = {
            "hunt-apt",
            "hunt-threat",
            "pivot-on-ioc",
            "deep-dive-ioc",
        }

        for persona_name, persona in self.personas.items():
            skills_config = persona.get("skills", {})
            primary_skills = set(skills_config.get("primary", []))

            has_advanced_hunting = bool(primary_skills & hunting_skills)

            iam = persona.get("iam_requirements", {})
            gti_license = iam.get("gti", {}).get("license", "")

            if has_advanced_hunting and gti_license not in [
                "GTI Enterprise",
                "GTI Enterprise+",
            ]:
                self.results.append(
                    ValidationResult(
                        passed=False,
                        category="iam_consistency",
                        message=(
                            f"Persona '{persona_name}' has advanced hunting "
                            f"skills but GTI license is '{gti_license}' "
                            "(needs Enterprise or Enterprise+)"
                        ),
                        severity="warning",
                    )
                )

    def _check_pre_flight_checks(self) -> None:
        """Verify all atomic skills have Pre-Flight Check sections."""
        for skill_name, skill in self.skills.items():
            content = skill.get("content", "")
            if "## Pre-Flight Check" not in content:
                self.results.append(
                    ValidationResult(
                        passed=False,
                        category="pre_flight_check",
                        message=f"Skill '{skill_name}' missing Pre-Flight Check section",
                        severity="warning",
                    )
                )

    def _check_skill_completeness(self) -> None:
        """Check that all skills have required sections."""
        required_sections = ["## Inputs", "## Workflow", "## Required Outputs"]

        for skill_name, skill in self.skills.items():
            content = skill.get("content", "")
            for section in required_sections:
                if section not in content:
                    # Allow 'PICERL Phases' as alternative to 'Workflow'
                    if section == "## Workflow" and "## PICERL Phases" in content:
                        continue
                    self.results.append(
                        ValidationResult(
                            passed=False,
                            category="skill_completeness",
                            message=(
                                f"Skill '{skill_name}' missing "
                                f"required section: {section}"
                            ),
                            severity="warning",
                        )
                    )


def main() -> int:
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Determine skills directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    skills_dir = repo_root / "skills"

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return 1

    verifier = SecurityModelVerifier(skills_dir=skills_dir, verbose=verbose)
    results = verifier.verify_all()

    errors = [r for r in results if r.severity == "error"]
    warnings = [r for r in results if r.severity == "warning"]
    infos = [r for r in results if r.severity == "info"]

    print(f"\n{'=' * 60}")
    print("Security Model Verification Results")
    print(f"{'=' * 60}")
    print(f"Personas loaded: {len(verifier.personas)}")
    print(f"Skills loaded:   {len(verifier.skills)}")
    print(f"{'=' * 60}")
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    if verbose:
        print(f"Info:     {len(infos)}")
    print(f"{'=' * 60}\n")

    # Print errors first
    if errors:
        print("ERRORS:")
        for result in errors:
            print(f"  X [{result.category}] {result.message}")
        print()

    # Print warnings
    if warnings:
        print("WARNINGS:")
        for result in warnings:
            print(f"  ! [{result.category}] {result.message}")
        print()

    # Print info if verbose
    if verbose and infos:
        print("INFO:")
        for result in infos:
            print(f"  . [{result.category}] {result.message}")
        print()

    # Summary
    if len(errors) == 0 and len(warnings) == 0:
        print("All checks passed!")
        return 0
    elif len(errors) == 0:
        print(f"Verification completed with {len(warnings)} warnings.")
        return 0
    else:
        print(f"Verification FAILED with {len(errors)} errors.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
