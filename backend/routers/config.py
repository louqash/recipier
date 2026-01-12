"""
Configuration endpoints
"""

import os
from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel

from backend.config_loader import get_config

router = APIRouter()


class ConfigStatus(BaseModel):
    has_env_token: bool


class UsersResponse(BaseModel):
    diet_profiles: Dict[str, str]


@router.get("/status", response_model=ConfigStatus)
async def get_config_status():
    """
    Check if Todoist API token is configured via environment variable.
    If token is set via ENV, frontend should hide settings modal.

    NOTE: This endpoint only returns whether the token exists, NOT the token itself.
    The actual token is kept secure on the server side.
    """
    has_env_token = bool(os.getenv("TODOIST_API_TOKEN"))
    return ConfigStatus(has_env_token=has_env_token)


@router.get("/users", response_model=UsersResponse)
async def get_users():
    """
    Get diet profiles from config.
    Returns user keys and their diet profile mappings from the config file.
    Frontend can extract user list with Object.keys(diet_profiles).
    """
    # Get cached config
    config = get_config()
    return UsersResponse(diet_profiles=config.diet_profiles)
