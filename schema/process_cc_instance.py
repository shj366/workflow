from typing import Optional, Any

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from backend.common.schema import SchemaBase, as_query


@as_query
class ProcessCCInstancePageModel(SchemaBase):
    """抄送实例查询参数"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    state: Optional[int] = Field(default=None, description="状态(1:已读；0：未读)")


class ProcessCCInstanceModel(SchemaBase):
    """抄送实例模型"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int
    process_instance_id: int
    actor_id: str
    state: Optional[int] = None
    created_time: Any = Field(default=None)
    # 关联的流程实例信息
    business_no: Optional[str] = None
    operator: Optional[str] = None
    process_state: Optional[int] = None
