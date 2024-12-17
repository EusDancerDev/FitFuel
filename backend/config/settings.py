from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str] = None
    
    # AI Service settings
    OPENAI_API_KEY: str
    VISION_API_KEY: str
    
    # Application settings
    MENU_VALIDITY_DAYS: int = 7
    NOTIFICATION_COOLDOWN_MINUTES: int = 30
    MAX_DAILY_NOTIFICATIONS: int = 10
    MEAL_TRACKING_WINDOW: int = 30
    MEAL_SIMILARITY_THRESHOLD: float = 0.8
    
    class Config:
        env_file = ".env"

settings = Settings() 