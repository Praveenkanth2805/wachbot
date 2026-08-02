# fix_response.py
from app.database import SessionLocal
from app.models import Keyword, Response
from app.models.response import ResponseType

db = SessionLocal()
kw = db.query(Keyword).filter(Keyword.pattern == "hi").first()
if kw:
    # If there is at least one response, update the first one
    if kw.responses:
        resp = kw.responses[0]
        resp.type = ResponseType.text
        resp.text = "Hi there! Welcome to ASC."
        resp.media_id = None
        db.commit()
        print("✅ Updated first response for 'hi' to text.")
    else:
        # Create a new one
        resp = Response(keyword_id=kw.id, type=ResponseType.text, text="Hi there! Welcome to ASC.")
        db.add(resp)
        db.commit()
        print("✅ Created new text response for 'hi'.")
else:
    print("❌ Keyword 'hi' not found.")
db.close()