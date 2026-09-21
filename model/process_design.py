"""流程设计模型"""
from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class ProcessDesign(Base):
    """流程设计表 - 用于设计和管理流程模板"""

    __tablename__ = "wf_process_design"
    __table_args__ = {"comment": "流程设计"}

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(64), comment="唯一编码", index=True)
    display_name: Mapped[str | None] = mapped_column(String(100), default=None, comment="显示名称")
    type: Mapped[int | None] = mapped_column(Integer, default=None, comment="流程类型")
    icon: Mapped[str | None] = mapped_column(String(100), default=None, comment="图标")
    is_deployed: Mapped[int] = mapped_column(Integer, default=0, comment="是否已部署(1是；0否)")
    json_object: Mapped[str | None] = mapped_column(Text, default=None, comment="流程定义JSON")
    remark: Mapped[str | None] = mapped_column(String(200), default=None, comment="备注")

    create_time: Mapped[datetime] = mapped_column(
        DateTime, init=False, default_factory=datetime.now, comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        default_factory=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )
    create_user: Mapped[int | None] = mapped_column(BigInteger, default=None, comment="创建用户")
    update_user: Mapped[int | None] = mapped_column(BigInteger, default=None, comment="更新用户")
    is_deleted: Mapped[int] = mapped_column(Integer, default=0, comment="是否删除")
