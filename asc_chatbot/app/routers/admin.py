from fastapi import APIRouter, Request, Depends, HTTPException, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import require_login, generate_csrf_token, validate_csrf, verify_password, get_password_hash
from app.core.config import settings
from app.models import User, Category, Keyword, Response, Media, ChatLog, UnansweredMessage, Version
from app.repositories import CategoryRepository, KeywordRepository, ResponseRepository, MediaRepository, ChatLogRepository, UnansweredRepository
from app.services.media_service import MediaService
from app.schemas import schemas
import os
from pathlib import Path
from sqlalchemy.sql import func

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Login
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="admin/login.html",
    context={
        "request": request
    }
)

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(User.username == username).first()

    if not user:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Invalid credentials"},
            status_code=401
        )

    if not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Invalid credentials"},
            status_code=401
        )

    request.session["user"] = user.username

    user.last_login = func.now()
    db.commit()

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )
    
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login")

# Dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_login(request)
    # Counts
    total_keywords = db.query(Keyword).count()
    total_categories = db.query(Category).count()
    total_unanswered = db.query(UnansweredMessage).filter(UnansweredMessage.is_resolved == False).count()
    recent_logs = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(request=request,name="admin/dashboard.html",  context={
        "total_keywords": total_keywords,
        "total_categories": total_categories,
        "total_unanswered": total_unanswered,
        "recent_logs": recent_logs,
    })

# Categories CRUD
@router.get("/categories", response_class=HTMLResponse)
async def categories_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    categories = db.query(Category).all()
    return templates.TemplateResponse(request=request,name="admin/categories.html", context={ "categories": categories})

@router.post("/categories")
async def create_category(request: Request, name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    require_login(request)
    # CSRF validation can be added
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    return RedirectResponse("/admin/categories", status_code=302)

@router.get("/categories/{id}/delete")
async def delete_category(id: int, db: Session = Depends(get_db)):
    # require login, csrf
    category = db.query(Category).filter(Category.id == id).first()
    if category:
        db.delete(category)
        db.commit()
    return RedirectResponse("/admin/categories", status_code=302)

# Keywords CRUD (simplified)
@router.get("/keywords", response_class=HTMLResponse)
async def keywords_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    keywords = db.query(Keyword).all()
    categories = db.query(Category).all()
    return templates.TemplateResponse(request=request,name="admin/keywords.html", context={ "keywords": keywords, "categories": categories})

@router.post("/keywords")
async def create_keyword(request: Request,
                         pattern: str = Form(...),
                         match_type: str = Form(...),
                         priority: int = Form(0),
                         language: str = Form("en"),
                         category_id: int = Form(None),
                         response_type: str = Form("text"),
                         response_text: str = Form(""),
                         db: Session = Depends(get_db)):
    require_login(request)
    keyword = Keyword(
        pattern=pattern,
        match_type=match_type,
        priority=priority,
        language=language,
        category_id=category_id if category_id else None
    )
    db.add(keyword)
    db.flush()
    # Add response
    resp = Response(keyword_id=keyword.id, type=response_type, text=response_text)
    db.add(resp)
    db.commit()
    return RedirectResponse("/admin/keywords", status_code=302)

# Media Library
@router.get("/media", response_class=HTMLResponse)
async def media_library(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    media_files = db.query(Media).all()
    return templates.TemplateResponse(request=request,name="admin/media.html", context={"media_files": media_files})

@router.post("/media/upload")
async def upload_media(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    require_login(request)
    media_service = MediaService(db)
    media = media_service.save_file(file)
    return RedirectResponse("/admin/media", status_code=302)

@router.get("/media/{id}/delete")
async def delete_media(id: int, db: Session = Depends(get_db)):
    # require login
    media_service = MediaService(db)
    media_service.delete_file(id)
    return RedirectResponse("/admin/media", status_code=302)

# Logs
@router.get("/logs", response_class=HTMLResponse)
async def chat_logs(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    logs = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(request=request,name="admin/logs.html", context={ "logs": logs})

# Unanswered
@router.get("/unanswered", response_class=HTMLResponse)
async def unanswered_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    unanswered = db.query(UnansweredMessage).filter(UnansweredMessage.is_resolved == False).all()
    return templates.TemplateResponse(request=request,name="admin/unanswered.html", context={ "unanswered": unanswered})

@router.post("/unanswered/{id}/resolve")
async def resolve_unanswered(id: int, db: Session = Depends(get_db)):
    # require login
    msg = db.query(UnansweredMessage).filter(UnansweredMessage.id == id).first()
    if msg:
        msg.is_resolved = True
        db.commit()
    return RedirectResponse(request=request,name="/admin/unanswered", status_code=302)

# Versions
@router.get("/versions", response_class=HTMLResponse)
async def versions_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    versions = db.query(Version).order_by(Version.changed_at.desc()).limit(50).all()
    return templates.TemplateResponse(request=request,name="admin/versions.html", context={ "versions": versions})

# Settings (simple)
@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    return templates.TemplateResponse(request=request,name="admin/settings.html", context={ "fallback_reply": settings.FALLBACK_REPLY})

@router.post("/settings")
async def update_settings(request: Request, fallback_reply: str = Form(...), db: Session = Depends(get_db)):
    require_login(request)
    # For simplicity, we just update env? Not recommended. We'll update config in memory.
    # In production, persist in DB settings table.
    settings.FALLBACK_REPLY = fallback_reply
    return RedirectResponse("/admin/settings", status_code=302)