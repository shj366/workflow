from sqlalchemy import Integer, String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UserMixin, id_key


class ProcessDefine(Base, UserMixin):
    """
    流程定义实体
    """

    __tablename__ = "wf_process_define"
    
    id: Mapped[id_key]
    
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="唯一编码")
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="显示名称")
    type: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="流程类型")
    state: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="流程状态(1可用；0不可用)")
    content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True, comment="流程模型定义")
    version: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="流程版本")

