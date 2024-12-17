from typing import Dict, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
import enum
from ..database import Base

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class ActivityLevel(enum.Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

class DietaryPreference(enum.Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Personal Information
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(DateTime)
    gender = Column(Enum(Gender))
    
    # Physical Attributes
    height = Column(Integer)  # in centimeters
    weight = Column(Integer)  # in grams
    activity_level = Column(Enum(ActivityLevel))
    
    # Dietary Information
    dietary_preference = Column(Enum(DietaryPreference))
    allergies = Column(JSON, default=list)
    restrictions = Column(JSON, default=list)
    
    # Preferences and Settings
    meal_times = Column(JSON, default=dict)  # {"breakfast": "08:00", "lunch": "13:00", ...}
    notification_preferences = Column(JSON, default=dict)
    app_settings = Column(JSON, default=dict)
    
    # Connected Devices
    connected_watch = Column(JSON, nullable=True)  # {"device_type": "apple_watch", "device_id": "..."}
    
    # Statistics and Tracking
    meal_stats = Column(JSON, default=dict)
    compliance_stats = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict:
        """Convert user model to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "personal_info": {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
                "gender": self.gender.value if self.gender else None
            },
            "physical_info": {
                "height": self.height,
                "weight": self.weight,
                "activity_level": self.activity_level.value if self.activity_level else None
            },
            "dietary_info": {
                "preference": self.dietary_preference.value if self.dietary_preference else None,
                "allergies": self.allergies,
                "restrictions": self.restrictions
            },
            "preferences": {
                "meal_times": self.meal_times,
                "notifications": self.notification_preferences,
                "app_settings": self.app_settings
            },
            "connected_watch": self.connected_watch,
            "statistics": {
                "meal_stats": self.meal_stats,
                "compliance_stats": self.compliance_stats
            },
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "last_login": self.last_login.isoformat() if self.last_login else None
            }
        }

    def update(self, data: Dict) -> None:
        """Update user data"""
        for key, value in data.items():
            if hasattr(self, key):
                if key in ["gender", "activity_level", "dietary_preference"]:
                    # Handle enum fields
                    if value is not None:
                        enum_class = type(getattr(self, key))
                        setattr(self, key, enum_class(value))
                elif key in ["date_of_birth", "last_login"]:
                    # Handle datetime fields
                    if value is not None:
                        setattr(self, key, datetime.fromisoformat(value))
                else:
                    setattr(self, key, value)

    def calculate_daily_calories(self) -> int:
        """Calculate daily caloric needs"""
        if not all([self.weight, self.height, self.date_of_birth, self.gender, self.activity_level]):
            return 0

        age = (datetime.now() - self.date_of_birth).days // 365
        
        # Base Metabolic Rate (BMR) using Mifflin-St Jeor Equation
        if self.gender == Gender.MALE:
            bmr = (10 * self.weight/1000) + (6.25 * self.height) - (5 * age) + 5
        else:
            bmr = (10 * self.weight/1000) + (6.25 * self.height) - (5 * age) - 161

        # Activity multiplier
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTREMELY_ACTIVE: 1.9
        }

        return int(bmr * activity_multipliers[self.activity_level])

    def get_macro_distribution(self) -> Dict[str, float]:
        """Get recommended macro distribution based on dietary preference"""
        base_distribution = {
            "protein": 0.3,
            "carbs": 0.4,
            "fats": 0.3
        }

        if self.dietary_preference == DietaryPreference.KETO:
            return {
                "protein": 0.3,
                "carbs": 0.05,
                "fats": 0.65
            }
        elif self.dietary_preference == DietaryPreference.VEGAN:
            return {
                "protein": 0.25,
                "carbs": 0.5,
                "fats": 0.25
            }

        return base_distribution 