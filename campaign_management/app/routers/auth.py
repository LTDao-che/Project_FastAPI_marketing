from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token, RefreshTokenIn
from app.services.auth import get_user_by_email, register_user, authenticate_user, create_user_token
from app.core.security import verify_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    return register_user(db, user_in)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email hoặc mật khẩu không đúng")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")
    return create_user_token(user)

@router.post("/refresh", response_model=Token)
def refresh_token(body: RefreshTokenIn, db: Session = Depends(get_db)):
    email = verify_refresh_token(body.refresh_token)
    if not email:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn")
    
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User không hợp lệ")
    
    return create_user_token(user)