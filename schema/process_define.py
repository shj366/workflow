from datetime import datetime
from typing import Optional, Any, List

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from backend.common.schema import SchemaBase, as_query


class ProcessDefineModel(SchemaBase):
    """流程定义模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: Optional[int] = Field(default=None, description="主键")
    name: Optional[str] = Field(default=None, description="唯一编码")
    display_name: Optional[str] = Field(default=None, description="显示名称")
    type: Optional[int] = Field(default=None, description="流程类型")
    state: Optional[int] = Field(default=None, description="流程状态")
    content: Optional[bytes] = Field(default=None, description="流程模型定义")
    version: Optional[int] = Field(default=None, description="流程版本")
    created_time: Optional[datetime] = Field(default=None, description="创建时间")
    updated_time: Optional[datetime] = Field(default=None, description="更新时间")
    created_by: Optional[int] = Field(default=None, description="创建用户")
    updated_by: Optional[int] = Field(default=None, description="更新用户")


class SaveDesignRequest(SchemaBase):
    """保存设计请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int = Field(description="主键")
    json_object: dict[str, Any] = Field(description="流程设计JSON对象")


class UpAndDownRequest(SchemaBase):
    """启用/禁用请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    ids: List[int] = Field(description="流程定义ID列表")
    op_type: int = Field(description="操作类型 1=启用 0=禁用")


@as_query
class ProcessDefinePageModel(SchemaBase):
    """流程定义分页查询模型"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    name: Optional[str] = Field(default=None, description="唯一编码")
    display_name: Optional[str] = Field(default=None, description="显示名称")
    type: Optional[int] = Field(default=None, description="流程类型")
    state: Optional[int] = Field(default=None, description="流程状态")
