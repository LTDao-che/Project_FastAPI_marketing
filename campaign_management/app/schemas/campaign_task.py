from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.campaign_task import TaskStatus, TaskPriority


class CampaignTaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class CampaignTaskCreate(CampaignTaskBase):
    pass


class CampaignTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class CampaignTaskOut(CampaignTaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    assignee_id: int | None
    status: TaskStatus
    created_at: datetime