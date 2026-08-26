from sqlalchemy.orm import Session
from typing import Optional
from app.models.campaign_task import CampaignTask, TaskStatus, TaskPriority
from app.schemas.campaign_task import CampaignTaskCreate, CampaignTaskUpdate
from app.models.campaign import CampaignMember, CampaignMemberRole
from fastapi import HTTPException, status

def get_task(db: Session, task_id: int):
    return db.query(CampaignTask).filter(CampaignTask.id == task_id).first()

def get_tasks_by_campaign(db: Session,campaign_id: int,status: Optional[TaskStatus] = None,priority: Optional[TaskPriority] = None,assignee_id: Optional[int] = None,search: Optional[str] = None,sort_by: str = "created_at",sort_order: str = "desc",limit: int = 10,offset: int = 0):
    query = db.query(CampaignTask).filter(CampaignTask.campaign_id == campaign_id)

    if status:
        query = query.filter(CampaignTask.status == status)
    if priority:
        query = query.filter(CampaignTask.priority == priority)
    if assignee_id:
        query = query.filter(CampaignTask.assignee_id == assignee_id)
    if search:
        query = query.filter(CampaignTask.title.ilike(f"%{search}%"))

    column = getattr(CampaignTask, sort_by, CampaignTask.created_at)
    if sort_order == "desc":
        column = column.desc()
    query = query.order_by(column)

    total = query.count()

    tasks = query.offset(offset).limit(limit).all()

    return tasks, total


def create_task(db: Session, campaign_id: int, task_in: CampaignTaskCreate, created_by: int):
    db_task = CampaignTask(campaign_id=campaign_id,title=task_in.title,description=task_in.description,priority=task_in.priority,due_date=task_in.due_date,assignee_id=task_in.assignee_id,created_by=created_by,status=TaskStatus.TODO)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task: CampaignTask, task_in: CampaignTaskUpdate):
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: CampaignTask):
    db.delete(task)
    db.commit()


def get_member(db: Session, campaign_id: int, user_id: int) -> Optional[CampaignMember]:
    return db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id,CampaignMember.user_id == user_id).first()

def is_campaign_member(db: Session, campaign_id: int, user_id: int) -> bool:
    return get_member(db, campaign_id, user_id) is not None

def is_campaign_owner(db: Session, campaign_id: int, user_id: int) -> bool:
    member = get_member(db, campaign_id, user_id)
    return member is not None and member.role == CampaignMemberRole.OWNER


def require_campaign_member(db: Session, campaign_id: int, user_id: int):
    if not is_campaign_member(db, campaign_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không thuộc chiến dịch này"
        )


def can_update_task(db: Session, task: CampaignTask, user_id: int) -> bool:
    if is_campaign_owner(db, task.campaign_id, user_id):
        return True
    if task.created_by == user_id:
        return True
    if task.assignee_id == user_id:
        return True
    return False


def can_delete_task(db: Session, task: CampaignTask, user_id: int) -> bool:
    if is_campaign_owner(db, task.campaign_id, user_id):
        return True
    if task.created_by == user_id:
        return True
    return False