from fastapi import APIRouter, Depends, UploadFile, File, Request

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession
from backend.plugin.wf.schema.process_define import ProcessDefinePageModel, ProcessDefineModel, SaveDesignRequest, UpAndDownRequest
from backend.plugin.wf.service.process_define import ProcessDefineService

router = APIRouter()


@router.get(
    "/detail",
    summary="获取流程定义详情",
    dependencies=[DependsJwtAuth],
)
async def get_process_define_detail(
    db: CurrentSession,
    id: int,
) -> ResponseSchemaModel[dict]:
    """获取流程定义详情"""
    data = await ProcessDefineService.get_detail(db, id)
    return response_base.success(data=data)


@router.post(
    "/saveDesign",
    summary="保存流程设计",
    dependencies=[DependsJwtAuth],
)
async def save_process_design(
    request: Request,
    db: CurrentSession,
    data: SaveDesignRequest,
) -> ResponseSchemaModel[ProcessDefineModel]:
    """保存流程设计"""
    define = await ProcessDefineService.save_design(db, data.id, data.json_object, request.user.id)
    return response_base.success(data=define)


@router.post(
    "/upAndDown",
    summary="启用/禁用流程定义",
    dependencies=[DependsJwtAuth],
)
async def up_and_down(
    request: Request,
    db: CurrentSession,
    data: UpAndDownRequest,
) -> ResponseSchemaModel[int]:
    """启用/禁用流程定义"""
    count = await ProcessDefineService.up_and_down(db, data.ids, data.op_type, request.user.id)
    return response_base.success(data=count)


@router.get(
    "/page",
    summary="分页获取流程定义列表",
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_process_define_list(
    db: CurrentSession,
    query: ProcessDefinePageModel = Depends(ProcessDefinePageModel.as_query),
) -> ResponseSchemaModel[PageData[dict]]:
    """分页查询流程定义"""
    page_data = await ProcessDefineService.get_process_define_list(db, query)
    return response_base.success(data=page_data)


@router.post(
    "/deploy",
    summary="部署流程定义",
    dependencies=[DependsJwtAuth],
)
async def deploy_process_define(
    request: Request,
    db: CurrentSession,
    file: UploadFile = File(...),
) -> ResponseSchemaModel[ProcessDefineModel]:
    """部署流程定义 (上传 JSON 文件)"""
    content = await file.read()
    user_id = request.user.id
    new_define = await ProcessDefineService.deploy(db, content, user_id)
    return response_base.success(data=new_define)
