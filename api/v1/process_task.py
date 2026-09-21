from fastapi import APIRouter, Depends, Query, Request

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.wf.engine.core.flow_engine import FlowEngine
from backend.plugin.wf.schema.process_task import (
    ProcessTaskPageModel,
    CompleteTaskRequest,
    ProcessTaskModel,
    AddCandidateRequest,
    JumpTaskRequest,
    SurrogateRequest,
)
from backend.plugin.wf.service.process_task import ProcessTaskService

router = APIRouter()


@router.get(
    "/list",
    summary="获取流程实例的任务列表",
    dependencies=[DependsJwtAuth],
)
async def get_task_list(
    request: Request,
    db: CurrentSession,
    instance_id: int = Query(..., alias="instanceId"),
) -> ResponseSchemaModel[list[ProcessTaskModel]]:
    """获取流程实例的任务列表"""
    tasks = await ProcessTaskService.get_list_by_instance_id(db, instance_id)
    return response_base.success(data=tasks)


@router.get(
    "/todo",
    summary="分页获取待办任务",
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_todo_list(
    request: Request,
    db: CurrentSession,
    query: ProcessTaskPageModel = Depends(ProcessTaskPageModel.as_query),
) -> ResponseSchemaModel[PageData[dict]]:
    """查询我的待办任务"""
    username = request.user.username if hasattr(request.user, 'username') else str(request.user.id)
    page_data = await ProcessTaskService.get_todo_list(db, query, username)
    return response_base.success(data=page_data)


@router.get(
    "/done",
    summary="分页获取已办任务",
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_done_list(
    request: Request,
    db: CurrentSession,
    query: ProcessTaskPageModel = Depends(ProcessTaskPageModel.as_query),
) -> ResponseSchemaModel[PageData[dict]]:
    """查询我的已办任务"""
    username = request.user.username if hasattr(request.user, 'username') else str(request.user.id)
    page_data = await ProcessTaskService.get_done_list(db, query, username)
    return response_base.success(data=page_data)


@router.post(
    "/complete",
    summary="完成任务",
    dependencies=[DependsJwtAuth],
)
async def complete_task(
    request: Request,
    db: CurrentSessionTransaction,
    data: CompleteTaskRequest,
) -> ResponseSchemaModel[list]:
    """完成任务 - 根据 submitType 分流处理"""
    engine = FlowEngine(db)
    operator = request.user.username if hasattr(request.user, 'username') else str(request.user.id)
    user_id = request.user.id
    args = data.args or {}
    submit_type = args.get("submitType", "agree")
    
    # 根据提交类型分流
    if submit_type == "rollback":
        # 退回上一步
        tasks = await engine.execute_and_rollback(
            task_id=data.task_id,
            operator=operator,
            args=args,
            user_id=user_id
        )
    elif submit_type == "reject":
        # 拒绝（跳转到结束节点）
        tasks = await engine.execute_and_jump_to_end(
            task_id=data.task_id,
            operator=operator,
            args=args,
            user_id=user_id
        )
    elif submit_type == "rollbackToOperator":
        # 退回发起人
        tasks = await engine.execute_and_rollback_to_operator(
            task_id=data.task_id,
            operator=operator,
            args=args,
            user_id=user_id
        )
    else:
        # 同意或其他：正常流转
        tasks = await engine.complete_task(
            task_id=data.task_id,
            operator=operator,
            args=args,
            user_id=user_id
        )
    
    return response_base.success(data=tasks)


@router.get(
    "/detail",
    summary="获取任务详情",
    dependencies=[DependsJwtAuth],
)
async def get_task_detail(
    request: Request,
    db: CurrentSession,
    task_id: int = Query(..., alias="taskId"),
) -> ResponseSchemaModel[dict]:
    """获取任务详情（含节点表单数据）"""
    detail = await ProcessTaskService.get_detail(db, task_id)
    return response_base.success(data=detail)


@router.post(
    "/addCandidate",
    summary="加签",
    dependencies=[DependsJwtAuth],
)
async def add_candidate(
    request: Request,
    db: CurrentSessionTransaction,
    data: AddCandidateRequest,
) -> ResponseSchemaModel[bool]:
    """加签：为任务增加参与人"""
    result = await ProcessTaskService.add_candidate_actor(db, data.process_task_id, data.actor_ids, request.user.id)
    return response_base.success(data=result)


@router.get(
    "/jumpAbleTaskNameList",
    summary="获取可跳转节点列表",
    dependencies=[DependsJwtAuth],
)
async def get_jump_able_task_name_list(
    request: Request,
    db: CurrentSession,
    task_id: int = Query(..., alias="taskId"),
) -> ResponseSchemaModel[list]:
    """获取可跳转的节点列表"""
    nodes = await ProcessTaskService.get_jump_able_task_name_list(db, task_id)
    return response_base.success(data=nodes)


@router.post(
    "/jump",
    summary="跳转",
    dependencies=[DependsJwtAuth],
)
async def jump_task(
    request: Request,
    db: CurrentSessionTransaction,
    data: JumpTaskRequest,
) -> ResponseSchemaModel[bool]:
    """跳转到指定节点"""
    operator = request.user.username if hasattr(request.user, 'username') else str(request.user.id)
    result = await ProcessTaskService.jump(db, data.process_task_id, data.target_node_id, operator, request.user.id)
    return response_base.success(data=result)


@router.post(
    "/surrogate",
    summary="委托",
    dependencies=[DependsJwtAuth],
)
async def surrogate_task(
    request: Request,
    db: CurrentSessionTransaction,
    data: SurrogateRequest,
) -> ResponseSchemaModel[bool]:
    """委托：将任务委托给其他人处理"""
    result = await ProcessTaskService.surrogate(db, data.process_task_id, data.user_id)
    return response_base.success(data=result)
