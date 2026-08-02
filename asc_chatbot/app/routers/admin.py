from fastapi import APIRouter, Request, Depends, HTTPException, Form, File, UploadFile, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from app.database import get_db
from app.core.security import require_login, generate_csrf_token, verify_password
from app.core.config import settings
from app.models import User, Category, Keyword, Response, Media, ChatLog, UnansweredMessage, Version
from app.services.media_service import MediaService
import urllib.parse

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# ---------- Login ----------
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request,name="admin/login.html", context={})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request=request,name=
            "admin/login.html",
            context={"error": "Invalid credentials"},
            status_code=401
        )
    request.session["user"] = user.username
    user.last_login = func.now()
    db.commit()
    return RedirectResponse("/admin/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login")

# ---------- Dashboard ----------
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    total_keywords = db.query(Keyword).count()
    total_categories = db.query(Category).count()
    total_unanswered = db.query(UnansweredMessage).filter(UnansweredMessage.is_resolved == False).count()
    recent_logs = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(request=request,name="admin/dashboard.html", context={
        "total_keywords": total_keywords,
        "total_categories": total_categories,
        "total_unanswered": total_unanswered,
        "recent_logs": recent_logs,
    })

# ---------- Categories ----------
@router.get("/categories", response_class=HTMLResponse)
async def categories_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    categories = db.query(Category).all()
    return templates.TemplateResponse(request=request,name="admin/categories.html", context={ "categories": categories})

@router.post("/categories")
async def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    require_login(request)
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    return RedirectResponse("/admin/categories?msg=Category created successfully", status_code=302)

@router.get("/categories/{id}/delete")
async def delete_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()
    if category:
        db.delete(category)
        db.commit()
    return RedirectResponse("/admin/categories?msg=Category deleted successfully", status_code=302)

# ---------- Keywords ----------
@router.get("/keywords", response_class=HTMLResponse)
async def keywords_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    keywords = db.query(Keyword).options(joinedload(Keyword.responses)).all()
    categories = db.query(Category).all()
    pattern = request.query_params.get("pattern", "")
    return templates.TemplateResponse(request=request,name="admin/keywords.html", context={
        "keywords": keywords,
        "categories": categories,
        "pattern": pattern, 
    })

@router.post("/keywords")
async def create_keyword(
    request: Request,
    pattern: str = Form(...),
    match_type: str = Form(...),
    priority: int = Form(0),
    language: str = Form("en"),
    category_id: int = Form(None),
    response_type: str = Form("text"),
    response_text: str = Form(""),
    response_media_id: int = Form(None),
    db: Session = Depends(get_db)
):
    username = require_login(request)
    keyword = Keyword(
        pattern=pattern,
        match_type=match_type,
        priority=priority,
        language=language,
        category_id=category_id if category_id else None
    )
    db.add(keyword)
    db.flush()

    resp = Response(
        keyword_id=keyword.id,
        type=response_type,
        text=response_text if response_text else None,
        media_id=response_media_id if response_media_id else None
    )
    db.add(resp)
    db.commit()

    # Version history
    user = db.query(User).filter(User.username == username).first()
    version = Version(
        keyword_id=keyword.id,
        changed_by=user.id if user else None,
        new_text=response_text if response_text else None,
        new_media_id=response_media_id if response_media_id else None
    )
    db.add(version)
    db.commit()

    return RedirectResponse("/admin/keywords?msg=Keyword created successfully", status_code=302)

