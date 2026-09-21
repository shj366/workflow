import logging
from backend.plugin.wf.engine.model import NodeModel
from backend.plugin.wf.engine.util.expr_util import ExprUtil
from backend.plugin.wf.engine.util.reflect_util import ReflectUtil
from backend.plugin.wf.engine.decision_handler import DecisionHandler


class DecisionModel(NodeModel):
    """
    决策节点模型
    """

    expr = None  # 决策表达式
    handleClass = None  # 决策处理类

    def __init__(self):
        super().__init__()
        self.expr = None
        self.handleClass = None

    async def exec(self, execution):
        """
        执行节点
        @param execution: 执行对象参数
        """
        is_found = False
        next_node_name = None
        args = execution.args or {}
        
        # 1. 优先使用决策表达式
        if self.expr:
            next_node_name = ExprUtil.eval(self.expr, args)
        # 2. 其次使用决策处理类
        elif self.handleClass:
            logging.debug(f"load handleClass: {self.handleClass}")
            handle_instance: DecisionHandler = ReflectUtil.new_instance(self.handleClass)
            if handle_instance:
                next_node_name = handle_instance.decide(execution)
                logging.debug(f"{self.handleClass} decide result: {next_node_name}")
            else:
                logging.error(f"Failed to load handleClass: {self.handleClass}")

        for transition in self.outputs:
            # 决策节点输出边存在表达式，则使用输出边的表达式，true则执行
            if transition.expr and ExprUtil.eval(transition.expr, args):
                is_found = True
                transition.enabled = True
                await transition.execute(execution)
            # 找到对应的下一个节点
            elif transition.to == next_node_name:
                is_found = True
                transition.enabled = True
                await transition.execute(execution)
                
        if not is_found:
            # 找不到下一个可执行路线
            logging.error(f'{self.name} 找不到下一个可执行路线')
            # raise Exception(f'{self.name} 找不到下一个可执行路线')
