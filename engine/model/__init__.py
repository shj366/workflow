from abc import ABC, abstractmethod
import logging

from backend.plugin.wf.engine.handlers import IHandler
from backend.plugin.wf.engine.util.reflect_util import ReflectUtil
from backend.plugin.wf.engine.util.expr_util import ExprUtil


class BaseModel(object):
    """
    基础模型
    """

    __abstract__ = True
    # 唯一编码
    name = None
    # 显示名称
    displayName = None

    async def fire(self, handler: IHandler, execution):
        """
        将执行对象execution交给具体的处理器处理
        @param handler: 处理器
        @param execution: 执行对象参数
        """
        await handler.handle(execution)


class Action(object):
    """
    节点行为接口
    """

    __abstract__ = True

    async def execute(self, execution):
        """
        执行行为
        @param execution: 执行对象参数
        """


class NodeModel(ABC, BaseModel, Action):
    """
    节点模型
    """

    __abstract__ = True
    # 输入边集合
    inputs = []
    # 输出边集合
    outputs = []
    # 前置拦截器-字符串，多个使用英文逗号分割
    preInterceptors = None
    # 后置拦截器-字符串，多个使用英文逗号分割
    postInterceptors = None

    def __init__(self):
        """
        构造函数-重新初始化属性
        因python的父类属性会共享，所以需要重新初始化属性，要不然所有的节点属性都指向同一个对象
        """
        self.inputs = []
        self.outputs = []
        self.preInterceptors = None
        self.postInterceptors = None

    @abstractmethod
    async def exec(self, execution):
        """
        由子类自定义执行方法
        @param execution: 执行对象参数
        """

    async def execute(self, execution):
        """
        执行节点
        @param execution: 执行对象参数
        """
        # 0. 设置当前节点模型
        execution.node_model = self
        # 1. 执行前置拦截器
        self._exec_pre_interceptors(execution)
        # 2. 调用子类的exec方法
        await self.exec(execution)
        # 3. 执行后置拦截器
        self._exec_post_interceptors(execution)

    async def run_out_transition(self, execution):
        """
        执行输出边
        """
        for transition in self.outputs:
            transition.enabled = True
            await transition.execute(execution)

    def get_next_models(self, clazz):
        """
        获取下一个节点模型
        @param clazz: 节点模型类
        """
        # 记录已递归项，防止死循环
        temp = {}
        models = []
        for tm in self.outputs:
            self._add_next_models(models, tm, clazz, temp)
        return models

    @staticmethod
    def can_rejected(current, parent) -> bool:
        """
        根据父节点模型、当前节点模型判断是否可退回。可退回条件：
        1、满足中间无fork、join、subprocess模型
        2、满足父节点模型如果为任务模型时，参与类型为any
        @param parent 父节点模型
        @return 是否可以退回
        """
        result: bool = False
        for tm in current.inputs:
            source = tm.source
            if source == parent:
                return True
            logging.debug(source.__class__.__name__)
            if source.__class__.__name__ in ["ForkModel", "JoinModel", "StartModel"]:
                continue
            result = result or NodeModel.can_rejected(source, parent)

        return result

    def _add_next_models(self, models, tm, clazz, temp: dict):
        if tm.to in temp:
            return
        if isinstance(tm.target, clazz):
            models.append(tm.target)
        else:
            for tm2 in tm.target.outputs:
                temp[tm.to] = tm.target
                self._add_next_models(models, tm2, clazz, temp)

    def _exec_interceptors(self, interceptors: str, execution):
        """
        执行节点拦截器
        @param interceptors: 拦截器字符串
        @param execution: 执行对象参数
        """
        if interceptors is None or len(interceptors) == 0:
            return
        # 存在多个，英文逗号分割
        interceptors = interceptors.split(",")
        for interceptor in interceptors:
            # 反射实例化
            flowInterceptor = ReflectUtil.new_instance(interceptor)
            if flowInterceptor is not None:
                flowInterceptor.intercept(execution)

    def _exec_pre_interceptors(self, execution):
        """
        执行节点前置拦截器
        """
        if self.preInterceptors is None or len(self.preInterceptors) == 0:
            self.preInterceptors = execution.process_model.preInterceptors
        self._exec_interceptors(self.preInterceptors, execution)

    def _exec_post_interceptors(self, execution):
        """
        执行节点后置拦截器
        """
        if self.postInterceptors is None or len(self.postInterceptors) == 0:
            self.postInterceptors = execution.process_model.postInterceptors
        self._exec_interceptors(self.postInterceptors, execution)

    def __repr__(self) -> str:
        """
        重写输出
        """
        return f"调用模型节点执行方法：model:{self.__class__.__name__},name:{self.name},displayName:{self.displayName}"
