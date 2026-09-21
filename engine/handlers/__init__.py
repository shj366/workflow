from abc import ABC, abstractmethod


class IHandler(ABC):
    """
    流程各模型操作处理接口
    """

    @abstractmethod
    async def handle(self, execution):
        """
        子类需要实现的方法，来处理具体的操作
        :param execution:执行对象
        """
        pass
