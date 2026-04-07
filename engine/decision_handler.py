from abc import ABC, abstractmethod


class DecisionHandler(ABC):
    """
    决策处理类基类
    用于在流程决策节点中自定义决策逻辑
    """
    
    @abstractmethod
    def decide(self, execution) -> str:
        """
        决策方法，返回下一个节点的名称
        @param execution: 执行对象
        @return: 下一个节点的名称
        """
        pass
