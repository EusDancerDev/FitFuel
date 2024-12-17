from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from ...database.models import User, Meal, MealPreference
from ...config import settings
from ..ai.llm_manager import LLMManager

logger = logging.getLogger(__name__)

class MenuGenerator:
    def __init__(self, db_session, llm_manager: LLMManager):
        self.db = db_session
        self.llm = llm_manager
        self.menu_validity_days = settings.MENU_VALIDITY_DAYS
        self.max_retries = 3

    async def generate_menu(
        self,
        user_id: int,
        days: int = 7,
        preferences: Optional[Dict] = None
    ) -> Dict:
        """Generate personalized menu for specified days"""
        try:
            # Get user data and preferences
            user = await self._get_user_data(user_id)
            user_preferences = preferences or user.dietary_preferences

            # Get meal history for context
            meal_history = await self._get_meal_history(user_id)

            # Generate menu using LLM
            menu_result = await self._generate_with_llm(
                user,
                meal_history,
                user_preferences,
                days
            )

            if menu_result["success"]:
                # Store generated menu
                await self._store_menu(user_id, menu_result["menu"])
                
                return {
                    "success": True,
                    "menu": menu_result["menu"],
                    "valid_until": datetime.now() + timedelta(days=self.menu_validity_days)
                }
            else:
                raise ValueError(menu_result["error"])

        except Exception as e:
            logger.error(f"Error generating menu: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_user_data(self, user_id: int) -> User:
        """Get user data including preferences and restrictions"""
        try:
            user = await self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            raise

    async def _get_meal_history(self, user_id: int) -> List[Dict]:
        """Get recent meal history for context"""
        try:
            meals = await self.db.query(Meal).filter(
                Meal.user_id == user_id
            ).order_by(
                Meal.consumed_at.desc()
            ).limit(30).all()
            
            return [meal.to_dict() for meal in meals]
        except Exception as e:
            logger.error(f"Error getting meal history: {str(e)}")
            raise

    async def _generate_with_llm(
        self,
        user: User,
        meal_history: List[Dict],
        preferences: Dict,
        days: int
    ) -> Dict:
        """Generate menu using LLM"""
        try:
            prompt = self._create_menu_prompt(
                user,
                meal_history,
                preferences,
                days
            )

            for attempt in range(self.max_retries):
                result = await self.llm.process_request(
                    prompt=prompt,
                    context={
                        "user_data": user.to_dict(),
                        "meal_history": meal_history,
                        "preferences": preferences
                    }
                )

                if self._validate_menu(result.get("menu", {})):
                    return {
                        "success": True,
                        "menu": result["menu"]
                    }
                else:
                    logger.warning(f"Invalid menu generated, attempt {attempt + 1}")

            raise ValueError("Failed to generate valid menu")

        except Exception as e:
            logger.error(f"Error in LLM menu generation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _create_menu_prompt(
        self,
        user: User,
        meal_history: List[Dict],
        preferences: Dict,
        days: int
    ) -> str:
        """Create prompt for menu generation"""
        return f"""Generate a {days}-day menu plan with the following requirements:

User Profile:
- Age: {user.age}
- Gender: {user.gender}
- Activity Level: {user.activity_level}
- Dietary Preferences: {preferences}
- Allergies/Restrictions: {user.restrictions}

Recent Meal History:
{self._format_meal_history(meal_history)}

Requirements:
1. Include 3 main meals and 2 snacks per day
2. Follow dietary preferences and restrictions
3. Maintain variety across days
4. Include nutritional information per meal
5. Consider user's activity level
6. Avoid recently consumed meals
7. Include preparation difficulty level
8. Estimate preparation time
9. List main ingredients

Format response as structured JSON."""

    def _format_meal_history(self, meal_history: List[Dict]) -> str:
        """Format meal history for prompt"""
        recent_meals = meal_history[:10]  # Last 10 meals
        return "\n".join([
            f"- {meal['consumed_at']}: {meal['meal_type']} - {meal['items']}"
            for meal in recent_meals
        ])

    def _validate_menu(self, menu: Dict) -> bool:
        """Validate generated menu structure and content"""
        try:
            required_fields = [
                "days",
                "meals_per_day",
                "daily_menus"
            ]

            if not all(field in menu for field in required_fields):
                return False

            for day in menu["daily_menus"]:
                if not self._validate_daily_menu(day):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating menu: {str(e)}")
            return False

    def _validate_daily_menu(self, daily_menu: Dict) -> bool:
        """Validate single day menu structure"""
        required_meals = [
            "breakfast",
            "morning_snack",
            "lunch",
            "afternoon_snack",
            "dinner"
        ]

        try:
            if not all(meal in daily_menu for meal in required_meals):
                return False

            for meal in required_meals:
                if not self._validate_meal(daily_menu[meal]):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating daily menu: {str(e)}")
            return False

    def _validate_meal(self, meal: Dict) -> bool:
        """Validate single meal structure"""
        required_fields = [
            "name",
            "ingredients",
            "nutritional_info",
            "preparation_time",
            "difficulty"
        ]

        return all(field in meal for field in required_fields)

    async def _store_menu(self, user_id: int, menu: Dict) -> None:
        """Store generated menu in database"""
        try:
            # Implementation for storing menu
            pass
        except Exception as e:
            logger.error(f"Error storing menu: {str(e)}")
            raise 