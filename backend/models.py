from sqlalchemy import String, BigInteger, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Vocab(Base):
    __tablename__ = "vocab"
    __table_args__ = (UniqueConstraint("zh", "ja", name="uniq_zh_ja"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    zh: Mapped[str] = mapped_column(String(255), nullable=False)
    ja: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
