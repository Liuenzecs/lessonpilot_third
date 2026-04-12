from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.auth import UserRead


class AccountRead(UserRead):
    pass


class AccountUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_any_field_present(self) -> "AccountUpdatePayload":
        if self.name is None and self.email is None:
            raise ValueError("At least one field must be provided")
        return self


class AccountChangePasswordPayload(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_confirm_password(self) -> "AccountChangePasswordPayload":
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class AccountDeletePayload(BaseModel):
    confirm_text: str = Field(max_length=64)

    @model_validator(mode="after")
    def validate_confirmation(self) -> "AccountDeletePayload":
        if self.confirm_text.strip().upper() != "DELETE":
            raise ValueError('confirm_text must equal "DELETE"')
        return self


class FeedbackCreatePayload(BaseModel):
    mood: Literal["happy", "neutral", "sad"]
    message: str = Field(min_length=1, max_length=2000)
    page_path: str | None = Field(default=None, max_length=500)


class FeedbackRead(BaseModel):
    id: str
    user_id: str
    mood: Literal["happy", "neutral", "sad"]
    message: str
    page_path: str | None = None
    created_at: datetime
