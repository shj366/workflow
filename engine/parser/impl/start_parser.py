from backend.plugin.wf.engine.model.start_model import StartModel
from backend.plugin.wf.engine.parser.abstract_node_parser import AbstractNodeParser


class StartParser(AbstractNodeParser):
    """
    开始节点解析器
    """

    def parse_node(self, lfNode):
        pass

    def new_nodel(self):
        return StartModel()
