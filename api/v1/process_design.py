"""流程设计 API"""
import json
from fastapi import APIRouter, Depends, HTTPException, Request

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.wf.service.process_design import ProcessDesignService
from backend.plugin.wf.schema.process_design import (
    ProcessDesignPageModel,
    ProcessDesignCreateModel,
    ProcessDesignUpdateModel,
    SaveDesignRequest,
)

router = APIRouter()


@router.get(
    "/page",
    summary="分页获取流程设计列表",
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_page(
    db: CurrentSession,
    query: ProcessDesignPageModel = Depends(ProcessDesignPageModel.as_query),
) -> ResponseSchemaModel[PageData[dict]]:
    """分页查询流程设计"""
    page_data = await ProcessDesignService.get_page(db, query)
    return response_base.success(data=page_data)


@router.get(
    "/detail",
    summary="获取流程设计详情",
    dependencies=[DependsJwtAuth],
)
async def get_detail(
    db: CurrentSession,
    id: int,
) -> ResponseSchemaModel[dict]:
    """获取流程设计详情"""
    data = await ProcessDesignService.get_detail(db, id)
    return response_base.success(data=data)


@router.post(
    "/create",
    summary="创建流程设计",
    dependencies=[DependsJwtAuth],
)
async def create_design(
    request: Request,
    db: CurrentSessionTransaction,
    data: ProcessDesignCreateModel,
) -> ResponseSchemaModel[dict]:
    """创建流程设计"""
    design = await ProcessDesignService.create(db, data, request.user.id)
    return response_base.success(data={"id": design.id})


@router.post(
    "/update",
    summary="更新流程设计",
    dependencies=[DependsJwtAuth],
)
async def update_design(
    request: Request,
    db: CurrentSessionTransaction,
    data: ProcessDesignUpdateModel,
) -> ResponseSchemaModel[dict]:
    """更新流程设计"""
    await ProcessDesignService.update_design(db, data.id, data, request.user.id)
    return response_base.success(data={})


@router.post(
    "/saveDesign",
    summary="保存流程设计JSON",
    dependencies=[DependsJwtAuth],
)
async def save_design(
    request: Request,
    db: CurrentSessionTransaction,
    data: SaveDesignRequest,
) -> ResponseSchemaModel[dict]:
    """保存流程设计JSON"""
    await ProcessDesignService.save_design_json(db, data.id, data.json_object, request.user.id)
    return response_base.success(data={})


@router.post(
    "/delete",
    summary="删除流程设计",
    dependencies=[DependsJwtAuth],
)
async def delete_designs(
    db: CurrentSessionTransaction,
    ids: list[int],
) -> ResponseSchemaModel[dict]:
    """删除流程设计"""
    await ProcessDesignService.delete_designs(db, ids)
    return response_base.success(data={})


@router.post(
    "/deploy",
    summary="部署流程设计",
    dependencies=[DependsJwtAuth],
)
async def deploy_design(
    request: Request,
    db: CurrentSessionTransaction,
    id: int,
) -> ResponseSchemaModel[dict]:
    """部署流程设计"""
    try:
        define = await ProcessDesignService.deploy(db, id, request.user.id)
        return response_base.success(data={"id": define.id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/redeploy",
    summary="重新部署流程设计",
    dependencies=[DependsJwtAuth],
)
async def redeploy_design(
    request: Request,
    db: CurrentSessionTransaction,
    id: int,
) -> ResponseSchemaModel[dict]:
    """重新部署流程设计"""
    try:
        define = await ProcessDesignService.redeploy(db, id, request.user.id)
        return response_base.success(data={"id": define.id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/listByType",
    summary="按类型获取已部署的流程设计列表",
    dependencies=[DependsJwtAuth],
)
async def list_by_type(
    db: CurrentSession,
) -> ResponseSchemaModel[list]:
    """按类型获取已部署的流程设计列表，用于发起申请页面"""
    data = await ProcessDesignService.list_by_type(db)
    return response_base.success(data=data)


@router.get(
    "/userTree",
    summary="获取部门用户树",
    dependencies=[DependsJwtAuth],
)
async def get_user_tree(
    db: CurrentSession,
) -> ResponseSchemaModel[list]:
    """获取部门用户树，用于流程设计器选人"""
    data = await ProcessDesignService.get_user_tree(db)
    return response_base.success(data=data)
