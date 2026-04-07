from datetime import datetime
from typing import Optional, Any

from pydantic import ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from backend.common.schema import SchemaBase, as_query


class ProcessDesignModel(SchemaBase):
    """流程设计模型"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )

    id: Optional[int] = Field(default=None, description="主键")
    name: Optional[str] = Field(default=None, description="唯一编码")
    display_name: Optional[str] = Field(default=None, description="显示名称")
    type: Optional[int] = Field(default=None, description="流程类型")
    icon: Optional[str] = Field(default=None, description="图标")
    is_deployed: Optional[int] = Field(default=0, description="是否已部署")
    json_object: Optional[dict[str, Any]] = Field(default=None, description="流程定义JSON")
    remark: Optional[str] = Field(default=None, description="备注")

    @field_validator('json_object', mode='before')
    @classmethod
    def ensure_dict(cls, value: Any):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                import json
                return json.loads(value)
            except json.JSONDecodeError:
                return {} # 或者 None，视需求而定，这里给个空对象防止报错
        return value
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_user: Optional[int] = Field(default=None, description="创建用户")
    update_user: Optional[int] = Field(default=None, description="更新用户")


class ProcessDesignCreateModel(SchemaBase):
    """创建流程设计模型"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )

    name: str = Field(description="唯一编码")
    display_name: Optional[str] = Field(default=None, description="显示名称")
    type: Optional[int] = Field(default=None, description="流程类型")
    icon: Optional[str] = Field(default=None, description="图标")
    remark: Optional[str] = Field(default=None, description="备注")


class ProcessDesignUpdateModel(SchemaBase):
    """更新流程设计模型"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )

    id: int = Field(description="主键")
    name: Optional[str] = Field(default=None, description="唯一编码")
    display_name: Optional[str] = Field(default=None, description="显示名称")
    type: Optional[int] = Field(default=None, description="流程类型")
    icon: Optional[str] = Field(default=None, description="图标")
    remark: Optional[str] = Field(default=None, description="备注")


class SaveDesignRequest(SchemaBase):
    """保存设计请求"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int = Field(description="主键")
    json_object: Optional[dict[str, Any]] = Field(default=None, description="流程设计JSON对象")

    @field_validator('json_object', mode='before')
    @classmethod
    def ensure_dict(cls, value: Any):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                import json

                return json.loads(value)
            except json.JSONDecodeError as exc:  # pragma: no cover - error message handled by pydantic
                raise ValueError(f'json_object 解析失败: {exc}') from exc
        if not isinstance(value, dict):
            raise ValueError(f'json_object 输入应为有效的字典, 实际类型: {type(value)}')
        return value


@as_query
class ProcessDesignPageModel(SchemaBase):
    """流程设计分页查询模型"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    name: Optional[str] = Field(default=None, description="唯一编码")
    display_name: Optional[str] = Field(default=None, description="显示名称")
    type: Optional[int] = Field(default=None, description="流程类型")
