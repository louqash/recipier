"""
Configuration endpoints
"""
import os
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()


class ConfigStatus(BaseModel):
    has_env_token: bool


class UsersResponse(BaseModel):
    users: List[str]
    diet_profiles: Dict[str, str] = {}


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


@router.get("/users", response_model=UsersResponse)
async def get_users():
    """
    Get list of available users from config's user_mapping and diet_profiles.
    Returns user keys and their diet profile mappings from the config file.
    """
    try:
        # Try to load config file
        config_path = os.path.join(os.getcwd(), "my_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                user_mapping = config_data.get('user_mapping', {})
                diet_profiles = config_data.get('diet_profiles', {})
                users = list(user_mapping.keys())
                return UsersResponse(users=users, diet_profiles=diet_profiles)
    except Exception as e:
        print(f"Warning: Could not load config: {e}")

    # Return empty list if config not found (frontend will show error)
    return UsersResponse(users=[], diet_profiles={})
