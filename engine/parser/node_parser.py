from abc import ABC, abstractmethod

from backend.plugin.wf.engine.model import NodeModel


class NodeParser(ABC):
    """
    节点解析器
    """

    __abstract__ = True
    ID_KEY = "id"  # 节点id
    NODE_NAME_PREFIX = "snaker:"  # 节点名称前辍
    NODES_KEY = "nodes"  # 节点
    EDGES_KEY = "edges"  # 边
    TARGET_NODE_ID = "targetNodeId"  # 目标节点id
    SOURCE_NODE_ID = "sourceNodeId"  # 源节点id
    PROPERTIES_KEY = "properties"  # 属性KEy
    TEXT_KEY = "text"  # 文本节点
    TEXT_VALUE_KEY = "value"  # 文本值
    WIDTH_KEY = "width"  # 节点宽度
    HEIGHT_KEY = "height"  # 节点高度
    PRE_INTERCEPTORS_KEY = "preInterceptors"  # 前置拦截器
    POST_INTERCEPTORS_KEY = "postInterceptors"  # 后置拦截器
    EXPR_KEY = "expr"  # 表达式key
    HANDLE_CLASS_KEY = "handleClass"  # 表达式处理类
    FORM_KEY = "form"  # 表单标识
    ASSIGNEE_KEY = "assignee"  # 参与人
    ASSIGNMENT_HANDLE_KEY = "assignmentHandler"  # 参与人处理类
    TASK_TYPE_KEY = "taskType"  # 任务类型(主办/协办)
    PERFORM_TYPE_KEY = "performType"  # 参与类型(普通参与/会签参与)
    REMINDER_TIME_KEY = "reminderTime"  # 提醒时间
    REMINDER_REPEAT_KEY = "reminderRepeat"  # 重复提醒间隔
    EXPIRE_TIME_KEY = "expireTime"  # 期待任务完成时间变量key
    AUTH_EXECUTE_KEY = "autoExecute"  # 到期是否自动执行Y/N
    CALLBACK_KEY = "callback"  # 自动执行回调类
    EXT_FIELD_KEY = "field"  # 自定义扩展属性
    CANDIDATE_USERS_KEY = "candidateUsers"  # 候选用户
    CANDIDATE_GROUPS_KEY = "candidateGroups"  # 候选组
    CANDIDATE_HANDLER_KEY = "candidateHandler"  # 候选处理类
    FIELD_COUNTERSIGN_TYPE_KEY = "countersignType"  # 会签类型
    FIELD_COUNTERSIGN_COMPLETION_CONDITION_KEY = "countersignCompletionCondition"  # 会签完成条件
    CLASS_KEY = "clazz"  # 类路径
    METHOD_NAME_KEY = "methodName"  # 方法名
    ARGS_KEY = "args"   # 方法入参
    RETURN_VAL_KEY = "val"  # 返回变量名
    VERSION_KEY = "version"  # 版本号

    @abstractmethod
    def parse(self, lfNode, lfEdges):
        """
        节点属性解析方法，由解析类完成解析
        @param lfNode LogicFlow节点对象
        @param lfEdges 所有边对象
        """
        pass

    @abstractmethod
    def get_model(self) -> NodeModel:
        """
        解析完成后，提供返回NodeModel对象
        """
        pass
