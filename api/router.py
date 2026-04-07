from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.wf.api.v1.process_define import router as process_define_router
from backend.plugin.wf.api.v1.process_design import router as process_design_router
from backend.plugin.wf.api.v1.process_instance import router as process_instance_router
from backend.plugin.wf.api.v1.process_task import router as process_task_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(process_define_router, prefix="/wf/processDefine", tags=["流程定义"])
v1.include_router(process_design_router, prefix="/wf/processDesign", tags=["流程设计"])
v1.include_router(process_instance_router, prefix="/wf/processInstance", tags=["流程实例"])
v1.include_router(process_task_router, prefix="/wf/processTask", tags=["流程任务"])
