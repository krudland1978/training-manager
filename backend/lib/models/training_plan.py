from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class OutstandingCert(BaseModel):
    cert_id: str
    name: str
    level: str
    level_order: int
    effective_study_days: float
    superseded_by: Optional[str] = None


class TrainingPlan(BaseModel):
    person_id: str
    name: str = ""
    generated_at: str
    role_id: str
    grade_level: int
    required_cert_ids: list[str]
    certs_held: list[str]
    outstanding_certs: list[OutstandingCert]
    total_study_days_required: float
    days_remaining: Optional[float] = None
    days_warning: bool
    no_requirement: bool
    requirement_met: bool

    def to_dynamo(self) -> dict:
        data = self.model_dump()
        data["total_study_days_required"] = Decimal(str(self.total_study_days_required))
        if self.days_remaining is not None:
            data["days_remaining"] = Decimal(str(self.days_remaining))
        data["outstanding_certs"] = [
            {**c.model_dump(), "effective_study_days": Decimal(str(c.effective_study_days))}
            for c in self.outstanding_certs
        ]
        return data

    @classmethod
    def from_dynamo(cls, item: dict) -> "TrainingPlan":
        return cls(**item)
