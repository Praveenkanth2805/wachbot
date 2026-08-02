from app.models import Category
from .base import BaseRepository
from sqlalchemy.orm import Session

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_by_name(self, name: str):
        return self.db.query(Category).filter(Category.name == name).first()