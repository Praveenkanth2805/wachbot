# sample_data.py
from app.database import SessionLocal
from app.models import Category, Keyword, Response
from app.models.keyword import MatchType
from app.models.response import ResponseType

def insert_sample_data():
    db = SessionLocal()
    try:
        # Categories
        cat1 = Category(name="Greeting", description="Greeting messages")
        cat2 = Category(name="Pricing", description="Pricing inquiries")
        db.add_all([cat1, cat2])
        db.commit()

        # Keywords
        kw1 = Keyword(pattern="hello", match_type=MatchType.contains, priority=10, language="en", category=cat1)
        kw2 = Keyword(pattern="hi", match_type=MatchType.exact, priority=10, language="en", category=cat1)
        kw3 = Keyword(pattern="price", match_type=MatchType.contains, priority=20, language="en", category=cat2)
        kw4 = Keyword(pattern="cost", match_type=MatchType.contains, priority=20, language="en", category=cat2)
        kw5 = Keyword(pattern="website price", match_type=MatchType.contains, priority=100, language="en", category=cat2)
        db.add_all([kw1, kw2, kw3, kw4, kw5])
        db.commit()

        # Responses
        resp1 = Response(keyword=kw1, type=ResponseType.text, text="Hello! How can I help you?")
        resp2 = Response(keyword=kw2, type=ResponseType.text, text="Hi there! Welcome to ASC.")
        resp3 = Response(keyword=kw3, type=ResponseType.text, text="Our pricing starts at $99 per month.")
        resp4 = Response(keyword=kw4, type=ResponseType.text, text="The cost depends on the package. Please visit our website.")
        resp5 = Response(keyword=kw5, type=ResponseType.text, text="Website pricing is $199 per month for the premium plan.")
        db.add_all([resp1, resp2, resp3, resp4, resp5])
        db.commit()
        print("✅ Sample data inserted successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_data()