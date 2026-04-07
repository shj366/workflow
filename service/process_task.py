from datetime import datetime
from typing import List, Any
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import paging_data
from backend.plugin.wf.model.process_task import ProcessTask
from backend.plugin.wf.model.process_instance import ProcessInstance
from backend.plugin.wf.model.process_task_actor import ProcessTaskActor
from backend.plugin.wf.schema.process_task import ProcessTaskPageModel


class ProcessTaskService:
    """流程任务服务"""
    
    @classmethod
    async def create(cls, db: AsyncSession, task: ProcessTask) -> ProcessTask:
        """创建任务"""
        db.add(task)
        await db.flush()
        await db.refresh(task)
        
        # 同步添加参与者（为了兼容 mldong 逻辑，创建任务时默认将 operator 加入 actor 表）
        if task.operator:
            await cls.add_task_actor(db, task.id, [task.operator])
            
        return task

    @classmethod
    async def add_task_actor(cls, db: AsyncSession, task_id: int, actor_ids: list[str]):
        """添加任务参与者"""
        if not actor_ids:
            return
            
        for actor_id in actor_ids:
            actor = ProcessTaskActor(
                process_task_id=task_id,
                actor_id=actor_id
            )
            db.add(actor)
        await db.flush()

    @classmethod
    async def get_doing_task_list(cls, db: AsyncSession, process_instance_id: int) -> List[ProcessTask]:
        """获取流程实例的进行中任务列表"""
        stmt = (
            select(ProcessTask)
            .where(
                ProcessTask.process_instance_id == process_instance_id,
                ProcessTask.task_state == 10  # 进行中
            )
            .order_by(ProcessTask.created_time)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def complete(cls, db: AsyncSession, task_id: int, operator: str, args: dict = None, user_id: int = None) -> ProcessTask:
        import json
        from backend.plugin.wf.service.process_cc_instance import ProcessCCInstanceService
        
        stmt = select(ProcessTask).where(ProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise ValueError(f"任务[{task_id}]不存在")
            
        task.task_state = 20 # 已完成
        task.finish_time = datetime.now()
        task.operator = operator # 更新实际处理人
        
        # 保存审批意见等信息到variable字段
        if args:
            variable = {}
            if task.variable:
                try:
                    variable = json.loads(task.variable)
                except:
                    pass
            # 保存审批意见
            if args.get("approvalComment"):
                variable["approvalComment"] = args.get("approvalComment")
            # 保存提交类型
            if args.get("submitType"):
                variable["submitType"] = args.get("submitType")
            task.variable = json.dumps(variable, ensure_ascii=False)
            
            # 处理抄送
            cc_actors = args.get("ccActors")
            if cc_actors and len(cc_actors) > 0:
                await ProcessCCInstanceService.create_cc(
                    db, 
                    task.process_instance_id, 
                    cc_actors, 
                    user_id or task.created_by
                )
        
        db.add(task)
        await db.flush()
        await db.refresh(task)
        return task

    @classmethod
    async def get_list_by_instance_id(cls, db: AsyncSession, instance_id: int) -> List[ProcessTask]:
        stmt = (
            select(ProcessTask)
            .where(ProcessTask.process_instance_id == instance_id)
            .order_by(ProcessTask.created_time)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_todo_list(
        cls,
        db: AsyncSession,
        query_object: ProcessTaskPageModel,
        username: str,
    ) -> dict[str, Any]:
        """查询待办任务

        为了对齐 mldong，这里联表流程实例，补充实例扩展信息：
        - processInstanceId：流程实例 ID
        - instanceCreateTime：实例创建时间
        - instanceExt：从实例 variable 解析出的扩展字段（autoGenTitle、f_title、u_realName 等）
        """
        import json
        from backend.app.admin.service.user_service import UserService

        # 获取当前用户及其角色
        try:
            user = await UserService.get_userinfo(db=db, username=username)
            roles = await UserService.get_roles(db=db, pk=user.id)
            actor_ids = [username]
            if roles:
                # 同时支持角色名称和角色ID
                actor_ids.extend([f"ROLE:{role.name}" for role in roles])
                actor_ids.extend([f"ROLE:{role.id}" for role in roles])
        except Exception:
            # 如果查不到用户，则只查 username
            actor_ids = [username]

        filters = [
            ProcessTask.task_state == 10,  # 进行中
        ]

        if query_object.task_name:
            filters.append(ProcessTask.task_name.like(f"%{query_object.task_name}%"))
        if query_object.display_name:
            filters.append(ProcessTask.display_name.like(f"%{query_object.display_name}%"))

        # 显式选择字段并对部分字段使用 label，对齐前端预期的驼峰命名
        stmt = (
            select(
                ProcessTask.id,
                ProcessTask.process_instance_id.label("processInstanceId"),
                ProcessTask.task_name.label("taskName"),
                ProcessTask.display_name.label("displayName"),
                ProcessTask.task_state.label("taskState"),
                ProcessTask.operator,
                ProcessTask.created_time.label("createTime"),
                ProcessTask.finish_time.label("finishTime"),
                ProcessInstance.created_time.label("instanceCreateTime"),
                ProcessInstance.variable.label("instanceVariable"),
            )
            .join(ProcessInstance, ProcessTask.process_instance_id == ProcessInstance.id)
            .join(ProcessTaskActor, ProcessTask.id == ProcessTaskActor.process_task_id)
            .where(
                ProcessTaskActor.actor_id.in_(actor_ids),
                *filters
            )
            .distinct()
            .order_by(desc(ProcessTask.created_time))
        )

        # 手动处理结果，支持异步查询角色名
        data = await paging_data(db, stmt)
        
        items = data.get("items", [])
        if items:
            # 1. 收集需要查询的角色ID
            role_ids = set()
            # 先转为字典列表
            rows = [dict(row._mapping) for row in items]
            
            for row in rows:
                op = row.get("operator")
                if op and op.startswith("ROLE:"):
                    val = op.split(":", 1)[1]
                    if val.isdigit():
                        role_ids.add(int(val))
            
            # 2. 批量查询角色名
            role_map = {}
            if role_ids:
                from backend.app.admin.model import Role
                role_stmt = select(Role).where(Role.id.in_(role_ids))
                role_result = await db.execute(role_stmt)
                for role in role_result.scalars().all():
                    role_map[str(role.id)] = role.name

            # 3. 处理数据：JSON解析 + 角色名替换
            result_items = []
            for row in rows:
                # 解析实例扩展变量
                instance_ext: dict[str, Any] = {}
                instance_variable = row.pop("instanceVariable", None)
                if instance_variable:
                    try:
                        instance_ext = json.loads(instance_variable)
                    except Exception:
                        instance_ext = {}
                row["instanceExt"] = instance_ext
                
                # 替换 operator 显示
                op = row.get("operator")
                if op and op.startswith("ROLE:"):
                    val = op.split(":", 1)[1]
                    if val in role_map:
                        row["operator"] = f"角色:{role_map[val]}"
                    else:
                        # 没查到ID或者本来就是中文，直接显示
                        row["operator"] = f"角色:{val}"
                
                result_items.append(row)
            
            data["items"] = result_items

        return data

    @classmethod
    def _get_task_actors(cls, task_model, execution) -> list[str]:
        """
        根据Task模型的assignee、candidateUsers、candidateGroups属性以及运行时数据，确定参与者
        @param task_model Task模型
        @param execution 运行时数据
        """
        # 1. 优先检查运行时是否指定了下一节点处理人
        args = execution.args or {}
        next_node_operator = args.get("nextNodeOperator") or args.get("nextOperator")
        if next_node_operator:
            if isinstance(next_node_operator, list):
                return next_node_operator
            elif isinstance(next_node_operator, str):
                return next_node_operator.split(",")

        actor_id_list = []
        
        # 2. 检查 assignee
        assignee = task_model.assignee
        if assignee:
            assignee_list = assignee.split(",")
            for assign in assignee_list:
                # 支持从 args 中动态获取变量，例如 assignee="${initiator}"
                if assign.startswith("${") and assign.endswith("}"):
                    var_name = assign[2:-1]
                    if var_name in args:
                        val = args[var_name]
                        if isinstance(val, list):
                            actor_id_list.extend(val)
                        else:
                            actor_id_list.append(str(val))
                elif assign in args:
                    # 兼容旧逻辑：如果 assignee 是变量名
                    val = args[assign]
                    if isinstance(val, list):
                        actor_id_list.extend(val)
                    else:
                        actor_id_list.append(str(val))
                else:
                    actor_id_list.append(assign)
        
        # 3. 检查 candidateUsers (候选人)
        if hasattr(task_model, "candidateUsers") and task_model.candidateUsers:
            users = task_model.candidateUsers.split(",")
            for user in users:
                # 同样支持变量替换
                if user.startswith("${") and user.endswith("}"):
                    var_name = user[2:-1]
                    if var_name in args:
                        val = args[var_name]
                        if isinstance(val, list):
                            actor_id_list.extend(val)
                        else:
                            actor_id_list.append(str(val))
                else:
                    actor_id_list.append(user)

        # 4. 检查 candidateGroups (候选组/角色)
        if hasattr(task_model, "candidateGroups") and task_model.candidateGroups:
            groups = task_model.candidateGroups.split(",")
            for group in groups:
                # 同样支持变量替换
                role_name = group
                if group.startswith("${") and group.endswith("}"):
                    var_name = group[2:-1]
                    if var_name in args:
                        role_name = str(args[var_name])
                
                # 添加角色前缀
                if role_name:
                    actor_id_list.append(f"ROLE:{role_name}")

        # 5. 如果都没有，默认使用当前操作人（兜底）
        if not actor_id_list:
            actor_id_list.append(execution.operator)

        # 去重
        return list(set(actor_id_list))

    @classmethod
    async def get_done_list(
        cls,
        db: AsyncSession,
        query_object: ProcessTaskPageModel,
        username: str,
    ) -> dict[str, Any]:
        """查询已办任务

        对齐 mldong：同待办列表，联表流程实例并返回实例扩展信息。
        """
        import json

        filters = [
            ProcessTask.operator == username,  # 匹配处理人用户名
            ProcessTask.task_state == 20,  # 已完成
        ]

        if query_object.task_name:
            filters.append(ProcessTask.task_name.like(f"%{query_object.task_name}%"))
        if query_object.display_name:
            filters.append(ProcessTask.display_name.like(f"%{query_object.display_name}%"))

        stmt = (
            select(
                ProcessTask.id,
                ProcessTask.process_instance_id.label("processInstanceId"),
                ProcessTask.task_name.label("taskName"),
                ProcessTask.display_name.label("displayName"),
                ProcessTask.task_state.label("taskState"),
                ProcessTask.operator,
                ProcessTask.created_time.label("createTime"),
                ProcessTask.finish_time.label("finishTime"),
                ProcessInstance.created_time.label("instanceCreateTime"),
                ProcessInstance.variable.label("instanceVariable"),
            )
            .join(ProcessInstance, ProcessTask.process_instance_id == ProcessInstance.id)
            .where(*filters)
            .order_by(desc(ProcessTask.finish_time))
        )

        def rows_to_dicts(items):
            result: list[dict[str, Any]] = []
            for row in items:
                data = dict(row._mapping)

                instance_ext: dict[str, Any] = {}
                instance_variable = data.pop("instanceVariable", None)
                if instance_variable:
                    try:
                        instance_ext = json.loads(instance_variable)
                    except Exception:
                        instance_ext = {}

                data["instanceExt"] = instance_ext
                result.append(data)
            return result

        return await paging_data(db, stmt, transformer=rows_to_dicts)

    @classmethod
    async def get_detail(cls, db: AsyncSession, task_id: int) -> dict[str, Any]:
        """获取任务详情，返回任务信息 + 节点表单Key + 表单数据"""
        import json
        from backend.plugin.wf.model.process_define import ProcessDefine
        from backend.plugin.wf.engine.parser.model_parser import ModelParser

        stmt = select(ProcessTask).where(ProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise ValueError(f"任务[{task_id}]不存在")

        # 获取流程实例
        stmt = select(ProcessInstance).where(ProcessInstance.id == task.process_instance_id)
        result = await db.execute(stmt)
        instance = result.scalars().first()

        # 获取流程定义
        stmt = select(ProcessDefine).where(ProcessDefine.id == instance.process_define_id)
        result = await db.execute(stmt)
        process_define = result.scalars().first()

        # 解析流程模型，获取节点的表单 key（TaskModel.form 属性）
        task_form_key = None
        task_form_data = {}
        if process_define and process_define.content:
            process_model = ModelParser.parse(process_define.content)
            node_model = process_model.get_node(task.task_name)
            if node_model and hasattr(node_model, 'form'):
                task_form_key = node_model.form

        # 解析实例变量
        ext = {}
        if instance.variable:
            try:
                ext = json.loads(instance.variable)
            except Exception:
                pass

        # 解析任务变量（可能包含节点表单数据）
        if task.variable:
            try:
                task_var = json.loads(task.variable)
                task_form_data = task_var.get("formData", {})
            except Exception:
                pass

        return {
            "id": task.id,
            "processInstanceId": task.process_instance_id,
            "taskName": task.task_name,
            "displayName": task.display_name,
            "taskType": task.task_type,
            "performType": task.perform_type,
            "taskState": task.task_state,
            "operator": task.operator,
            "finishTime": task.finish_time,
            "createdTime": task.created_time,
            "ext": ext,
            "taskFormData": task_form_data,
            "taskFormKey": task_form_key,
        }

    @classmethod
    async def add_candidate_actor(cls, db: AsyncSession, task_id: int, actor_ids: list[str], user_id: int = None) -> bool:
        """加签：为任务增加参与人
        
        这里简化实现：
        1. 获取当前任务
        2. 为每个新参与人复制一个新任务（状态为进行中）
        """
        import json
        stmt = select(ProcessTask).where(ProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise ValueError(f"任务[{task_id}]不存在")

        for actor_id in actor_ids:
            new_task = ProcessTask(
                process_instance_id=task.process_instance_id,
                task_name=task.task_name,
                display_name=task.display_name,
                task_type=task.task_type,
                perform_type=task.perform_type,
                task_state=10,  # 进行中
                operator=actor_id,
                variable=task.variable,
                created_by=user_id or task.created_by,
            )
            db.add(new_task)
        
        await db.flush()
        return True

    @classmethod
    async def get_jump_able_task_name_list(cls, db: AsyncSession, task_id: int) -> list[dict[str, str]]:
        """获取可跳转的节点列表"""
        from backend.plugin.wf.model.process_define import ProcessDefine
        from backend.plugin.wf.engine.parser.model_parser import ModelParser
        from backend.plugin.wf.engine.model.task_model import TaskModel

        stmt = select(ProcessTask).where(ProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise ValueError(f"任务[{task_id}]不存在")

        stmt = select(ProcessInstance).where(ProcessInstance.id == task.process_instance_id)
        result = await db.execute(stmt)
        instance = result.scalars().first()

        stmt = select(ProcessDefine).where(ProcessDefine.id == instance.process_define_id)
        result = await db.execute(stmt)
        process_define = result.scalars().first()

        if not process_define or not process_define.content:
            return []

        process_model = ModelParser.parse(process_define.content)
        # 返回所有任务节点（排除当前节点），通过 isinstance 判断是否为 TaskModel
        nodes = []
        for node in process_model.nodes:
            if node.name != task.task_name and isinstance(node, TaskModel):
                nodes.append({
                    "nodeId": node.name,
                    "nodeName": node.displayName or node.name,
                })
        return nodes

    @classmethod
    async def jump(cls, db: AsyncSession, task_id: int, target_node_id: str, operator: str, user_id: int = None) -> bool:
        """跳转到指定节点
        
        简化实现：
        1. 将当前任务标记为已完成（跳转）
        2. 在目标节点创建新任务
        """
        import json
        from backend.plugin.wf.model.process_define import ProcessDefine
        from backend.plugin.wf.engine.parser.model_parser import ModelParser

        stmt = select(ProcessTask).where(ProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise ValueError(f"任务[{task_id}]不存在")

        # 标记当前任务为已完成
        task.task_state = 20
        task.finish_time = datetime.now()
        task.operator = operator
        # 记录跳转信息
        variable = {}
        if task.variable:
            try:
                variable = json.loads(task.variable)
            except:
                pass
        variable["submitType"] = "jump"
        variable["jumpTo"] = target_node_id
        task.variable = json.dumps(variable, ensure_ascii=False)
        db.add(task)

        # 获取流程定义
        stmt = select(ProcessInstance).where(ProcessInstance.id == task.process_instance_id)
        result = await db.execute(stmt)
        instance = result.scalars().first()

        stmt = select(ProcessDefine).where(ProcessDefine.id == instance.process_define_id)
        result = await db.execute(stmt)
        process_define = result.scalars().first()

        process_model = ModelParser.parse(process_define.content)
        target_node = process_model.get_node(target_node_id)
        if not target_node:
            raise ValueError(f"目标节点[{target_node_id}]不存在")

        # 创建目标节点任务（这里简化处理，实际应根据节点配置获取处理人）
        new_task = ProcessTask(
            process_instance_id=task.process_instance_id,
            task_name=target_node.name,
            display_name=target_node.displayName,  # NodeModel 使用驼峰命名
            task_type=0,
            perform_type=0,
            task_state=10,
            operator=operator,  # 简化：跳转后由当前操作人处理
            created_by=user_id or task.created_by,
        )
        db.add(new_task)
        await db.flush()
        return True

    @classmethod
    async def surrogate(cls, db: AsyncSession, task_id: int, user_id: str) -> bool:
        """委托：将任务委托给其他人处理"""
        import json
        stmt = select(ProcessTask).where(ProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise ValueError(f"任务[{task_id}]不存在")

        original_operator = task.operator
        task.operator = user_id

        # 记录委托信息
        variable = {}
        if task.variable:
            try:
                variable = json.loads(task.variable)
            except:
                pass
        variable["surrogateFrom"] = original_operator
        task.variable = json.dumps(variable, ensure_ascii=False)

        db.add(task)
        await db.flush()
        return True
