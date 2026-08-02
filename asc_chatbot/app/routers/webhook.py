from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat_engine import ChatEngine
from app.services.whatsapp import WhatsAppService
from app.core.config import settings
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
whatsapp = WhatsAppService()

@router.get("/webhook")
async def verify_webhook(request: Request):
    # WhatsApp verification
    query = request.query_params
    mode = query.get("hub.mode")
    token = query.get("hub.verify_token")
    challenge = query.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    logger.info(f"Webhook received: {body}")
    # Process incoming messages
    try:
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "text":
                        from_id = msg.get("from")
                        text = msg.get("text", {}).get("body", "")
                        # Process with chat engine
                        engine = ChatEngine(db)
                        result = engine.process_message(from_id, text)
                        # Send reply
                        if result["text"]:
                            await whatsapp.send_text(from_id, result["text"])
                        if result["media"]:
                            # Need to upload media to WhatsApp? For now just text.
                            pass
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
    return {"status": "ok"}