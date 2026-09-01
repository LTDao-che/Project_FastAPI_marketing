from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.campaign import CampaignMemberRole


class CampaignBase(BaseModel):
    name: str
    description: str | None = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CampaignOut(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    is_deleted: bool = False  
    deleted_at: datetime | None = None
