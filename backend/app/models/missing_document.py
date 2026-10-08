from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class MissingDocumentRecommendation(Base):
    __tablename__ = "missing_document_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    document_category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    document_name: Mapped[str] = mapped_column(String(500), nullable=False)
    
    requirement_level: Mapped[str] = mapped_column(String(50), nullable=False) # "potentially required", "recommended", "optional"
    
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    related_evidence_fact: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_legal_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    
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
    case: Mapped["Case"] = relationship(back_populates="missing_document_recommendations")
