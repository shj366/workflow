from backend.plugin.wf.engine.model.task_model import TaskModel
from backend.plugin.wf.engine.parser.abstract_node_parser import AbstractNodeParser
from backend.plugin.wf.engine.parser.node_parser import NodeParser


class TaskParser(AbstractNodeParser):
    """
    任务节点解析器
    """

    def parse_node(self, lfNode):
        properties = lfNode.get(NodeParser.PROPERTIES_KEY, {})
        self.nodeModel.form = properties.get(NodeParser.FORM_KEY)
        self.nodeModel.assignee = properties.get(NodeParser.ASSIGNEE_KEY)
        self.nodeModel.taskType = properties.get(NodeParser.TASK_TYPE_KEY)
        self.nodeModel.performType = properties.get(NodeParser.PERFORM_TYPE_KEY)
        self.nodeModel.reminderTime = properties.get(NodeParser.REMINDER_TIME_KEY)
        self.nodeModel.reminderRepeat = properties.get(NodeParser.REMINDER_REPEAT_KEY)
        self.nodeModel.expireTime = properties.get(NodeParser.EXPIRE_TIME_KEY)
        self.nodeModel.autoExecute = properties.get(NodeParser.AUTH_EXECUTE_KEY)
        self.nodeModel.callback = properties.get(NodeParser.CALLBACK_KEY)
        self.nodeModel.assignmentHandler = properties.get(NodeParser.ASSIGNMENT_HANDLE_KEY)
        self.nodeModel.candidateUsers = properties.get(NodeParser.CANDIDATE_USERS_KEY)
        self.nodeModel.candidateGroups = properties.get(NodeParser.CANDIDATE_GROUPS_KEY)
        self.nodeModel.candidateHandler = properties.get(NodeParser.CANDIDATE_HANDLER_KEY)

    def new_nodel(self):
        return TaskModel()
