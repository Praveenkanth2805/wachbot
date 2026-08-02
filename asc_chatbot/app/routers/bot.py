from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat_engine import ChatEngine
from app.core.config import settings

router = APIRouter(prefix="/bot", tags=["bot"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def bot_page(request: Request):
    return templates.TemplateResponse(request= request,name="bot.html", context={})

@router.post("/message")
async def bot_message(request: Request, message: str = Form(...), db: Session = Depends(get_db)):
    engine = ChatEngine(db)
    result = engine.process_message("test_user", message)
    reply = result.get("text", settings.FALLBACK_REPLY)
    media = result.get("media")
    media_url = None
    media_type = None
    if media:
        # Serve media from /uploads/ (we'll mount the static dir)
        media_url = f"/uploads/{media.file_path}"
        media_type = media.mime_type
    return JSONResponse({
        "reply": reply,
        "media_url": media_url,
        "media_type": media_type,
        "media_id": media.id if media else None
    })