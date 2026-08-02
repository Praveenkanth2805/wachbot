from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.routers import webhook_router, admin_router, bot_router
from app.database import engine, Base
import logging
import os

# Create logs directory if not exists
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(settings.LOG_DIR, 'app.log')),
        logging.StreamHandler()
    ]
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(webhook_router)
app.include_router(admin_router)
app.include_router(bot_router)

@app.get("/")
async def root():
    return {"message": "ASC Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)