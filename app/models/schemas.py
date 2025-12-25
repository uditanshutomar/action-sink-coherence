"""Pydantic models for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.config import settings


class Decision(str, Enum):
    AXIS = "axis"
    M = "m"
    BOTH = "both"
    DLQ = "dlq"


class ActionTaken(str, Enum):
    LOGGED = "logged"
    WEBHOOK_STUB = "webhook_stub"
    NOOP = "noop"


class AxisOutput(BaseModel):
    decision: Decision
    coherence_score: float = Field(..., ge=0.0, le=1.0)
    reason_codes: List[str] = Field(..., max_length=settings.MAX_REASON_CODES)
    explanation: str = Field(..., max_length=settings.MAX_EXPLANATION_LENGTH)
    processing_ms: int = Field(..., ge=0, le=300000)

    @field_validator("reason_codes")
    @classmethod
    def validate_reason_codes(cls, v: List[str]) -> List[str]:
        for code in v:
            if len(code) > settings.MAX_REASON_CODE_LENGTH:
                raise ValueError(f"reason_code exceeds max length of {settings.MAX_REASON_CODE_LENGTH}")
        return v


class DispatchRequest(BaseModel):
    tenant_id: str = Field(..., min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_]+$")
    message_id: str = Field(..., min_length=1, max_length=256)
    schema_version: str
    timestamp: datetime
    payload_ref: str = Field(..., min_length=1, max_length=2048)
    axis_output: AxisOutput

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        if v != settings.SCHEMA_VERSION:
            raise ValueError(f"Unsupported schema_version: {v}")
        return v


class DispatchResponse(BaseModel):
    message_id: str
    accepted: bool
    idempotent_replay: bool
    action_taken: ActionTaken
    processing_ms: int


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    service: str
    version: str
    schema_version: str
