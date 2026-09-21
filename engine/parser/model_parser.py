import io
import json

from backend.plugin.wf.engine.model.process_model import ProcessModel
from backend.plugin.wf.engine.model.task_model import TaskModel
from backend.plugin.wf.engine.parser.impl.decision_parser import DecisionParser
from backend.plugin.wf.engine.parser.impl.end_parser import EndParser
from backend.plugin.wf.engine.parser.impl.start_parser import StartParser
from backend.plugin.wf.engine.parser.impl.task_parser import TaskParser
from backend.plugin.wf.engine.parser.node_parser import NodeParser


class ModelParser(object):
    """
    流程模型解析器
    """

    parserMap = {
        "start": StartParser(),
        "end": EndParser(),
        "task": TaskParser(),
        "decision": DecisionParser(),
        # "fork": ForkParser(),
        # "join": JoinParser(),
        # "custom": CustomParser(),
        # "wfSubProcess": WfSubProcessParser(),
    }

    @staticmethod
    def parse(jsonData):
        """
        将json定义文件解析成流程模型对象
        """
        processModel: ProcessModel = ProcessModel()
        if isinstance(jsonData, io.TextIOWrapper):
            lfModel = json.load(jsonData)
        elif isinstance(jsonData, str):
            lfModel = json.loads(jsonData)
        elif isinstance(jsonData, (bytes, bytearray)):
            lfModel = json.loads(jsonData.decode("utf-8"))
        elif isinstance(jsonData, dict):
            lfModel = jsonData
        else:
            raise ValueError("jsonData must be a json string or a file object")
        lfNodes = lfModel.get(NodeParser.NODES_KEY)
        lfEdges = lfModel.get(NodeParser.EDGES_KEY)
        if lfNodes is None or len(lfNodes) == 0 or lfEdges is None or len(lfEdges) == 0:
            return processModel
        # 流程定义基本信息
        processModel.name = lfModel.get("name")
        processModel.displayName = lfModel.get("displayName")
        processModel.type = lfModel.get("type")
        processModel.instanceUrl = lfModel.get("instanceUrl")
        processModel.instanceNoClass = lfModel.get("instanceNoClass")
        processModel.preInterceptors = lfModel.get("preInterceptors")
        processModel.postInterceptors = lfModel.get("postInterceptors")
        # 流程节点信息
        for node in lfNodes:
            nodeType = node.get("type", "").replace("snaker:", "")
            nodeParser: NodeParser = ModelParser.parserMap.get(nodeType)
            if nodeParser is None:
                continue
            nodeParser.parse(node, lfEdges)
            nodeModel = nodeParser.get_model()
            processModel.nodes.append(nodeModel)
            if isinstance(nodeModel, TaskModel):
                processModel.tasks.append(nodeModel)
        # 循环节点模型，构造输入边、输出边的source、target
        for node in processModel.nodes:
            for transition in node.outputs:
                to = transition.to
                for node2 in processModel.nodes:
                    if node2.name == to:
                        node2.inputs.append(transition)
                        transition.target = node2
                        # fix: transition.source is already set in parser
        return processModel
