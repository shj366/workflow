from backend.plugin.wf.engine.model import BaseModel
from backend.plugin.wf.engine.model.start_model import StartModel
from backend.plugin.wf.engine.model.task_model import TaskModel
from backend.plugin.wf.engine.model.end_model import EndModel


class ProcessModel(BaseModel):
    type = None  # 流程定义分类
    instanceUrl = None  # 启动实例要填写的表单key
    expireTime = None  # 期待完成时间变量key
    instanceNoClass = None  # 实例编号生成器实现类
    # 流程定义的所有节点
    nodes = []
    # 流程定义的所有任务节点
    tasks = []
    preInterceptors = None  # 流程定义前置拦截器
    postInterceptors = None  # 流程定义后置拦截器

    def __init__(self):
        self.type = None
        self.instanceUrl = None  # 启动实例要填写的表单key
        self.expireTime = None  # 期待完成时间变量key
        self.instanceNoClass = None  # 实例编号生成器实现类
        # 流程定义的所有节点
        self.nodes = []
        # 流程定义的所有任务节点
        self.tasks = []
        self.preInterceptors = None  # 流程定义前置拦截器
        self.postInterceptors = None  # 流程定义后置拦截器

    def get_start(self):
        """
        获取流程模型的开始节点
        """
        startModel = None
        for node in self.nodes:
            if isinstance(node, StartModel):
                startModel = node
                break
        return startModel

    def get_node(self, nodeName: str):
        """
        获取process定义的指定节点名称的节点模型
        @param nodeName: 节点名称
        """
        nodeModel = None
        for node in self.nodes:
            if node.name == nodeName:
                nodeModel = node
                break
        return nodeModel

    def get_end(self):
        """
        获取流程模型的结束节点
        """
        endModel = None
        for node in self.nodes:
            if isinstance(node, EndModel):
                endModel = node
                break
        return endModel
