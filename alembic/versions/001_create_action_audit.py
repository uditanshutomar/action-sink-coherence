"""Create action_audit table

Revision ID: 001_create_action_audit
Revises: 
Create Date: 2024-12-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_create_action_audit"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "action_audit",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("message_id", sa.String(256), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(128), nullable=False, index=True),
        sa.Column("schema_version", sa.String(16), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload_ref", sa.String(2048), nullable=False),
        sa.Column("decision", sa.String(16), nullable=False, index=True),
        sa.Column("coherence_score", sa.Float, nullable=False),
        sa.Column("reason_codes", sa.JSON, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("axis_processing_ms", sa.Integer, nullable=False),
        sa.Column("action_taken", sa.String(32), nullable=False),
        sa.Column("processing_ms", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("action_audit")
