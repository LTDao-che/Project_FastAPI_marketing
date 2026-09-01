from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
from app.models.campaign import Campaign, CampaignMember, CampaignMemberRole
from app.schemas.campaign import CampaignUpdate


def get_campaign(db: Session, campaign_id: int):
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()


def get_campaigns_for_user(db: Session, user_id: int, search: Optional[str] = None):
    member_campaign_ids = db.query(CampaignMember.campaign_id).filter(CampaignMember.user_id == user_id)

    query = db.query(Campaign).filter(Campaign.is_deleted == False, or_(Campaign.owner_id == user_id, Campaign.id.in_(member_campaign_ids)))
    if search:
        query = query.filter(Campaign.name.ilike(f"%{search}%"))

    return query.all()


def create_campaign(db: Session, name: str, description: Optional[str], owner_id: int):
    campaign = Campaign(name=name, description=description, owner_id=owner_id)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    owner_member = CampaignMember(
        campaign_id=campaign.id,
        user_id=owner_id,
        role=CampaignMemberRole.OWNER
    )
    db.add(owner_member)
    db.commit()

    return campaign


def update_campaign(db: Session, campaign: Campaign, obj_in: CampaignUpdate):
    if obj_in.name is not None:
        campaign.name = obj_in.name
    if obj_in.description is not None:
        campaign.description = obj_in.description

    db.commit()
    db.refresh(campaign)
    return campaign


def delete_campaign(db: Session, campaign: Campaign):
    campaign.is_deleted = True
    campaign.deleted_at = datetime.now()
    db.commit()
    db.refresh(campaign)
    return campaign

def restore_campaign(db: Session, campaign: Campaign):
    campaign.is_deleted = False
    campaign.deleted_at = None
    db.commit()
    db.refresh(campaign)
    return campaign