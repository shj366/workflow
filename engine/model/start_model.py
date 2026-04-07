from backend.plugin.wf.engine.model import NodeModel


class StartModel(NodeModel):
    """
    开始节点
    """

    async def exec(self, execution):
        """
        执行
        @param execution: 执行对象参数
        """
        await self.run_out_transition(execution)
