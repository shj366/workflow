from datetime import datetime
from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UserMixin, id_key


class ProcessTask(Base, UserMixin):
    """
    流程任务实体
    """

    __tablename__ = "wf_process_task"
    
    id: Mapped[id_key] = mapped_column(init=False)
    
    process_instance_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="流程实例ID")
    task_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="任务名称编码")
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None, comment="任务显示名称")
    # 任务类型(0：主办任务；1：协办任务)
    task_type: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0, comment="任务类型")
    # 参与类型(0：普通参与；1：会签参与)
    perform_type: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0, comment="参与类型")
    # 任务状态(10：进行中；20：已完成；30：已撤回；40：强行中止；50：挂起；99：已废弃)
    task_state: Mapped[int | None] = mapped_column(Integer, nullable=True, default=10, comment="任务状态")
    operator: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None, comment="任务处理人")
    finish_time: Mapped[datetime | None] = mapped_column(nullable=True, default=None, comment="任务完成时间")
    expire_time: Mapped[datetime | None] = mapped_column(nullable=True, default=None, comment="任务期待完成时间")
    form_key: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None, comment="任务处理表单KEY")
    task_parent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None, comment="父任务ID")
    variable: Mapped[str | None] = mapped_column(String(4000), nullable=True, default=None, comment="附属变量json存储")
