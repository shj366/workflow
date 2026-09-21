from typing import Optional, Any
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from backend.common.schema import SchemaBase, as_query

@as_query
class ProcessTaskPageModel(SchemaBase):
    """任务查询参数"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    task_name: Optional[str] = Field(default=None, description="任务名称")
    display_name: Optional[str] = Field(default=None, description="显示名称")

class CompleteTaskRequest(SchemaBase):
    """完成任务请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    task_id: int = Field(description="任务ID")
    args: Optional[dict[str, Any]] = Field(default=None, description="参数")
    
class ProcessTaskModel(SchemaBase):
    """任务模型"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    
    id: int
    process_instance_id: int
    task_name: str
    display_name: Optional[str] = None
    task_type: Optional[int] = None
    perform_type: Optional[int] = None
    task_state: Optional[int] = None
    operator: Optional[str] = None
    finish_time: Any = None
    created_time: Any = None


class ProcessTaskDetailModel(ProcessTaskModel):
    """任务详情模型（含表单数据）"""
    ext: dict[str, Any] = Field(default_factory=dict, description="全量扩展数据")
    task_form_data: dict[str, Any] = Field(default_factory=dict, description="节点表单数据")
    task_form_key: Optional[str] = Field(default=None, description="节点表单Key")


class AddCandidateRequest(SchemaBase):
    """加签请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    
    process_task_id: int = Field(description="任务ID")
    actor_ids: list[str] = Field(description="参与人ID列表")


class JumpTaskRequest(SchemaBase):
    """跳转请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    
    process_task_id: int = Field(description="任务ID")
    target_node_id: str = Field(description="目标节点ID")


class SurrogateRequest(SchemaBase):
    """委托请求"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    
    process_task_id: int = Field(description="任务ID")
    user_id: str = Field(description="委托给谁")
