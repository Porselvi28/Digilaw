from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class ActionPlan(Base):
    __tablename__ = "action_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    action_title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    action_category: Mapped[str] = mapped_column(String(100), nullable=False)
    
    required_documents: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_legal_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="action_plans")
