from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UserMixin, id_key


class ProcessCCInstance(Base, UserMixin):
    """
    流程实例抄送
    """

    __tablename__ = "wf_process_cc_instance"
    
    id: Mapped[id_key] = mapped_column(init=False)
    
    process_instance_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="流程实例ID")
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="被抄送人ID")
    # 抄送状态(1:已读；0：未读)
    state: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0, comment="抄送状态")
