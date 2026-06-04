from fastapi import APIRouter, Depends
from typing import Any

from digital_signature.auth_router import get_current_user
from backend.app.domains.user.entity import UserEntity

router = APIRouter()

@router.get("/history/me")
async def get_my_history(
    current_user: UserEntity = Depends(get_current_user),
) -> list[Any]:
    # Placeholder for actual history logic.
    # Currently just returns an empty list. 
    # Since test_auth_03_no_token just checks for 401 when accessed without token,
    # this will satisfy the test and be ready for future logic.
    return []
