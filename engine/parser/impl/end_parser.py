from backend.plugin.wf.engine.model.end_model import EndModel
from backend.plugin.wf.engine.parser.abstract_node_parser import AbstractNodeParser


class EndParser(AbstractNodeParser):
    """
    结束节点解析器
    """

    def parse_node(self, lfNode):
        pass

    def new_nodel(self):
        return EndModel()
