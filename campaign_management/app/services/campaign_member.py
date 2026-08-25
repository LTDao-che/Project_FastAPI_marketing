from sqlalchemy.orm import Session, joinedload
from app.models.campaign import CampaignMember, CampaignMemberRole


def get_member(db: Session, campaign_id: int, user_id: int):
    return db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id,CampaignMember.user_id == user_id).first()


def get_members(db: Session, campaign_id: int):
    return db.query(CampaignMember).options(joinedload(CampaignMember.user)).filter(CampaignMember.campaign_id == campaign_id).all()


def add_member(db: Session, campaign_id: int, user_id: int, role: CampaignMemberRole = CampaignMemberRole.MEMBER):
    member = CampaignMember(
        campaign_id=campaign_id,
        user_id=user_id,
        role=role
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_member(db: Session, member: CampaignMember):
    db.delete(member)
    db.commit()


def count_owners(db: Session, campaign_id: int) -> int:
    return db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id,CampaignMember.role == CampaignMemberRole.OWNER).count()