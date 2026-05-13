from decimal import Decimal
from pydantic import BaseModel, field_validator
from typing import Optional
from enum import IntEnum


class CertLevel(IntEnum):
    foundational = 1
    associate = 2
    professional = 3
    specialty = 4

    @classmethod
    def from_str(cls, value: str) -> "CertLevel":
        try:
            return cls[value.lower()]
        except KeyError:
            raise ValueError(f"Invalid certification level: {value}")


class Certification(BaseModel):
    cert_id: str
    exam_code: str
    name: str
    provider: str
    level: str
    level_order: int
    domain: str
    typical_study_days: int
    difficulty_multiplier: float
    validity_years: int
    retired: bool
    superseded_by_cert_id: Optional[str] = None
    updated_at: Optional[str] = None

    @field_validator("level")
    @classmethod
    def level_must_be_valid(cls, v):
        valid = {"foundational", "associate", "professional", "specialty"}
        if v.lower() not in valid:
            raise ValueError(f"level must be one of {valid}")
        return v.lower()

    @field_validator("typical_study_days")
    @classmethod
    def study_days_positive(cls, v):
        if v <= 0:
            raise ValueError("typical_study_days must be positive")
        return v

    @field_validator("difficulty_multiplier")
    @classmethod
    def multiplier_positive(cls, v):
        if v <= 0:
            raise ValueError("difficulty_multiplier must be > 0")
        return v

    @property
    def effective_study_days(self) -> float:
        return self.typical_study_days * self.difficulty_multiplier

    def to_dynamo(self) -> dict:
        data = self.model_dump()
        data["difficulty_multiplier"] = Decimal(str(self.difficulty_multiplier))
        data["effective_study_days"] = Decimal(str(self.effective_study_days))
        return data

    @classmethod
    def from_dynamo(cls, item: dict) -> "Certification":
        return cls(**item)
