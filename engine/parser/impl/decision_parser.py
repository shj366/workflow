from backend.plugin.wf.engine.model.decision_model import DecisionModel
from backend.plugin.wf.engine.parser.abstract_node_parser import AbstractNodeParser
from backend.plugin.wf.engine.parser.node_parser import NodeParser


class DecisionParser(AbstractNodeParser):
    """
    决策节点解析器
    """

    def parse_node(self, lfNode):
        properties = lfNode.get(NodeParser.PROPERTIES_KEY, {})
        self.nodeModel.expr = properties.get(NodeParser.EXPR_KEY)
        self.nodeModel.handleClass = properties.get(NodeParser.HANDLE_CLASS_KEY)

    def new_nodel(self):
        return DecisionModel()
