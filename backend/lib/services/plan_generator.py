"""
Gap analysis algorithm: matches each active member to their applicable
requirement rule, computes outstanding certifications, and flags days warnings.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from lib.models.training_plan import OutstandingCert, TrainingPlan
from lib.utils.dynamodb import scan_all

TEAM_MEMBERS_TABLE = os.environ.get("TEAM_MEMBERS_TABLE", "TeamMembers")
CERTIFICATIONS_TABLE = os.environ.get("CERTIFICATIONS_TABLE", "Certifications")
REQUIREMENT_RULES_TABLE = os.environ.get("REQUIREMENT_RULES_TABLE", "RequirementRules")


def _find_rule(rules_for_role: list[dict], grade_level: int) -> dict | None:
    """Return the best-matching rule for grade_level.

    Exact match first; then nearest-lower (highest grade_max that is still
    <= grade_level); then None.
    """
    exact = [r for r in rules_for_role if r["grade_min"] <= grade_level <= r["grade_max"]]
    if exact:
        return exact[0]

    lower = [r for r in rules_for_role if r["grade_max"] < grade_level]
    if lower:
        return max(lower, key=lambda r: r["grade_max"])

    return None


def generate(
    *,
    members_override: list[dict] | None = None,
    certs_override: list[dict] | None = None,
    rules_override: list[dict] | None = None,
) -> tuple[list[TrainingPlan], list[dict]]:
    """Run the gap analysis and return (plans, generation_errors).

    Override parameters allow unit tests to inject data without DynamoDB.
    """
    members = members_override if members_override is not None else scan_all(TEAM_MEMBERS_TABLE)
    cert_items = certs_override if certs_override is not None else scan_all(CERTIFICATIONS_TABLE)
    rule_items = rules_override if rules_override is not None else scan_all(REQUIREMENT_RULES_TABLE)

    # Index certs by cert_id; exclude retired from outstanding calculations
    cert_map: dict[str, dict] = {c["cert_id"]: c for c in cert_items}
    active_cert_ids: set[str] = {c["cert_id"] for c in cert_items if not c.get("retired")}

    # Group rules by role_id
    rules_by_role: dict[str, list[dict]] = {}
    for rule in rule_items:
        rules_by_role.setdefault(rule["role_id"], []).append(rule)

    now = datetime.now(timezone.utc).isoformat()
    plans: list[TrainingPlan] = []
    generation_errors: list[dict] = []

    active_members = [m for m in members if m.get("active", True)]

    for member in active_members:
        person_id = member.get("person_id", "")
        role_id = member.get("role_id")
        grade_level = member.get("grade_level")

        if not role_id or grade_level is None:
            generation_errors.append({
                "person_id": person_id,
                "reason": "Missing role_id or grade_level — skipped",
            })
            continue

        grade_level = int(grade_level)
        role_rules = rules_by_role.get(role_id, [])
        matched_rule = _find_rule(role_rules, grade_level)

        if matched_rule is None:
            plans.append(TrainingPlan(
                person_id=person_id,
                name=member.get("name", ""),
                role_id=role_id,
                grade_level=grade_level,
                required_cert_ids=[],
                certs_held=_parse_certs_held(member),
                outstanding_certs=[],
                total_study_days_required=0,
                days_remaining=_days_remaining(member),
                days_warning=False,
                requirement_met=False,
                no_requirement=True,
                generated_at=now,
            ))
            continue

        required_cert_ids: list[str] = matched_rule.get("required_cert_ids", [])
        certs_held: list[str] = _parse_certs_held(member)
        held_set = set(certs_held)

        outstanding: list[OutstandingCert] = []
        for cert_id in required_cert_ids:
            if cert_id in held_set:
                continue
            if cert_id not in active_cert_ids:
                # Retired or unknown cert — skip from outstanding
                continue
            cert = cert_map[cert_id]
            study_days = cert.get("effective_study_days") or (
                float(cert.get("typical_study_days", 0)) * float(cert.get("difficulty_multiplier", 1.0))
            )
            outstanding.append(OutstandingCert(
                cert_id=cert_id,
                name=cert.get("name", cert_id),
                level=cert.get("level", ""),
                level_order=int(cert.get("level_order", 0)),
                effective_study_days=study_days,
                superseded_by=cert.get("superseded_by_cert_id"),
            ))

        # Order by level_order ascending (foundational → associate → professional → specialty)
        outstanding.sort(key=lambda c: c.level_order)

        total_study_days = sum(c.effective_study_days for c in outstanding)
        days_remaining = _days_remaining(member)
        days_warning = (days_remaining is not None) and (total_study_days > days_remaining)

        plans.append(TrainingPlan(
            person_id=person_id,
            name=member.get("name", ""),
            role_id=role_id,
            grade_level=grade_level,
            required_cert_ids=required_cert_ids,
            certs_held=certs_held,
            outstanding_certs=outstanding,
            total_study_days_required=total_study_days,
            days_remaining=days_remaining,
            days_warning=days_warning,
            requirement_met=len(outstanding) == 0,
            no_requirement=False,
            generated_at=now,
        ))

    return plans, generation_errors


def _parse_certs_held(member: dict) -> list[str]:
    raw = member.get("certifications_held", [])
    if isinstance(raw, list):
        return [c.strip() for c in raw if c.strip()]
    if isinstance(raw, str):
        return [c.strip() for c in raw.split("|") if c.strip()]
    return []


def _days_remaining(member: dict) -> float | None:
    val = member.get("days_remaining")
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
