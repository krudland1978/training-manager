import pytest
from pydantic import ValidationError

from lib.models.certification import CertLevel, Certification
from lib.models.requirement_rule import RequirementRule
from lib.models.team_member import TeamMember
from lib.models.training_plan import OutstandingCert, TrainingPlan


class TestCertLevel:
    def test_ordering(self):
        assert CertLevel.foundational < CertLevel.associate
        assert CertLevel.associate < CertLevel.professional
        assert CertLevel.professional < CertLevel.specialty

    def test_from_string(self):
        assert CertLevel["associate"] == CertLevel.associate


class TestCertification:
    def test_valid_cert(self):
        c = Certification(
            cert_id="aws-saa",
            name="AWS SAA",
            provider="aws",
            level="associate",
            level_order=2,
            domain="Architecture",
            typical_study_days=8,
            difficulty_multiplier=1.5,
        )
        assert c.effective_study_days == 12.0

    def test_effective_study_days_override(self):
        c = Certification(
            cert_id="aws-saa",
            name="AWS SAA",
            provider="aws",
            level="associate",
            level_order=2,
            domain="Architecture",
            typical_study_days=8,
            difficulty_multiplier=1.5,
            effective_study_days=10.0,
        )
        assert c.effective_study_days == 10.0

    def test_retired_default_false(self):
        c = Certification(
            cert_id="aws-saa",
            name="X",
            provider="aws",
            level="associate",
            level_order=2,
            domain="Architecture",
            typical_study_days=5,
            difficulty_multiplier=1.0,
        )
        assert c.retired is False


class TestTeamMember:
    def _base(self, **kwargs):
        defaults = {
            "person_id": "P001",
            "name": "Alice",
            "email": "alice@co.com",
            "grade_level": 7,
            "role_id": "solution_architect",
            "start_date": "2020-01-01",
            "grade_start_date": "2022-01-01",
            "location": "London",
            "active": True,
        }
        defaults.update(kwargs)
        return TeamMember(**defaults)

    def test_valid_member(self):
        m = self._base()
        assert m.person_id == "P001"
        assert m.active is True

    def test_certifications_held_defaults_empty(self):
        m = self._base()
        assert m.certifications_held == []

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            TeamMember(person_id="P001", name="Alice")


class TestRequirementRule:
    def test_make_rule_id(self):
        rule_id = RequirementRule.make_rule_id("solution_architect", 7, 8)
        assert rule_id == "solution_architect#7#8"

    def test_matches_exact(self):
        rule = RequirementRule(
            rule_id="solution_architect#7#8",
            role_id="solution_architect",
            grade_min=7,
            grade_max=8,
            required_cert_ids=["aws-sap"],
        )
        assert rule.matches(7) is True
        assert rule.matches(8) is True
        assert rule.matches(6) is False
        assert rule.matches(9) is False

    def test_invalid_grade_band_raises(self):
        with pytest.raises(ValidationError):
            RequirementRule(
                rule_id="x#8#7",
                role_id="x",
                grade_min=8,
                grade_max=7,
                required_cert_ids=[],
            )


class TestTrainingPlan:
    def test_round_trip(self):
        plan = TrainingPlan(
            person_id="P001",
            name="Alice",
            generated_at="2026-05-10T10:00:00Z",
            role_id="solution_architect",
            grade_level=7,
            required_cert_ids=["aws-sap"],
            certs_held=["aws-saa"],
            outstanding_certs=[
                OutstandingCert(
                    cert_id="aws-sap",
                    name="SAP",
                    level="professional",
                    level_order=3,
                    effective_study_days=39.0,
                )
            ],
            total_study_days_required=39.0,
            days_remaining=10.0,
            days_warning=True,
            requirement_met=False,
            no_requirement=False,
        )
        data = plan.to_dynamo()
        assert data["person_id"] == "P001"
        assert len(data["outstanding_certs"]) == 1
        assert data["outstanding_certs"][0]["cert_id"] == "aws-sap"
