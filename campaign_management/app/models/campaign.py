from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class CampaignMemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    owner = relationship("User", back_populates="owned_campaigns")
    members = relationship("CampaignMember", back_populates="campaign")
    tasks = relationship("CampaignTask", back_populates="campaign")


class CampaignMember(Base):
    __tablename__ = "campaign_members"

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(CampaignMemberRole), default=CampaignMemberRole.MEMBER, nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    campaign = relationship("Campaign", back_populates="members")
    user = relationship("User", back_populates="campaign_memberships")