from app.database import SessionLocal
from app.services.chat_engine import ChatEngine

db = SessionLocal()
engine = ChatEngine(db)
result = engine.process_message("test", "hi")
print("Reply:", result["text"])
print("Matched keyword:", result["matched_keyword"])