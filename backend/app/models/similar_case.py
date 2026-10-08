from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class SimilarCase(Base):
    __tablename__ = "similar_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    judgment_title: Mapped[str] = mapped_column(String(500), nullable=False)
    court: Mapped[str | None] = mapped_column(String(200), nullable=True)
    judgment_year: Mapped[str | None] = mapped_column(String(50), nullable=True)
    citation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevant_passage: Mapped[str | None] = mapped_column(Text, nullable=True)
    similarity_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    
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
    case: Mapped["Case"] = relationship(back_populates="similar_cases")
