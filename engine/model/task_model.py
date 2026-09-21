from backend.plugin.wf.engine.model import NodeModel


class TaskModel(NodeModel):
    """
    任务节点模型
    """
    assignee = None
    assigneeDisplay = None
    form = None
    
    async def exec(self, execution):
        pass
