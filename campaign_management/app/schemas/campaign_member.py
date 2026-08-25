from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.campaign import CampaignMemberRole

class CampaignMemberCreate(BaseModel):
    user_id: int
    role: CampaignMemberRole = CampaignMemberRole.MEMBER


class CampaignMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: str
    full_name: str
    role: CampaignMemberRole
    joined_at: datetime