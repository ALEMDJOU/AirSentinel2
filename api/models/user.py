import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional

from api.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    subscribed_city: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    is_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true"
    )
    last_alert_sent: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    fcm_token: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
