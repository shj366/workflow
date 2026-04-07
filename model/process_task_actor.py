from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, id_key


class ProcessTaskActor(DataClassBase):
    """
    流程任务和参与人关系
    """

    __tablename__ = "wf_process_task_actor"

    id: Mapped[id_key] = mapped_column(init=False)

    process_task_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="流程任务ID")
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="参与人ID")
