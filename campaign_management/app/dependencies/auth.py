from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:

    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token không hợp lệ hoặc đã hết hạn",headers={"WWW-Authenticate": "Bearer"},)
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token không chứa thông tin người dùng",headers={"WWW-Authenticate": "Bearer"},)
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Không tìm thấy người dùng",headers={"WWW-Authenticate": "Bearer"},)
    
    if not user.is_active:
        raise HTTPException(
status_code=status.HTTP_403_FORBIDDEN,detail="Tài khoản đã bị khóa")
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )
    return current_user