from fastapi import FastAPI, HTTPException 
from app.core.config import get_settings
from app.db.database import engine, Base
from app.models.campaign import Campaign, CampaignMember
from app.models.campaign_task import CampaignTask
from app.models.user import User
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import http_exception_handler, validation_exception_handler,generic_exception_handler
from app.routers import auth, users, campaign

Base.metadata.create_all(engine)

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug = True)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get('/')
def start():
    return {
        "message": "Server đang hoạt động"
    }

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(campaign.router)