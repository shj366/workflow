"""HTTP facade compatible with jeeflow-ui."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Request

from backend.common.security.jwt import DependsJwtAuth

from ...runtime import get_runtime

router = APIRouter()


@router.post('/{action:path}', summary='jeeflow 统一门面', dependencies=[DependsJwtAuth])
async def flow(action: str, request: Request, body: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
    """Forward one jeeflow action while deriving operator from the JWT subject."""
    args = dict(body or {})
    current_user = request.user
    args['operator'] = str(current_user.id)
    return await get_runtime().flow(action, args)
