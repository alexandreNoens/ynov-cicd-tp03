import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class StudentCreate(BaseModel):
    firstName: str = Field(min_length=2)
    lastName: str = Field(min_length=2)
    email: str
    grade: float = Field(ge=0, le=20)
    field: Literal["informatique", "mathématiques", "physique", "chimie"]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            raise ValueError("Email invalide")
        return value


class Student(StudentCreate):
    id: int | None = None
