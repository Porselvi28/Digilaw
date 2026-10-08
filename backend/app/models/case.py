from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Case(Base):

    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    legal_domain: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="cases"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan"
    )

    evidence_analyses: Mapped[list["EvidenceAnalysis"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan"
    )

    legal_relevance_analyses: Mapped[list["LegalRelevanceAnalysis"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan"
    )

    missing_document_recommendations: Mapped[list["MissingDocumentRecommendation"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan"
    )

    similar_cases: Mapped[list["SimilarCase"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan"
    )

    action_plans: Mapped[list["ActionPlan"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="ActionPlan.sequence_order"
    )