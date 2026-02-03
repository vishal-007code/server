from beanie import Document
from pydantic import Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class User(Document):
    email: EmailStr
    password: str  # Will be hashed
    full_name: str = Field(..., alias="fullName", min_length=1)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="updatedAt")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.strip().lower()

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        return v.strip()

    class Settings:
        name = "users"
        indexes = [
            "email",
        ]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "fullName": "John Doe"
            }
        }
