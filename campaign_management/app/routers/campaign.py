from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.models.campaign import CampaignMemberRole
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignOut
from app.schemas.campaign_member import CampaignMemberOut
from app.dependencies.auth import get_current_user
from app.services.campaign import (
    get_campaign,
    get_campaigns_for_user,
    create_campaign as create_campaign_svc,   
    update_campaign as update_campaign_svc,
    delete_campaign as delete_campaign_svc,
    restore_campaign as restore_campaign_svc, 
)
from app.services.campaign_member import (
    get_member,
    get_members,
    add_member as add_member_svc,     
    remove_member as remove_member_svc,
    count_owners,
    count_member
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("/", response_model=list[CampaignOut])
def list_campaigns(search: Optional[str] = Query(None, description="Tìm theo tên chiến dịch"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_campaigns_for_user(db, current_user.id, search)


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_campaign_svc(
        db,
        name=campaign_in.name,
        description=campaign_in.description,
        owner_id=current_user.id
    )


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign_detail(campaign_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch")

    if campaign.owner_id != current_user.id:
        member = get_member(db, campaign_id, current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xem chiến dịch này")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignOut)
def update_campaign(campaign_id: int, campaign_in: CampaignUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch")

    if campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ owner mới được sửa chiến dịch")

    return update_campaign_svc(db, campaign, campaign_in)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch")

    if campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ owner mới được xóa chiến dịch")

    delete_campaign_svc(db, campaign)
    return None


@router.post("/{campaign_id}/restore", response_model=CampaignOut)
def restore_campaign(campaign_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)             
    if not campaign or not campaign.is_deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch đã xóa")
    
    if campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ owner mới được khôi phục")
    
    campaign = restore_campaign_svc(db, campaign)       
    campaign.total_members = count_member(db, campaign_id)
    return campaign


@router.get("/{campaign_id}/members", response_model=list[CampaignMemberOut])
def list_members(campaign_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch")

    if campaign.owner_id != current_user.id:
        member = get_member(db, campaign_id, current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xem")

    members = get_members(db, campaign_id)

    return [
        CampaignMemberOut(
            user_id=m.user_id,
            email=m.user.email,
            full_name=m.user.full_name,
            role=m.role,
            joined_at=m.joined_at
        )
        for m in members
    ]


@router.post("/{campaign_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(campaign_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch")

    if campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ owner mới được thêm thành viên")

    existing = get_member(db, campaign_id, user_id)
    if existing:
        raise HTTPException(status_code=400, detail="User đã là thành viên của chiến dịch")

    add_member_svc(db, campaign_id, user_id)
    return {"message": "Thêm thành viên thành công"}


@router.delete("/{campaign_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(campaign_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy chiến dịch")

    if campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ owner mới được xóa thành viên")

    member = get_member(db, campaign_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

    if member.role == CampaignMemberRole.OWNER:
        owner_count = count_owners(db, campaign_id)
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Không thể xóa owner cuối cùng")

    remove_member_svc(db, member)
    return None