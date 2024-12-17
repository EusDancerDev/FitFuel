from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..connection import Base

class Menu(Base):
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meals = Column(JSON)
    # Additional fields 