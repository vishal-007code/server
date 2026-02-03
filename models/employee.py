from beanie import Document
from pydantic import Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from pymongo import IndexModel


class Employee(Document):
    employee_id: str = Field(..., alias="employeeId", min_length=1)
    full_name: str = Field(..., alias="fullName", min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="updatedAt")

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        return v.strip().upper()

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.strip().lower()

    @field_validator('department')
    @classmethod
    def validate_department(cls, v):
        return v.strip()

    class Settings:
        name = "employees"
        indexes = [
            IndexModel([("employeeId", 1)], unique=True),  # Use MongoDB field name (alias)
            IndexModel([("email", 1)], unique=True),
        ]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "employeeId": "EMP001",
                "fullName": "John Doe",
                "email": "john.doe@example.com",
                "department": "Engineering"
            }
        }
