from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class TeamMember(BaseModel):
    person_id: str
    name: str
    email: str
    grade_level: int
    role_id: str
    start_date: str
    grade_start_date: str
    manager_email: str
    location: str
    active: bool
    days_allocated_override: int
    days_remaining: int
    certifications_held: list[str] = []
    updated_at: Optional[str] = None

    @field_validator("grade_level")
    @classmethod
    def grade_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("grade_level must be a positive integer")
        return v

    @field_validator("days_remaining")
    @classmethod
    def days_remaining_non_negative(cls, v):
        if v < 0:
            raise ValueError("days_remaining must be >= 0")
        return v

    def to_dynamo(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dynamo(cls, item: dict) -> "TeamMember":
        return cls(**item)
