from sqlalchemy.orm import Session

from app.models import User
from app.core.config import settings
from app.core.security import get_password_hash


def create_default_admin(db: Session):
    admin = (
        db.query(User)
        .filter(User.username == settings.ADMIN_USERNAME)
        .first()
    )

    if admin:
        print("✓ Admin already exists")
        return

    admin = User(
        username=settings.ADMIN_USERNAME,
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD_HASH),
    )

    db.add(admin)
    db.commit()

    print("✓ Default admin created")