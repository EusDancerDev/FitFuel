from typing import Dict
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, JSON, ForeignKey, String, Enum
import enum
from sqlalchemy.orm import relationship
from ..database import Base

class DeviceType(enum.Enum):
    APPLE_WATCH = "apple_watch"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    SAMSUNG = "samsung"

class WatchData(Base):
    __tablename__ = "watch_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Activity Data
    steps = Column(Integer, default=0)
    calories_burned = Column(Float, default=0.0)
    distance = Column(Float, default=0.0)  # in meters
    
    # Heart Rate Data
    heart_rate_avg = Column(Float)
    heart_rate_max = Column(Float)
    heart_rate_min = Column(Float)
    heart_rate_resting = Column(Float)
    
    # Activity Minutes
    sedentary_minutes = Column(Integer, default=0)
    lightly_active_minutes = Column(Integer, default=0)
    fairly_active_minutes = Column(Integer, default=0)
    very_active_minutes = Column(Integer, default=0)
    
    # Sleep Data
    sleep_duration = Column(Integer)  # in minutes
    sleep_efficiency = Column(Float)  # percentage
    sleep_stages = Column(JSON)  # {"deep": minutes, "light": minutes, "rem": minutes, "awake": minutes}
    
    # Raw Data
    raw_data = Column(JSON)  # Store original device data
    
    # Relationship
    user = relationship("User", back_populates="watch_data")
    
    def to_dict(self) -> Dict:
        """Convert watch data model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_type": self.device_type.value,
            "timestamp": self.timestamp.isoformat(),
            "activity": {
                "steps": self.steps,
                "calories_burned": self.calories_burned,
                "distance": self.distance,
                "active_minutes": {
                    "sedentary": self.sedentary_minutes,
                    "lightly_active": self.lightly_active_minutes,
                    "fairly_active": self.fairly_active_minutes,
                    "very_active": self.very_active_minutes
                }
            },
            "heart_rate": {
                "average": self.heart_rate_avg,
                "max": self.heart_rate_max,
                "min": self.heart_rate_min,
                "resting": self.heart_rate_resting
            },
            "sleep": {
                "duration": self.sleep_duration,
                "efficiency": self.sleep_efficiency,
                "stages": self.sleep_stages
            },
            "raw_data": self.raw_data
        } 