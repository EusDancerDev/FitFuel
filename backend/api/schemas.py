from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: str
    name: str
    
class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str
    
class MealBase(BaseModel):
    name: str
    ingredients: List[str]
    nutritional_info: Dict
    preparation_time: int
    difficulty: str
    
class MealCreate(MealBase):
    meal_type: str
    scheduled_time: datetime 