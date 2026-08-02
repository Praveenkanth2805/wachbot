from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat_engine import ChatEngine
from app.core.config import settings

router = APIRouter(prefix="/bot", tags=["bot"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def bot_page(request: Request):
    return templates.TemplateResponse("bot.html", context={"request": request})

@router.post("/message")
async def bot_message(request: Request, message: str = Form(...), db: Session = Depends(get_db)):
    engine = ChatEngine(db)
    result = engine.process_message("test_user", message)
    return {"reply": result.get("text", settings.FALLBACK_REPLY)}