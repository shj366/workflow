from typing import List, Any, TYPE_CHECKING

from backend.plugin.wf.engine.model import NodeModel
from backend.plugin.wf.engine.model.process_model import ProcessModel
from backend.plugin.wf.model.process_instance import ProcessInstance
from backend.plugin.wf.model.process_task import ProcessTask

if TYPE_CHECKING:
    from backend.plugin.wf.engine.core.flow_engine import FlowEngine


class Execution:
    """
    流程执行对象
    """

    engine: "FlowEngine" = None  # 引擎实例
    process_instance: ProcessInstance = None  # 流程实例
    process_instance_id: int = None  # 流程实例ID
    process_model: ProcessModel = None  # 当前流程模型
    process_task: ProcessTask = None  # 当前任务
    process_task_id: int = None  # 当前流程任务ID
    node_model: NodeModel = None  # 当前节点模型
    args: dict[str, Any] = {}  # 执行对象扩展参数
    operator: str = None  # 操作人
    process_task_list: List[ProcessTask] = []  # 所有任务集合
    is_merged: bool = False  # 是否合并

    def __init__(self, engine: "FlowEngine", process_instance: ProcessInstance, process_model: ProcessModel, operator: str = None, args: dict = None):
        self.engine = engine
        self.process_instance = process_instance
        self.process_instance_id = process_instance.id
        self.process_model = process_model
        self.operator = operator
        self.args = args or {}
        self.process_task_list = []

    def add_task(self, process_task: ProcessTask):
        """
        添加任务到任务集合
        """
        self.process_task_list.append(process_task)

    def add_tasks(self, process_tasks: List[ProcessTask]):
        """
        添加任务集合到任务集合
        """
        self.process_task_list.extend(process_tasks)
