from datetime import datetime
from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UserMixin, id_key


class ProcessInstance(Base, UserMixin):
    """
    流程实例实体
    """

    __tablename__ = "wf_process_instance"
    
    id: Mapped[id_key] = mapped_column(init=False)
    
    process_define_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="流程定义ID")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None, comment="父流程ID，子流程实例才有值")
    # 流程实例状态(10：进行中；20：已完成；30：已撤回；40：强行中止；50：挂起；99：已废弃)
    state: Mapped[int | None] = mapped_column(Integer, nullable=True, default=10, comment="流程实例状态")
    parent_node_name: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None, comment="父流程依赖的节点名称")
    business_no: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None, comment="业务编号")
    operator: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None, comment="流程发起人")
    expire_time: Mapped[datetime | None] = mapped_column(nullable=True, default=None, comment="期望完成时间")
    variable: Mapped[str | None] = mapped_column(String(4000), nullable=True, default=None, comment="附属变量json存储")
