from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class EvidenceAnalysis(Base):
    __tablename__ = "evidence_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    
    # Store the structured Gemini extraction result here
    facts: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    
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
    document: Mapped["Document"] = relationship(back_populates="evidence_analyses")
    case: Mapped["Case"] = relationship(back_populates="evidence_analyses")
    legal_relevance_analyses: Mapped[list["LegalRelevanceAnalysis"]] = relationship(
        back_populates="evidence",
        cascade="all, delete-orphan"
    )