@router.get("/keywords/{id}/edit", response_class=HTMLResponse)
async def edit_keyword_page(request: Request, id: int, db: Session = Depends(get_db)):
    require_login(request)
    keyword = db.query(Keyword).options(joinedload(Keyword.responses)).filter(Keyword.id == id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    categories = db.query(Category).all()
    return templates.TemplateResponse(request=request,name="admin/keyword_edit.html", context={
        "keyword": keyword,
        "categories": categories,
        "csrf_token": generate_csrf_token(request),
    })

@router.post("/keywords/{id}/edit")
async def update_keyword(
    request: Request,
    id: int,
    pattern: str = Form(...),
    match_type: str = Form(...),
    priority: int = Form(0),
    language: str = Form("en"),
    is_active: bool = Form(False),
    category_id: int = Form(None),
    response_type: str = Form("text"),
    response_text: str = Form(""),
    response_media_id: int = Form(None),
    db: Session = Depends(get_db)
):
    username = require_login(request)

    keyword = db.query(Keyword).options(joinedload(Keyword.responses)).filter(Keyword.id == id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # Capture old values for versioning
    old_text = keyword.responses[0].text if keyword.responses else None
    old_media_id = keyword.responses[0].media_id if keyword.responses else None

    # Update keyword fields
    keyword.pattern = pattern
    keyword.match_type = match_type
    keyword.priority = priority
    keyword.language = language
    keyword.is_active = is_active
    keyword.category_id = category_id if category_id else None

    # Update first response
    if keyword.responses:
        resp = keyword.responses[0]
    else:
        resp = Response(keyword_id=keyword.id)
        db.add(resp)

    resp.type = response_type
    resp.text = response_text if response_text else None
    resp.media_id = response_media_id if response_media_id else None

    db.commit()

    # Log version
    user = db.query(User).filter(User.username == username).first()
    version = Version(
        keyword_id=keyword.id,
        changed_by=user.id if user else None,
        old_text=old_text,
        new_text=response_text if response_text else None,
        old_media_id=old_media_id,
        new_media_id=response_media_id if response_media_id else None
    )
    db.add(version)
    db.commit()

    return RedirectResponse("/admin/keywords?msg=Keyword updated successfully", status_code=302)

@router.get("/keywords/{id}/delete")
async def delete_keyword(request: Request, id: int, db: Session = Depends(get_db)):
    require_login(request)
    keyword = db.query(Keyword).filter(Keyword.id == id).first()
    if keyword:
        db.delete(keyword)
        db.commit()
    return RedirectResponse("/admin/keywords?msg=Keyword deleted successfully", status_code=302)

# ---------- Media ----------
@router.get("/media", response_class=HTMLResponse)
async def media_library(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    media_files = db.query(Media).all()
    return templates.TemplateResponse(request=request,name="admin/media.html",context= { "media_files": media_files})

@router.post("/media/upload")
async def upload_media(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    require_login(request)
    media_service = MediaService(db)
    media_service.save_file(file)
    return RedirectResponse("/admin/media?msg=Media uploaded successfully", status_code=302)

@router.get("/media/{id}/delete")
async def delete_media(id: int, db: Session = Depends(get_db)):
    media_service = MediaService(db)
    media_service.delete_file(id)
    return RedirectResponse("/admin/media?msg=Media deleted successfully", status_code=302)

# ---------- Logs ----------
@router.get("/logs", response_class=HTMLResponse)
async def chat_logs(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    logs = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(request=request,name="admin/logs.html", context={ "logs": logs})

# ---------- Unanswered ----------
@router.get("/unanswered", response_class=HTMLResponse)
async def unanswered_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    unanswered = db.query(UnansweredMessage).filter(UnansweredMessage.is_resolved == False).all()
    return templates.TemplateResponse(request=request,name="admin/unanswered.html", context={"unanswered": unanswered})

@router.post("/unanswered/{id}/resolve")
async def resolve_unanswered(id: int, db: Session = Depends(get_db)):
    msg = db.query(UnansweredMessage).filter(UnansweredMessage.id == id).first()
    if msg:
        pattern = msg.message
        msg.is_resolved = True
        db.commit()
        # Encode pattern for URL
        encoded_pattern = urllib.parse.quote(pattern)
        return RedirectResponse(
            f"/admin/keywords?msg=Unanswered message resolved. Create a keyword for this pattern.&pattern={encoded_pattern}",
            status_code=302
        )
    return RedirectResponse("/admin/unanswered?msg=Message not found", status_code=302)

# ---------- Versions ----------
@router.get("/versions", response_class=HTMLResponse)
async def versions_list(request: Request, db: Session = Depends(get_db)):
    require_login(request)
    versions = db.query(Version).order_by(Version.changed_at.desc()).limit(50).all()
    return templates.TemplateResponse(request=request,name="admin/versions.html", context={"versions": versions})

# ---------- Settings ----------
@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    require_login(request)
    return templates.TemplateResponse(request=request,name="admin/settings.html", context={  
        "fallback_reply": settings.FALLBACK_REPLY
    })

@router.post("/settings")
async def update_settings(request: Request, fallback_reply: str = Form(...)):
    require_login(request)
    settings.FALLBACK_REPLY = fallback_reply
    return RedirectResponse("/admin/settings?msg=Settings updated", status_code=302)