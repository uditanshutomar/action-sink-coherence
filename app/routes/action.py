"""Action-Sink API routes."""

import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db, ActionAudit
from app.models import (
    DispatchRequest, DispatchResponse,
    HealthResponse, VersionResponse, ActionTaken,
)

router = APIRouter()


@router.post("/dispatch", response_model=DispatchResponse)
async def dispatch_action(
    request: DispatchRequest,
    db: AsyncSession = Depends(get_db),
) -> DispatchResponse:
    """Dispatch an action based on Axis output."""
    start_time = time.perf_counter()

    try:
        existing = await db.execute(
            select(ActionAudit).where(ActionAudit.message_id == request.message_id)
        )
        if existing.scalar_one_or_none():
            processing_ms = int((time.perf_counter() - start_time) * 1000)
            return DispatchResponse(
                message_id=request.message_id,
                accepted=True,
                idempotent_replay=True,
                action_taken=ActionTaken.NOOP,
                processing_ms=processing_ms,
            )

        action_taken = ActionTaken.LOGGED
        processing_ms = int((time.perf_counter() - start_time) * 1000)

        audit_record = ActionAudit(
            message_id=request.message_id,
            tenant_id=request.tenant_id,
            schema_version=request.schema_version,
            event_timestamp=request.timestamp,
            payload_ref=request.payload_ref,
            decision=request.axis_output.decision.value,
            coherence_score=request.axis_output.coherence_score,
            reason_codes=request.axis_output.reason_codes,
            explanation=request.axis_output.explanation,
            axis_processing_ms=request.axis_output.processing_ms,
            action_taken=action_taken.value,
            processing_ms=processing_ms,
        )
        db.add(audit_record)
        await db.flush()

        return DispatchResponse(
            message_id=request.message_id,
            accepted=True,
            idempotent_replay=False,
            action_taken=action_taken,
            processing_ms=processing_ms,
        )

    except IntegrityError:
        await db.rollback()
        processing_ms = int((time.perf_counter() - start_time) * 1000)
        return DispatchResponse(
            message_id=request.message_id,
            accepted=True,
            idempotent_replay=True,
            action_taken=ActionTaken.NOOP,
            processing_ms=processing_ms,
        )

    except OperationalError:
        # Fails closed per invariant
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "DEPENDENCY_UNAVAILABLE", "message": "Database unavailable"}},
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Health check endpoint."""
    try:
        await db.execute(select(1))
        return HealthResponse(status="ok")
    except OperationalError:
         raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "degraded"},
        )


@router.get("/version", response_model=VersionResponse)
async def get_version() -> VersionResponse:
    """Get service version information."""
    return VersionResponse(
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        schema_version=settings.SCHEMA_VERSION,
    )
