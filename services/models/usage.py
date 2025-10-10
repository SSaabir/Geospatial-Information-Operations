from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .user import Base, UserDB


class UsageMetrics(Base):
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    api_calls = Column(Integer, default=0, nullable=False)
    reports_generated = Column(Integer, default=0, nullable=False)
    data_downloads = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship(UserDB, backref="usage_metrics")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_usage_user"),
    )


