from typing import Optional, Any

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from backend.common.schema import SchemaBase, as_query


class StartProcessRequest(SchemaBase):
    """启动流程请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    process_define_id: int = Field(description="流程定义ID")
    business_no: Optional[str] = Field(default=None, description="业务编号")
    args: Optional[dict[str, Any]] = Field(default=None, description="启动参数")


class StartAndExecuteRequest(SchemaBase):
    """启动流程并执行请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    process_define_id: int = Field(description="流程定义ID")
    form_data: Optional[dict[str, Any]] = Field(default=None, description="表单数据")

@as_query
class ProcessInstancePageModel(SchemaBase):
    """流程实例查询参数"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    display_name: Optional[str] = Field(default=None, description="流程名称")
    business_no: Optional[str] = Field(default=None, description="业务编号")
    state: Optional[int] = Field(default=None, description="状态")

class ProcessInstanceModel(SchemaBase):
    """流程实例模型"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int
    process_define_id: int
    state: Optional[int] = None
    business_no: Optional[str] = None
    operator: Optional[str] = None
    created_time: Any = Field(default=None)
