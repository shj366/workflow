from backend.plugin.wf.engine.model import Action, BaseModel
from backend.plugin.wf.engine.model.task_model import TaskModel


class TransitionModel(BaseModel, Action):
    source = None  # 边源节点引用
    target = None  # 边目标节点引用
    to = None  # 目标节点名称
    expr = None  # 边表达式
    enabled = False  # 是否可执行

    def __init__(self):
        self.enabled = False
        self.expr = None
        self.source = None
        self.target = None
        self.to = None

    async def execute(self, execution):
        if not self.enabled:
            return
        if isinstance(self.target, TaskModel):
            # 创建阻塞任务
            from backend.plugin.wf.engine.handlers.create_task_handler import CreateTaskHandler
            await self.fire(CreateTaskHandler(self.target), execution)
        # elif isinstance(self.target, SubProcessModel):
        #     # 如果为子流程，则启动子流程
        #     await self.fire(StartSubProcessHandler(self.target), execution)
        else:
            await self.target.execute(execution)
