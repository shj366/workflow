from backend.plugin.wf.engine.handlers import IHandler
from backend.plugin.wf.engine.model.task_model import TaskModel
from backend.plugin.wf.model.process_task import ProcessTask


class CreateTaskHandler(IHandler):
    """
    创建任务处理器
    """

    model: TaskModel

    def __init__(self, model: TaskModel):
        self.model = model

    async def handle(self, execution):
        """
        处理创建任务
        """
        from backend.plugin.wf.service.process_task import ProcessTaskService

        # 确定任务执行人（支持 Assignee 和 Candidate）
        # 调用 Service 中的通用解析逻辑
        actors = ProcessTaskService._get_task_actors(self.model, execution)
        
        # 确定主要操作人 (operator)
        # 如果解析出了多个参与者，取第一个作为 operator（用于列表显示兼容），其他作为 actor 存储
        # 如果解析出了角色 (ROLE:xxx)，也作为 operator 存入，后续查询会处理
        assignee = actors[0] if actors else execution.operator
            
        # 构建任务对象
        task = ProcessTask(
            process_instance_id=execution.process_instance.id,
            task_name=self.model.name,
            display_name=self.model.displayName,
            task_type=0,  # 默认主办
            perform_type=0,  # 默认普通参与
            task_state=10,  # 进行中
            operator=assignee,
            form_key=self.model.form,
            created_by=execution.process_instance.created_by or 1,  # 继承创建人
        )
        task.updated_by = execution.process_instance.updated_by
        
        # 创建任务（这会自动将 operator 加入 actor 表）
        await execution.engine.create_task(task, execution)
        
        # 将剩余的参与者也加入 actor 表
        if len(actors) > 1:
            # 排除已经作为 operator 加入的第一个
            remaining_actors = [a for a in actors if a != assignee]
            if remaining_actors:
                await ProcessTaskService.add_task_actor(execution.engine.db, task.id, remaining_actors)
