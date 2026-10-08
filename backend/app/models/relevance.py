from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class LegalRelevanceAnalysis(Base):
    __tablename__ = "legal_relevance_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    evidence_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evidence_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    fact_reference: Mapped[str] = mapped_column(Text, nullable=False)
    
    legal_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    relevance_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    relevance_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
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
    case: Mapped["Case"] = relationship(back_populates="legal_relevance_analyses")
    evidence: Mapped["EvidenceAnalysis"] = relationship(back_populates="legal_relevance_analyses")
