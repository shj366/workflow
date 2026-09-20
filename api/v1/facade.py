"""HTTP facade compatible with jeeflow-ui."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request

from backend.common.context import ctx
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.rbac import DependsRBAC

from ...runtime import get_runtime



_FACADE_PERMISSIONS: dict[str, str] = {
    'processDefine/page': 'workflow:process-define:add',
    'processDefine/detail': 'workflow:process-define:add',
    'processDefine/startAndExecute': 'workflow:process:start',
    'processDefine/deploy': 'workflow:process-define:add',
    'processDefine/redeploy': 'workflow:process-define:edit',
    'processDefine/remove': 'workflow:process-define:del',
    'processDefine/upAndDown': 'workflow:process-define:edit',
    'processDefine/getLastByName': 'workflow:process-define:add',
    'processInstance/page': 'workflow:instance:my:view',
    'processInstance/detail': 'workflow:instance:my:view',
    'processInstance/startAndExecute': 'workflow:process:start',
    'processInstance/withdraw': 'workflow:instance:my:withdraw',
    'processInstance/ccList': 'workflow:instance:cc:view',
    'processInstance/createCCInstance': 'workflow:task:cc',
    'processInstance/updateCCStatus': 'workflow:instance:cc:read',
    'processInstance/highLight': 'workflow:instance:my:view',
    'processInstance/approvalRecord': 'workflow:instance:my:view',
    'processInstance/getAssigneeTextData': 'workflow:instance:my:view',
    'processInstance/bizData': 'workflow:instance:my:view',
    'processInstance/stats/overview': 'workflow:instance:my:view',
    'processInstance/stats/trend': 'workflow:instance:my:view',
    'processInstance/stats/group': 'workflow:instance:my:view',
    'processTask/todoList': 'workflow:task:todo:view',
    'processTask/doneList': 'workflow:task:done:view',
    'processTask/execute': 'workflow:task:complete',
    'processTask/detail': 'workflow:task:todo:view',
    'processTask/jumpAbleTaskNameList': 'workflow:task:jump',
    'processTask/candidatePage': 'workflow:task:add-candidate',
    'processTask/addCandidate': 'workflow:task:add-candidate',
    'processTask/surrogate': 'workflow:task:surrogate',
    'processTask/latest': 'workflow:task:todo:view',
    'processDesign/page': 'workflow:process-design:add',
    'processDesign/detail': 'workflow:process-design:add',
    'processDesign/save': 'workflow:process-design:add',
    'processDesign/update': 'workflow:process-design:edit',
    'processDesign/updateDefine': 'workflow:process-design:edit',
    'processDesign/remove': 'workflow:process-design:del',
    'processDesign/deploy': 'workflow:process-design:deploy',
    'processDesign/redeploy': 'workflow:process-design:deploy',
    'processDesign/listByType': 'workflow:apply:add',
    'processSurrogate/page': 'workflow:task:surrogate',
    'processSurrogate/save': 'workflow:task:surrogate',
    'processSurrogate/update': 'workflow:task:surrogate',
    'processSurrogate/detail': 'workflow:task:surrogate',
    'processSurrogate/remove': 'workflow:task:surrogate',
}


async def _set_facade_permission(action: str) -> None:
    permission = _FACADE_PERMISSIONS.get(action)
    if permission:
        ctx.permission = permission

router = APIRouter(dependencies=[Depends(_set_facade_permission), DependsRBAC])

@router.post('/{action:path}', summary='jeeflow 统一门面', dependencies=[DependsJwtAuth])
async def flow(action: str, request: Request, body: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
    """Forward one jeeflow action while deriving operator from the JWT subject."""
    args = dict(body or {})
    current_user = request.user
    args['operator'] = str(current_user.id)
    return await get_runtime().flow(action, args)
