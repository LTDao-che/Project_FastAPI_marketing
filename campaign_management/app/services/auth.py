from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def register_user(db: Session, user_in: UserCreate):
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_user_token(user: User) -> Token:
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )