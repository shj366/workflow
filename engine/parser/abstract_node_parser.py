from abc import abstractmethod

from backend.plugin.wf.engine.model import NodeModel
from backend.plugin.wf.engine.model.transition_model import TransitionModel
from backend.plugin.wf.engine.parser.node_parser import NodeParser


class AbstractNodeParser(NodeParser):
    """
    抽象节点解析器
    """

    nodeModel = None

    def __init__(self):
        self.nodeModel = None

    def parse(self, lfNode, lfEdges: list):
        """
        子类实现此类完成特定解析
        """
        self.nodeModel = self.new_nodel()
        # 解析基本信息
        self.nodeModel.name = lfNode.get(NodeParser.ID_KEY)
        text = lfNode.get(NodeParser.TEXT_KEY, {})
        self.nodeModel.displayName = text.get(NodeParser.TEXT_VALUE_KEY)
        properties = lfNode.get(NodeParser.PROPERTIES_KEY, {})
        # 解析拦截器
        self.nodeModel.preInterceptors = properties.get(NodeParser.PRE_INTERCEPTORS_KEY)
        self.nodeModel.postInterceptors = properties.get(
            NodeParser.POST_INTERCEPTORS_KEY
        )
        # 解析输出边
        nodeEdges = self.get_edge_by_source_node_id(self.nodeModel.name, lfEdges)
        for nodeEdge in nodeEdges:
            transitionModel = TransitionModel()
            transitionModel.name = nodeEdge.get(NodeParser.ID_KEY)
            transitionModel.to = nodeEdge.get(NodeParser.TARGET_NODE_ID)
            transitionModel.source = self.nodeModel
            trProps = nodeEdge.get(NodeParser.PROPERTIES_KEY, {})
            transitionModel.expr = trProps.get(NodeParser.EXPR_KEY)
            self.nodeModel.outputs.append(transitionModel)
        # 调用子类特定解析方法
        self.parse_node(lfNode)

    @abstractmethod
    def parse_node(self, lfNode):
        """
        子类实现此类完成特定解析
        """

    def new_nodel(self) -> NodeModel:
        """
        由子类各自创建节点模型对象
        """

    def get_model(self) -> NodeModel:
        """
        获取节点模型对象
        """
        return self.nodeModel

    def get_edge_by_target_node_id(self, targetNodeId: str, edges: list):
        """
        获取节点输入
        @param targetNodeId 目标节点id
        @param edges
        """
        res = []
        for edge in edges:
            if edge.get("targetNodeId") == targetNodeId:
                res.append(edge)
        return res

    def get_edge_by_source_node_id(self, sourceNodeId: str, edges: list):
        """
        获取节点输出
        @param sourceNodeId 源节点id
        @param edges
        """
        res = []
        for edge in edges:
            if edge.get("sourceNodeId") == sourceNodeId:
                res.append(edge)
        return res
