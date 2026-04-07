from typing import Any
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import paging_data
from backend.plugin.wf.model.process_cc_instance import ProcessCCInstance
from backend.plugin.wf.model.process_instance import ProcessInstance
from backend.plugin.wf.schema.process_cc_instance import ProcessCCInstancePageModel


def to_camel(snake_str: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class ProcessCCInstanceService:
    """抄送实例服务"""
    
    @classmethod
    async def get_cc_list(
        cls,
        db: AsyncSession,
        query_object: ProcessCCInstancePageModel,
        user_id: int,
    ) -> dict[str, Any]:
        """查询抄送给我的流程

        对齐待办/已办：联表流程实例，并解析实例 variable 为 instanceExt，补充：
        - processInstanceId：流程实例 ID
        - instanceCreateTime：实例创建时间
        - instanceExt：实例扩展信息（autoGenTitle、f_title、u_realName 等）
        """
        import json

        filters = [
            ProcessCCInstance.actor_id == str(user_id),
        ]

        if query_object.state is not None:
            filters.append(ProcessCCInstance.state == query_object.state)

        # 联表查询，获取流程实例信息
        stmt = (
            select(
                ProcessCCInstance.id,
                ProcessCCInstance.process_instance_id.label("processInstanceId"),
                ProcessCCInstance.actor_id,
                ProcessCCInstance.state,
                ProcessCCInstance.created_time,
                ProcessInstance.business_no,
                ProcessInstance.operator,
                ProcessInstance.state.label("process_state"),
                ProcessInstance.created_time.label("instanceCreateTime"),
                ProcessInstance.variable.label("instanceVariable"),
            )
            .join(ProcessInstance, ProcessCCInstance.process_instance_id == ProcessInstance.id)
            .where(*filters)
            .order_by(desc(ProcessCCInstance.created_time))
        )

        # 将 Row 转换为 dict 的 transformer，并解析 instanceVariable
        def rows_to_dicts(items):
            result: list[dict[str, Any]] = []
            for row in items:
                raw_data = dict(row._mapping)
                # 转换为驼峰格式
                data = {to_camel(k): v for k, v in raw_data.items()}

                instance_ext: dict[str, Any] = {}
                instance_variable = raw_data.get("instanceVariable")
                if instance_variable:
                    try:
                        instance_ext = json.loads(instance_variable)
                    except Exception:
                        instance_ext = {}
                # 移除 instanceVariable 原始字段
                data.pop("instanceVariable", None)
                data["instanceExt"] = instance_ext
                result.append(data)
            return result

        return await paging_data(db, stmt, transformer=rows_to_dicts)

    @classmethod
    async def mark_as_read(cls, db: AsyncSession, cc_id: int, user_id: int) -> bool:
        """标记抄送为已读"""
        stmt = select(ProcessCCInstance).where(
            ProcessCCInstance.id == cc_id,
            ProcessCCInstance.actor_id == str(user_id),
        )
        result = await db.execute(stmt)
        cc_instance = result.scalars().first()
        
        if cc_instance:
            cc_instance.state = 1  # 已读
            await db.flush()
            return True
        return False

    @classmethod
    async def create_cc(cls, db: AsyncSession, process_instance_id: int, actor_ids: list[str], user_id: int) -> int:
        """创建抄送记录
        
        Args:
            process_instance_id: 流程实例ID
            actor_ids: 被抄送人ID列表
            user_id: 操作人ID
            
        Returns:
            创建的抄送记录数量
        """
        count = 0
        for actor_id in actor_ids:
            cc = ProcessCCInstance(
                process_instance_id=process_instance_id,
                actor_id=actor_id,
                state=0,  # 未读
                created_by=user_id,
            )
            db.add(cc)
            count += 1
        await db.flush()
        return count
