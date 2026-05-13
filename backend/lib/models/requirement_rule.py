from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class RequirementRule(BaseModel):
    rule_id: str
    role_id: str
    grade_min: int
    grade_max: int
    required_cert_ids: list[str]
    notes: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def make_rule_id(cls, role_id: str, grade_min: int, grade_max: int) -> str:
        return f"{role_id}#{grade_min}#{grade_max}"

    @model_validator(mode="after")
    def grade_band_valid(self):
        if self.grade_min > self.grade_max:
            raise ValueError("grade_min must be <= grade_max")
        return self

    def matches(self, grade_level: int) -> bool:
        return self.grade_min <= grade_level <= self.grade_max

    def to_dynamo(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dynamo(cls, item: dict) -> "RequirementRule":
        return cls(**item)
