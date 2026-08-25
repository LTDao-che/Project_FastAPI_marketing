from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.dependencies.auth import get_current_user, require_admin
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserOut])
def list_users(search: Optional[str] = Query(None, description="Tìm theo tên hoặc email"),is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái"),db: Session = Depends(get_db),admin: User = Depends(require_admin)):
    return user_service.search_users(db, search=search, is_active=is_active)