from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.campaign import Campaign, CampaignMember, CampaignMemberRole
from app.models.campaign_task import CampaignTask, TaskStatus, TaskPriority
from app.core.security import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        admin = User(email="admin@demo.com", full_name="Admin Demo", password_hash=get_password_hash("admin123"), role=UserRole.ADMIN, is_active=True)
        user1 = User(email="user1@demo.com", full_name="User One", password_hash=get_password_hash("user123"), role=UserRole.USER, is_active=True)
        user2 = User(email="user2@demo.com", full_name="User Two", password_hash=get_password_hash("user123"), role=UserRole.USER, is_active=True)
        user3 = User(email="user3@demo.com", full_name="User Three", password_hash=get_password_hash("user123"), role=UserRole.USER, is_active=True)
        db.add_all([admin, user1, user2, user3])
        db.commit()
        for u in [admin, user1, user2, user3]:
            db.refresh(u)

        camp1 = Campaign(name="Tết 2026 Campaign", description="Chiến dịch Tết Nguyên Đán", owner_id=user1.id)
        camp2 = Campaign(name="Summer Sale 2026", description="Khuyến mãi mùa hè", owner_id=user2.id)
        db.add_all([camp1, camp2])
        db.commit()
        db.refresh(camp1); db.refresh(camp2)

        db.add_all([
            CampaignMember(campaign_id=camp1.id, user_id=user1.id, role=CampaignMemberRole.OWNER),
            CampaignMember(campaign_id=camp1.id, user_id=user2.id, role=CampaignMemberRole.MEMBER),
            CampaignMember(campaign_id=camp1.id, user_id=user3.id, role=CampaignMemberRole.MEMBER),
            CampaignMember(campaign_id=camp2.id, user_id=user2.id, role=CampaignMemberRole.OWNER),
            CampaignMember(campaign_id=camp2.id, user_id=user1.id, role=CampaignMemberRole.MEMBER),
        ])
        db.commit()

        db.add_all([
            CampaignTask(campaign_id=camp1.id, title="Thiết kế banner Tết", description="Banner 1080x1080px", status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH, due_date=datetime.now()+timedelta(days=7), assignee_id=user2.id, created_by=user1.id),
            CampaignTask(campaign_id=camp1.id, title="Viết content Facebook", description="5 bài post chuẩn SEO", status=TaskStatus.TODO, priority=TaskPriority.MEDIUM, due_date=datetime.now()+timedelta(days=5), assignee_id=user3.id, created_by=user1.id),
            CampaignTask(campaign_id=camp2.id, title="Chạy ads Google", description="Budget 10 triệu, target HCM", status=TaskStatus.TODO, priority=TaskPriority.HIGH, due_date=datetime.now()+timedelta(days=3), assignee_id=user1.id, created_by=user2.id),
        ])
        db.commit()

        print(" Seed dữ liệu thành công!")
        print("   Admin: admin@demo.com / admin123")
        print("   Users: user1@demo.com -> user3@demo.com / user123")
    except Exception as e:
        db.rollback()
        print(f" Lỗi seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()