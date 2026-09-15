from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.wf.api.v1.facade import router as facade_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)
v1.include_router(facade_router, prefix='/wf', tags=['jeeflow 工作流'])
