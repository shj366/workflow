from fastapi import APIRouter, Request, Depends
from sqlalchemy import select

from backend.app.admin.model import User
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.wf.engine.core.flow_engine import FlowEngine
from backend.plugin.wf.schema.process_instance import StartProcessRequest, ProcessInstanceModel, ProcessInstancePageModel, StartAndExecuteRequest
from backend.plugin.wf.schema.process_cc_instance import ProcessCCInstancePageModel
from backend.plugin.wf.service.process_instance import ProcessInstanceService
from backend.plugin.wf.service.process_cc_instance import ProcessCCInstanceService

router = APIRouter()


@router.get("/users", summary="获取用户列表选项", dependencies=[DependsJwtAuth])
async def get_user_options(db: CurrentSession) -> ResponseSchemaModel[list]:
    """获取用户列表选项（用于选择下一节点处理人）"""
    stmt = select(User.id, User.username, User.nickname).where(User.status == 1)
    result = await db.execute(stmt)
    users = result.all()
    return response_base.success(data=[
        {"id": u.id, "username": u.username, "nickname": u.nickname} 
        for u in users
    ])


@router.get(
    "/my",
    summary="分页获取我发起的流程",
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_instances(
    request: Request,
    db: CurrentSession,
    query: ProcessInstancePageModel = Depends(ProcessInstancePageModel.as_query),
) -> ResponseSchemaModel[PageData[dict]]:
    """查询我发起的流程"""
    page_data = await ProcessInstanceService.get_my_instances(db, query, request.user.id)
    return response_base.success(data=page_data)


@router.post(
    "/start",
    summary="启动流程实例",
    dependencies=[DependsJwtAuth],
)
async def start_process(
    request: Request,
    db: CurrentSessionTransaction,
    data: StartProcessRequest,
) -> ResponseSchemaModel[ProcessInstanceModel]:
    """启动流程实例"""
    engine = FlowEngine(db)
    args = data.args or {}
    args["business_no"] = data.business_no
    args["user_id"] = request.user.id
    # 补充用户信息，供后续写入流程实例 variable
    # key 命名对齐前端/ext：u_realName 等
    if hasattr(request.user, "nickname"):
        args.setdefault("u_realName", request.user.nickname)
    if hasattr(request.user, "username"):
        args.setdefault("u_username", request.user.username)

    instance = await engine.start_process(
        process_define_id=data.process_define_id,
        operator=request.user.username if hasattr(request.user, 'username') else str(request.user.id),
        args=args
    )
    return response_base.success(data=instance)


@router.post(
    "/startAndExecute",
    summary="启动流程并执行第一个任务",
    dependencies=[DependsJwtAuth],
)
async def start_and_execute(
    request: Request,
    db: CurrentSessionTransaction,
    data: StartAndExecuteRequest,
) -> ResponseSchemaModel[ProcessInstanceModel]:
    """启动流程并执行第一个任务（发起申请）"""
    engine = FlowEngine(db)

    # 构建参数，将表单字段合并到 args
    args = {}
    if data.form_data:
        args.update(data.form_data)
    args["user_id"] = request.user.id
    # 补充用户信息，供后续写入流程实例 variable
    if hasattr(request.user, "nickname"):
        args.setdefault("u_realName", request.user.nickname)
    if hasattr(request.user, "username"):
        args.setdefault("u_username", request.user.username)

    operator = request.user.username if hasattr(request.user, 'username') else str(request.user.id)

    instance = await engine.start_and_execute(
        process_define_id=data.process_define_id,
        operator=operator,
        args=args
    )
    return response_base.success(data=instance)


@router.get(
    "/cc",
    summary="分页获取抄送给我的流程",
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_cc_list(
    request: Request,
    db: CurrentSession,
    query: ProcessCCInstancePageModel = Depends(ProcessCCInstancePageModel.as_query),
) -> ResponseSchemaModel[PageData[dict]]:
    """查询抄送给我的流程"""
    page_data = await ProcessCCInstanceService.get_cc_list(db, query, request.user.id)
    return response_base.success(data=page_data)


@router.post(
    "/cc/read/{cc_id}",
    summary="标记抄送为已读",
    dependencies=[DependsJwtAuth],
)
async def mark_cc_as_read(
    request: Request,
    db: CurrentSessionTransaction,
    cc_id: int,
) -> ResponseSchemaModel[bool]:
    """标记抄送为已读"""
    result = await ProcessCCInstanceService.mark_as_read(db, cc_id, request.user.id)
    return response_base.success(data=result)


@router.post(
    "/withdraw",
    summary="撤回流程实例",
    dependencies=[DependsJwtAuth],
)
async def withdraw_instance(
    request: Request,
    db: CurrentSessionTransaction,
    ids: list[int],
) -> ResponseSchemaModel[int]:
    """撤回流程实例（只能撤回自己发起的进行中流程）"""
    count = await ProcessInstanceService.withdraw(db, ids, request.user.id)
    return response_base.success(data=count)


@router.get(
    "/detail",
    summary="获取流程实例详情",
    dependencies=[DependsJwtAuth],
)
async def get_instance_detail(
    db: CurrentSession,
    id: int,
) -> ResponseSchemaModel[dict]:
    """获取流程实例详情，包含流程定义JSON和表单数据"""
    data = await ProcessInstanceService.get_detail(db, id)
    return response_base.success(data=data)


@router.get(
    "/approvalRecord",
    summary="获取审批记录",
    dependencies=[DependsJwtAuth],
)
async def get_instance_approval_record(
    db: CurrentSession,
    id: int,
) -> ResponseSchemaModel[list]:
    """获取流程实例的审批记录"""
    data = await ProcessInstanceService.get_approval_record(db, id)
    return response_base.success(data=data)


@router.get(
    "/highLight",
    summary="获取流程高亮数据",
    dependencies=[DependsJwtAuth],
)
async def get_instance_high_light(
    db: CurrentSession,
    id: int,
) -> ResponseSchemaModel[dict]:
    """获取流程实例的高亮数据（当前节点和已完成节点）"""
    data = await ProcessInstanceService.get_high_light(db, id)
    return response_base.success(data=data)
