"""Unit tests for the gap analysis algorithm using injected test data."""
import pytest
from lib.services.plan_generator import _find_rule, generate


# ─── Fixtures ────────────────────────────────────────────────────────────────

CERTS = [
    {"cert_id": "aws-cp",  "name": "Cloud Practitioner", "level": "foundational", "level_order": 1, "typical_study_days": 3,  "difficulty_multiplier": 1.0, "retired": False},
    {"cert_id": "aws-saa", "name": "Solutions Architect Associate", "level": "associate",    "level_order": 2, "typical_study_days": 8,  "difficulty_multiplier": 1.5, "retired": False},
    {"cert_id": "aws-sap", "name": "Solutions Architect Professional", "level": "professional", "level_order": 3, "typical_study_days": 14, "difficulty_multiplier": 2.5, "retired": False},
    {"cert_id": "aws-das", "name": "Data Analytics (retired)", "level": "specialty",    "level_order": 4, "typical_study_days": 10, "difficulty_multiplier": 2.0, "retired": True},
]

RULES = [
    {"rule_id": "solution_architect#7#8", "role_id": "solution_architect", "grade_min": 7, "grade_max": 8, "required_cert_ids": ["aws-sap"]},
    {"rule_id": "solution_architect#4#6", "role_id": "solution_architect", "grade_min": 4, "grade_max": 6, "required_cert_ids": ["aws-saa"]},
    {"rule_id": "solution_architect#1#3", "role_id": "solution_architect", "grade_min": 1, "grade_max": 3, "required_cert_ids": ["aws-cp"]},
]


def make_member(**kwargs):
    defaults = {
        "person_id": "P001",
        "name": "Alice",
        "role_id": "solution_architect",
        "grade_level": 7,
        "active": True,
        "certifications_held": [],
        "days_remaining": 20,
    }
    defaults.update(kwargs)
    return defaults


# ─── _find_rule ───────────────────────────────────────────────────────────────

class TestFindRule:
    def test_exact_match(self):
        rule = _find_rule(RULES, grade_level=7)
        assert rule["rule_id"] == "solution_architect#7#8"

    def test_exact_match_lower_band(self):
        rule = _find_rule(RULES, grade_level=5)
        assert rule["rule_id"] == "solution_architect#4#6"

    def test_nearest_lower_when_no_exact(self):
        # Grade 10 — no band 9+, so nearest lower is 7-8
        rule = _find_rule(RULES, grade_level=10)
        assert rule["rule_id"] == "solution_architect#7#8"

    def test_no_rule_when_below_all_bands(self):
        rules_high = [{"rule_id": "x#7#8", "role_id": "x", "grade_min": 7, "grade_max": 8, "required_cert_ids": []}]
        rule = _find_rule(rules_high, grade_level=5)
        # Grade 5 is below grade_min=7, so no nearest lower exists
        assert rule is None

    def test_empty_rules_returns_none(self):
        assert _find_rule([], grade_level=7) is None


# ─── generate ─────────────────────────────────────────────────────────────────

class TestGenerate:
    def _run(self, members, certs=None, rules=None):
        return generate(
            members_override=members,
            certs_override=certs if certs is not None else CERTS,
            rules_override=rules if rules is not None else RULES,
        )

    def test_member_already_certified_requirement_met(self):
        members = [make_member(certifications_held=["aws-sap"])]
        plans, errors = self._run(members)
        assert len(plans) == 1
        assert plans[0].requirement_met is True
        assert plans[0].outstanding_certs == []
        assert plans[0].days_warning is False

    def test_member_with_gap_has_outstanding_cert(self):
        members = [make_member(certifications_held=[])]
        plans, errors = self._run(members)
        assert len(plans) == 1
        plan = plans[0]
        assert plan.requirement_met is False
        outstanding_ids = [c.cert_id for c in plan.outstanding_certs]
        assert "aws-sap" in outstanding_ids

    def test_days_warning_triggered(self):
        # aws-sap effective_study_days = 14 * 2.5 = 35; days_remaining = 10
        members = [make_member(certifications_held=[], days_remaining=10)]
        plans, _ = self._run(members)
        assert plans[0].days_warning is True

    def test_no_days_warning_when_sufficient_days(self):
        members = [make_member(certifications_held=[], days_remaining=100)]
        plans, _ = self._run(members)
        assert plans[0].days_warning is False

    def test_no_days_warning_when_no_days_remaining(self):
        members = [make_member(certifications_held=[], days_remaining=None)]
        plans, _ = self._run(members)
        assert plans[0].days_warning is False

    def test_retired_cert_excluded_from_outstanding(self):
        rules_with_retired = [
            {"rule_id": "x#1#3", "role_id": "solution_architect", "grade_min": 1, "grade_max": 12, "required_cert_ids": ["aws-das"]}
        ]
        members = [make_member(certifications_held=[])]
        plans, _ = self._run(members, rules=rules_with_retired)
        assert plans[0].outstanding_certs == []

    def test_outstanding_certs_ordered_by_level(self):
        rules = [{"rule_id": "x#7#8", "role_id": "solution_architect", "grade_min": 7, "grade_max": 8, "required_cert_ids": ["aws-sap", "aws-saa", "aws-cp"]}]
        members = [make_member(certifications_held=[])]
        plans, _ = self._run(members, rules=rules)
        orders = [c.level_order for c in plans[0].outstanding_certs]
        assert orders == sorted(orders)

    def test_member_missing_role_goes_to_errors(self):
        members = [make_member(role_id=None)]
        plans, errors = self._run(members)
        assert len(errors) == 1
        assert errors[0]["person_id"] == "P001"

    def test_member_missing_grade_goes_to_errors(self):
        members = [make_member(grade_level=None)]
        plans, errors = self._run(members)
        assert len(errors) == 1

    def test_no_matching_rule_sets_no_requirement(self):
        members = [make_member(role_id="unknown_role")]
        plans, errors = self._run(members)
        assert len(plans) == 1
        assert plans[0].no_requirement is True
        assert errors == []

    def test_inactive_members_excluded(self):
        members = [make_member(active=False), make_member(person_id="P002", active=True)]
        plans, _ = self._run(members)
        assert len(plans) == 1
        assert plans[0].person_id == "P002"

    def test_nearest_lower_grade_matching(self):
        # Grade 10, highest band is 7-8 → should use that rule
        members = [make_member(grade_level=10, certifications_held=[])]
        plans, _ = self._run(members)
        outstanding_ids = {c.cert_id for c in plans[0].outstanding_certs}
        assert "aws-sap" in outstanding_ids

    def test_certs_held_as_pipe_string(self):
        # certifications_held stored as pipe-separated string
        members = [make_member(certifications_held="aws-sap|aws-saa")]
        plans, _ = self._run(members)
        assert plans[0].requirement_met is True

    def test_multiple_members(self):
        members = [
            make_member(person_id="P001", certifications_held=["aws-sap"]),
            make_member(person_id="P002", certifications_held=[]),
        ]
        plans, _ = self._run(members)
        assert len(plans) == 2
        met = {p.person_id: p.requirement_met for p in plans}
        assert met["P001"] is True
        assert met["P002"] is False
