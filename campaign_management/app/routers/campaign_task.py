from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.campaign_task import TaskStatus, TaskPriority
from app.schemas.campaign_task import CampaignTaskCreate, CampaignTaskUpdate, CampaignTaskOut,CampaignTaskListOut
from app.services import campaign_task as task_service

router = APIRouter(tags=["Campaign Tasks"])


@router.post("/campaigns/{campaign_id}/campaign-tasks",response_model=CampaignTaskOut,status_code=status.HTTP_201_CREATED)
def create_campaign_task(campaign_id: int,task_in: CampaignTaskCreate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    task_service.require_campaign_member(db, campaign_id, current_user.id)

    assignee_id = getattr(task_in, "assignee_id", None)
    if assignee_id is not None:
        if not task_service.is_campaign_member(db, campaign_id, assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được gán việc không thuộc chiến dịch này"
            )

    return task_service.create_task(
        db=db,
        campaign_id=campaign_id,
        task_in=task_in,
        created_by=current_user.id
    )


@router.get("/campaigns/{campaign_id}/campaign-tasks",response_model=CampaignTaskListOut)
def list_campaign_tasks(campaign_id: int,status: Optional[TaskStatus] = Query(None, description="Lọc theo trạng thái"),priority: Optional[TaskPriority] = Query(None, description="Lọc theo mức độ ưu tiên"),assignee_id: Optional[int] = Query(None, description="Lọc theo người được gán"),search: Optional[str] = Query(None, description="Tìm kiếm theo title"),sort_by: str = Query("created_at", description="Sắp xếp theo: created_at | due_date"),sort_order: str = Query("desc", description="Thứ tự: asc | desc"),limit: int = Query(10, ge=1, le=100),offset: int = Query(0, ge=0),db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    task_service.require_campaign_member(db, campaign_id, current_user.id)

    tasks, total = task_service.get_tasks_by_campaign(
        db=db,
        campaign_id=campaign_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

    return {
        "data": tasks,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/campaign-tasks/{task_id}", response_model=CampaignTaskOut)
def get_campaign_task(task_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đầu việc"
        )

    task_service.require_campaign_member(db, task.campaign_id, current_user.id)
    return task


@router.patch("/campaign-tasks/{task_id}", response_model=CampaignTaskOut)
def update_campaign_task(task_id: int,task_in: CampaignTaskUpdate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đầu việc"
        )

    if not task_service.can_update_task(db, task, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật đầu việc này"
        )

    is_owner = task_service.is_campaign_owner(db, task.campaign_id, current_user.id)
    is_creator = task.created_by == current_user.id
    is_assignee_only = (task.assignee_id == current_user.id) and not is_owner and not is_creator

    update_data = task_in.model_dump(exclude_unset=True)

    if is_assignee_only and "assignee_id" in update_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thay đổi người được gán việc"
        )

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        new_assignee_id = update_data["assignee_id"]
        if not task_service.is_campaign_member(db, task.campaign_id, new_assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được gán việc mới không thuộc chiến dịch này"
            )

    return task_service.update_task(db, task, task_in)


@router.delete("/campaign-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign_task(task_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đầu việc"
        )

    if not task_service.can_delete_task(db, task, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa đầu việc này"
        )

    task_service.delete_task(db, task)
    return None