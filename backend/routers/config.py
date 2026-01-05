"""
Configuration endpoints
"""
import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ConfigStatus(BaseModel):
    has_env_token: bool


@router.get("/status", response_model=ConfigStatus)
async def get_config_status():
    """
    Check if Todoist API token is configured via environment variable.
    If token is set via ENV, frontend should hide settings modal.

    NOTE: This endpoint only returns whether the token exists, NOT the token itself.
    The actual token is kept secure on the server side.
    """
    has_env_token = bool(os.getenv('TODOIST_API_TOKEN'))
    return ConfigStatus(has_env_token=has_env_token)
