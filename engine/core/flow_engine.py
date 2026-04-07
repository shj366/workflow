from typing import List
from datetime import datetime
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.plugin.wf.engine.core.execution import Execution
from backend.plugin.wf.engine.parser.model_parser import ModelParser
from backend.plugin.wf.engine.model.task_model import TaskModel
from backend.plugin.wf.engine.model.transition_model import TransitionModel
from backend.plugin.wf.model.process_define import ProcessDefine
from backend.plugin.wf.model.process_instance import ProcessInstance
from backend.plugin.wf.model.process_task import ProcessTask
from backend.plugin.wf.service.process_instance import ProcessInstanceService
from backend.plugin.wf.service.process_task import ProcessTaskService


class FlowEngine:
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_process(self, process_define_id: int, operator: str, args: dict = None) -> ProcessInstance:
        """
        启动流程实例
        """
        if args is None:
            args = {}
            
        # 1. 获取流程定义
        stmt = select(ProcessDefine).where(ProcessDefine.id == process_define_id)
        result = await self.db.execute(stmt)
        process_define = result.scalars().first()
        if not process_define:
            raise ValueError(f"流程定义[{process_define_id}]不存在")

        # 2. 解析模型
        process_model = ModelParser.parse(process_define.content)

        # 3. 构造实例变量（variable），尽量对齐 mldong：
        #   - 业务编号/business_no
        #   - 用户相关信息（u_realName 等，需在调用处提前写入 args）
        #   - 自动生成标题 autoGenTitle
        real_name = args.get("u_realName") or args.get("realName") or operator
        now = datetime.now()
        auto_title = f"{real_name}的{process_define.display_name}-{now.strftime('%Y-%m-%d %H:%M')}"
        args.setdefault("autoGenTitle", auto_title)

        # 4. 创建实例
        instance = ProcessInstance(
            process_define_id=process_define.id,
            state=10,  # 进行中
            parent_node_name=None,
            business_no=args.get("business_no"),
            operator=operator,
            created_by=args.get("user_id"),
            variable=json.dumps(args, ensure_ascii=False),
        )
        instance.updated_by = args.get("user_id")
        
        instance = await ProcessInstanceService.create(self.db, instance)

        # 4. 创建执行对象
        execution = Execution(self, instance, process_model, operator, args)

        # 5. 执行开始节点
        start_node = process_model.get_start()
        if not start_node:
            raise ValueError("流程定义中没有开始节点")

        await start_node.execute(execution)

        return instance

    async def start_and_execute(self, process_define_id: int, operator: str, args: dict = None) -> ProcessInstance:
        """
        启动流程并执行第一个任务（发起申请）
        """
        # 1. 启动流程
        instance = await self.start_process(process_define_id, operator, args)
        
        # 2. 获取当前待办任务
        tasks = await ProcessTaskService.get_doing_task_list(self.db, instance.id)
        
        # 3. 自动执行第一个任务（申请节点）
        for task in tasks:
            if args is None:
                args = {}
            args["submit_type"] = "apply"  # 标记为申请提交
            await self.complete_task(task.id, operator, args)
        
        return instance

    async def create_task(self, task: ProcessTask, execution: Execution) -> List[ProcessTask]:
        """
        创建任务
        """
        # 保存任务
        await ProcessTaskService.create(self.db, task)
        # 添加到execution
        execution.add_task(task)
        return [task]
        
    async def complete_task(self, task_id: int, operator: str, args: dict = None, user_id: int = None) -> List[ProcessTask]:
        """
        完成任务
        """
        # 1. 完成任务，传递args以保存审批意见等
        task = await ProcessTaskService.complete(self.db, task_id, operator, args, user_id)
        
        # 2. 获取流程实例
        stmt = select(ProcessInstance).where(ProcessInstance.id == task.process_instance_id)
        result = await self.db.execute(stmt)
        instance = result.scalars().first()
        
        # 3. 获取流程定义
        stmt = select(ProcessDefine).where(ProcessDefine.id == instance.process_define_id)
        result = await self.db.execute(stmt)
        process_define = result.scalars().first()
        
        # 4. 解析模型
        process_model = ModelParser.parse(process_define.content)
        
        # 5. 找到节点模型
        node_model = process_model.get_node(task.task_name)
        if not node_model:
            raise ValueError(f"任务节点[{task.task_name}]在流程定义中不存在")
        
        # 6. 合并流程变量和当前参数（按 mldong 方式）
        # 流程变量（包含表单数据如 f_je）存储在 process_instance.variable 中
        merged_args = {}
        if instance.variable:
            try:
                merged_args = json.loads(instance.variable)
            except:
                pass
        merged_args.update(args or {})
            
        # 7. 创建执行对象
        execution = Execution(self, instance, process_model, operator, merged_args)
        
        # 8. 执行流转
        await node_model.run_out_transition(execution)

        # 9. 如果该流程实例已经没有进行中的任务，则标记流程实例为已完成（state=20）
        doing_tasks = await ProcessTaskService.get_doing_task_list(self.db, instance.id)
        if not doing_tasks:
            instance.state = 20  # 已完成
            await ProcessInstanceService.update(self.db, instance)

        return execution.process_task_list

    async def _prepare_execution(self, task_id: int, operator: str, args: dict = None, user_id: int = None) -> tuple:
        """
        准备执行对象（完成任务但不流转）
        返回 (task, execution, process_model, instance)
        """
        # 1. 完成任务
        task = await ProcessTaskService.complete(self.db, task_id, operator, args, user_id)
        
        # 2. 获取流程实例
        stmt = select(ProcessInstance).where(ProcessInstance.id == task.process_instance_id)
        result = await self.db.execute(stmt)
        instance = result.scalars().first()
        
        # 3. 获取流程定义
        stmt = select(ProcessDefine).where(ProcessDefine.id == instance.process_define_id)
        result = await self.db.execute(stmt)
        process_define = result.scalars().first()
        
        # 4. 解析模型
        process_model = ModelParser.parse(process_define.content)
        
        # 5. 创建执行对象
        execution = Execution(self, instance, process_model, operator, args)
        execution.process_task = task
        
        return task, execution, process_model, instance

    async def execute_and_rollback(self, task_id: int, operator: str, args: dict = None, user_id: int = None) -> List[ProcessTask]:
        """
        执行任务并退回上一步
        """
        task, execution, process_model, instance = await self._prepare_execution(task_id, operator, args, user_id)
        
        # 找到上一个任务节点
        current_node = process_model.get_node(task.task_name)
        if not current_node:
            raise ValueError(f"任务节点[{task.task_name}]在流程定义中不存在")
        
        # 找到可以退回的前置任务节点
        prev_task_name = await self._find_previous_task_name(instance.id, task.task_name)
        if not prev_task_name:
            raise ValueError("没有可退回的前置节点")
        
        prev_node = process_model.get_node(prev_task_name)
        if not prev_node or not isinstance(prev_node, TaskModel):
            raise ValueError(f"前置节点[{prev_task_name}]不是任务节点")
        
        # 创建新任务到前置节点
        new_task = ProcessTask(
            process_instance_id=instance.id,
            task_name=prev_node.name,
            display_name=prev_node.displayName,
            task_type=0,
            perform_type=0,
            task_state=10,  # 进行中
            operator=prev_node.assignee or instance.operator,  # 使用原处理人或发起人
            created_by=user_id or task.created_by,
        )
        await ProcessTaskService.create(self.db, new_task)
        execution.add_task(new_task)
        
        return execution.process_task_list

    async def execute_and_jump_to_end(self, task_id: int, operator: str, args: dict = None, user_id: int = None) -> List[ProcessTask]:
        """
        执行任务并跳转到结束节点（拒绝）
        """
        task, execution, process_model, instance = await self._prepare_execution(task_id, operator, args, user_id)
        
        # 找到结束节点
        end_node = process_model.get_end()
        if not end_node:
            raise ValueError("流程定义中没有结束节点")
        
        # 执行结束节点（会将流程实例标记为已完成）
        await end_node.execute(execution)
        
        # 标记流程实例为已完成（拒绝状态）
        instance.state = 20  # 已完成
        await ProcessInstanceService.update(self.db, instance)
        
        return execution.process_task_list

    async def execute_and_rollback_to_operator(self, task_id: int, operator: str, args: dict = None, user_id: int = None) -> List[ProcessTask]:
        """
        执行任务并退回发起人（跳转到第一个任务节点）
        """
        task, execution, process_model, instance = await self._prepare_execution(task_id, operator, args, user_id)
        
        # 找到开始节点
        start_node = process_model.get_start()
        if not start_node:
            raise ValueError("流程定义中没有开始节点")
        
        # 找到第一个任务节点（开始节点的输出目标）
        first_task_node = None
        for output in start_node.outputs:
            if isinstance(output.target, TaskModel):
                first_task_node = output.target
                break
        
        if not first_task_node:
            raise ValueError("找不到第一个任务节点")
        
        # 创建新任务，处理人为流程发起人
        new_task = ProcessTask(
            process_instance_id=instance.id,
            task_name=first_task_node.name,
            display_name=first_task_node.displayName,
            task_type=0,
            perform_type=0,
            task_state=10,  # 进行中
            operator=instance.operator,  # 流程发起人
            created_by=user_id or task.created_by,
        )
        await ProcessTaskService.create(self.db, new_task)
        execution.add_task(new_task)
        
        return execution.process_task_list

    async def _find_previous_task_name(self, instance_id: int, current_task_name: str) -> str | None:
        """
        查找上一个已完成的任务名称
        """
        # 获取该实例的所有已完成任务，按时间倒序
        stmt = (
            select(ProcessTask)
            .where(
                ProcessTask.process_instance_id == instance_id,
                ProcessTask.task_state == 20,  # 已完成
                ProcessTask.task_name != current_task_name
            )
            .order_by(ProcessTask.finish_time.desc())
        )
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        
        if tasks:
            return tasks[0].task_name
        return None
