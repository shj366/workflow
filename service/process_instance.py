from typing import Any
import json
import re
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import paging_data
from backend.plugin.wf.model.process_instance import ProcessInstance
from backend.plugin.wf.model.process_define import ProcessDefine
from backend.plugin.wf.schema.process_instance import ProcessInstancePageModel


def to_camel(snake_str: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class ProcessInstanceService:
    """流程实例服务"""
    
    @classmethod
    async def get_my_instances(
        cls,
        db: AsyncSession,
        query_object: ProcessInstancePageModel,
        user_id: int,
    ) -> dict[str, Any]:
        """查询我发起的流程"""
        filters = [
            ProcessInstance.created_by == user_id,
        ]
        
        if query_object.business_no:
             filters.append(ProcessInstance.business_no.like(f"%{query_object.business_no}%"))
        if query_object.state is not None:
             filters.append(ProcessInstance.state == query_object.state)
        if query_object.display_name:
             filters.append(ProcessDefine.display_name.like(f"%{query_object.display_name}%"))

        # 联表查询，获取流程定义信息
        stmt = (
            select(
                ProcessInstance.id,
                ProcessInstance.process_define_id,
                ProcessInstance.state,
                ProcessInstance.business_no,
                ProcessInstance.operator,
                ProcessInstance.created_time,
                ProcessInstance.variable,
                ProcessDefine.name.label("define_name"),
                ProcessDefine.display_name.label("display_name"),
                ProcessDefine.version,
            )
            .outerjoin(ProcessDefine, ProcessInstance.process_define_id == ProcessDefine.id)
            .where(*filters)
            .order_by(desc(ProcessInstance.created_time))
        )
        
        # 将 Row 转换为 dict 的 transformer，并解析 variable 生成 ext 和 formData
        def rows_to_dicts(items):
            result: list[dict[str, Any]] = []
            for row in items:
                raw_data = dict(row._mapping)
                # 转换为驼峰格式
                data = {to_camel(k): v for k, v in raw_data.items()}
                
                variable = raw_data.get("variable")
                if variable:
                    try:
                        ext = json.loads(variable)
                    except Exception:
                        ext = {}
                    data["ext"] = ext

                    # 只把以 f_ 开头的变量当做表单字段，同时生成去掉前缀的 key
                    form_data: dict[str, Any] = {}
                    for key, value in ext.items():
                        if isinstance(key, str) and key.startswith("f_"):
                            form_data[key] = value
                            form_data[key[2:]] = value
                    data["formData"] = form_data

                result.append(data)
            return result
        
        return await paging_data(db, stmt, transformer=rows_to_dicts)

    @classmethod
    async def create(cls, db: AsyncSession, instance: ProcessInstance) -> ProcessInstance:
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    @classmethod
    async def update(cls, db: AsyncSession, instance: ProcessInstance) -> ProcessInstance:
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    @classmethod
    async def get_detail(cls, db: AsyncSession, instance_id: int) -> dict | None:
        """获取流程实例详情，包含流程定义JSON"""
        from backend.plugin.wf.model.process_define import ProcessDefine
        import json
        
        # 查询实例和关联的流程定义
        stmt = (
            select(
                ProcessInstance,
                ProcessDefine.content,
                ProcessDefine.display_name,
                ProcessDefine.name.label("define_name"),
                ProcessDefine.version,
            )
            .outerjoin(ProcessDefine, ProcessInstance.process_define_id == ProcessDefine.id)
            .where(ProcessInstance.id == instance_id)
        )
        result = await db.execute(stmt)
        row = result.first()
        
        if not row:
            return None
            
        instance = row[0]
        content = row[1]
        
        # 解析流程定义JSON
        json_object = None
        if content:
            try:
                json_object = json.loads(content.decode() if isinstance(content, bytes) else content)
            except:
                pass
        
        # 解析表单数据
        form_data = None
        if instance.variable:
            try:
                form_data = json.loads(instance.variable)
            except:
                pass
        
        return {
            "id": instance.id,
            "processDefineId": instance.process_define_id,
            "state": instance.state,
            "businessNo": instance.business_no,
            "operator": instance.operator,
            "createdTime": instance.created_time,
            "displayName": row[2],
            "defineName": row[3],
            "version": row[4],
            "jsonObject": json_object,
            "formData": form_data,
        }

    @classmethod
    async def get_approval_record(cls, db: AsyncSession, instance_id: int) -> list:
        """获取审批记录（已完成的任务列表）"""
        from backend.plugin.wf.model.process_task import ProcessTask
        from backend.app.admin.model.user import User
        from sqlalchemy import text
        
        # 查询该实例的所有任务，关联用户信息
        # 使用 COLLATE utf8mb4_unicode_ci 解决字符集不一致问题
        stmt = (
            select(
                ProcessTask.id,
                ProcessTask.task_name,
                ProcessTask.display_name,
                ProcessTask.operator,
                ProcessTask.task_state,
                ProcessTask.created_time,
                ProcessTask.finish_time,
                ProcessTask.variable,
                User.nickname.label("operator_name"),
            )
            .outerjoin(
                User, 
                text("wf_process_task.operator = sys_user.username COLLATE utf8mb4_unicode_ci")
            )
            .where(ProcessTask.process_instance_id == instance_id)
            .order_by(ProcessTask.created_time)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        # 1. 收集需要查询的角色ID
        role_ids = set()
        for row in rows:
            op = row[3] # operator
            if op and op.startswith("ROLE:"):
                val = op.split(":", 1)[1]
                if val.isdigit():
                    role_ids.add(int(val))
        
        # 2. 批量查询角色名
        role_map = {}
        if role_ids:
            from backend.app.admin.model import Role
            q = select(Role).where(Role.id.in_(role_ids))
            rs = await db.execute(q)
            for role in rs.scalars().all():
                role_map[str(role.id)] = role.name
        
        records = []
        for row in rows:
            import json
            variable = {}
            if row[7]:  # variable
                try:
                    variable = json.loads(row[7])
                except:
                    pass
            
            operator = row[3]
            operator_name = row[8] or operator
            
            # 角色名处理
            if operator and operator.startswith("ROLE:"):
                val = operator.split(":", 1)[1]
                if val in role_map:
                    operator_name = f"角色:{role_map[val]}"
                else:
                    # 没查到ID或者本来就是中文，直接显示
                    operator_name = f"角色:{val}"
            
            records.append({
                "id": row[0],
                "taskName": row[1],
                "displayName": row[2],
                "operator": operator,
                "taskState": row[4],
                "createdTime": row[5],
                "finishTime": row[6],
                "operatorName": operator_name,
                "approvalComment": variable.get("approvalComment", ""),
                "submitType": variable.get("submitType", ""),
            })
        
        return records

    @classmethod
    async def get_high_light(cls, db: AsyncSession, instance_id: int) -> dict:
        """获取流程高亮数据（当前节点和已完成节点）"""
        from backend.plugin.wf.model.process_task import ProcessTask
        
        stmt = select(ProcessTask).where(ProcessTask.process_instance_id == instance_id)
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        active_nodes: list[str] = []  # 当前活动节点
        history_nodes: list[str] = []  # 历史节点
        
        for task in tasks:
            if task.task_state == 10:  # 进行中
                active_nodes.append(task.task_name)
            elif task.task_state == 20:  # 已完成
                history_nodes.append(task.task_name)
        
        # 为了兼容 mldong 的 SnakerFlowDesigner 用法，返回更丰富的结构：
        # - activeNodeNames/historyNodeNames/historyEdgeNames：供组件内部高亮使用
        # - 同时保留 activeNodes/historyNodes，供当前前端标签展示使用
        return {
            "activeNodes": active_nodes,
            "historyNodes": history_nodes,
            "activeNodeNames": active_nodes,
            "historyNodeNames": history_nodes,
            "historyEdgeNames": [],
        }

    @classmethod
    async def withdraw(cls, db: AsyncSession, instance_ids: list[int], user_id: int) -> int:
        """撤回流程实例（只能撤回自己发起的进行中流程）"""
        from sqlalchemy import update as sql_update
        from datetime import datetime
        from backend.plugin.wf.model.process_task import ProcessTask
        
        # 1. 更新流程实例状态
        result = await db.execute(
            sql_update(ProcessInstance)
            .where(
                ProcessInstance.id.in_(instance_ids),
                ProcessInstance.created_by == user_id,
                ProcessInstance.state == 10,  # 只能撤回进行中的
            )
            .values(state=30)  # 30 = 已撤回
        )
        
        # 2. 取消所有进行中的任务（将任务状态设为已完成，并记录撤回信息）
        import json
        await db.execute(
            sql_update(ProcessTask)
            .where(
                ProcessTask.process_instance_id.in_(instance_ids),
                ProcessTask.task_state == 10,  # 进行中的任务
            )
            .values(
                task_state=20,  # 标记为已完成
                finish_time=datetime.now(),
                variable=json.dumps({"submitType": "withdraw", "approvalComment": "流程已撤回"}, ensure_ascii=False),
            )
        )
        
        await db.flush()
        return result.rowcount
