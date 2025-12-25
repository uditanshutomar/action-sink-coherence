"""SQLAlchemy models."""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class ActionAudit(Base):
    """Append-only audit log for dispatched actions."""
    __tablename__ = "action_audit"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(256), unique=True, nullable=False, index=True)
    tenant_id = Column(String(128), nullable=False, index=True)
    schema_version = Column(String(16), nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    payload_ref = Column(String(2048), nullable=False)
    decision = Column(String(16), nullable=False, index=True)
    coherence_score = Column(Float, nullable=False)
    reason_codes = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=False)
    axis_processing_ms = Column(Integer, nullable=False)
    action_taken = Column(String(32), nullable=False)
    processing_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
