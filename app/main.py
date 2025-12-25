"""Action-Sink FastAPI Application."""

from fastapi import FastAPI

from app.routes import action
from app.config import settings


app = FastAPI(
    title="Action-Sink",
    description="Downstream agent for Axis output processing",
    version=settings.VERSION,
)

app.include_router(action.router, prefix="/v1/action", tags=["action"])
