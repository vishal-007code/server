from beanie import Document
from pydantic import Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date, time
from pymongo import IndexModel


class Attendance(Document):
    employeeId: str = Field(..., min_length=1)
    date: datetime
    status: Literal["Present", "Absent"] = "Present"
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("employeeId")
    @classmethod
    def validate_employee_id(cls, v):
        return v.strip().upper()

    @field_validator("date", mode="before")
    @classmethod
    def normalize_date(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime.combine(v, time.min)
        return v

    class Settings:
        name = "attendances"
        indexes = [
            IndexModel([("employeeId", 1), ("date", 1)], unique=True),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "employeeId": "EMP001",
                "date": "2024-01-01",
                "status": "Present"
            }
        }
