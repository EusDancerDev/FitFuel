from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from ...database.models import User, Meal, MealType
from ...config import settings
from ...utils.exceptions import MealTrackingError

logger = logging.getLogger(__name__)

class MealTracker:
    def __init__(self, db_session):
        self.db = db_session
        self.tracking_window = settings.MEAL_TRACKING_WINDOW
        self.similarity_threshold = settings.MEAL_SIMILARITY_THRESHOLD

    async def track_meal(
        self,
        user_id: int,
        meal_data: Dict,
        meal_type: MealType,
        location: str = "home"
    ) -> Dict:
        """Track a new meal for the user"""
        try:
            # Validate meal timing
            if not self._is_valid_meal_time(meal_type):
                raise MealTrackingError(f"Invalid time for {meal_type}")

            # Create meal record
            meal = await self._create_meal_record(
                user_id,
                meal_data,
                meal_type,
                location
            )

            # Calculate compliance
            compliance = await self._calculate_compliance(
                meal,
                meal_data.get("expected_meal")
            )

            # Update user statistics
            await self._update_user_stats(user_id, compliance)

            return {
                "success": True,
                "meal_id": meal.id,
                "compliance": compliance,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error tracking meal: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _is_valid_meal_time(self, meal_type: MealType) -> bool:
        """Check if current time is valid for meal type"""
        current_time = datetime.now().time()
        
        meal_windows = {
            MealType.BREAKFAST: (
                datetime.strptime("06:00", "%H:%M").time(),
                datetime.strptime("10:00", "%H:%M").time()
            ),
            MealType.LUNCH: (
                datetime.strptime("12:00", "%H:%M").time(),
                datetime.strptime("15:00", "%H:%M").time()
            ),
            MealType.DINNER: (
                datetime.strptime("18:00", "%H:%M").time(),
                datetime.strptime("22:00", "%H:%M").time()
            )
        }

        if meal_type not in meal_windows:
            return True  # For snacks or other meal types

        start_time, end_time = meal_windows[meal_type]
        return start_time <= current_time <= end_time

    async def _create_meal_record(
        self,
        user_id: int,
        meal_data: Dict,
        meal_type: MealType,
        location: str
    ) -> Meal:
        """Create a new meal record in database"""
        try:
            meal = Meal(
                user_id=user_id,
                meal_type=meal_type,
                location=location,
                items=meal_data.get("items", []),
                nutritional_info=meal_data.get("nutritional_info", {}),
                image_url=meal_data.get("image_url"),
                consumed_at=datetime.now()
            )
            
            self.db.add(meal)
            await self.db.commit()
            await self.db.refresh(meal)
            
            return meal

        except Exception as e:
            logger.error(f"Error creating meal record: {str(e)}")
            await self.db.rollback()
            raise

    async def _calculate_compliance(
        self,
        meal: Meal,
        expected_meal: Optional[Dict]
    ) -> Dict:
        """Calculate meal compliance score"""
        try:
            if not expected_meal:
                return {
                    "score": 1.0,
                    "details": "No expected meal to compare"
                }

            # Calculate ingredient similarity
            ingredient_score = self._calculate_ingredient_similarity(
                meal.items,
                expected_meal.get("items", [])
            )

            # Calculate nutritional similarity
            nutrition_score = self._calculate_nutritional_similarity(
                meal.nutritional_info,
                expected_meal.get("nutritional_info", {})
            )

            # Weighted average
            final_score = (ingredient_score * 0.6) + (nutrition_score * 0.4)

            return {
                "score": final_score,
                "ingredient_score": ingredient_score,
                "nutrition_score": nutrition_score,
                "is_compliant": final_score >= self.similarity_threshold
            }

        except Exception as e:
            logger.error(f"Error calculating compliance: {str(e)}")
            raise

    def _calculate_ingredient_similarity(
        self,
        actual_items: List[str],
        expected_items: List[str]
    ) -> float:
        """Calculate similarity between actual and expected ingredients"""
        if not expected_items:
            return 1.0

        actual_set = set(actual_items)
        expected_set = set(expected_items)

        intersection = len(actual_set.intersection(expected_set))
        union = len(actual_set.union(expected_set))

        return intersection / union if union > 0 else 0.0

    def _calculate_nutritional_similarity(
        self,
        actual_nutrition: Dict,
        expected_nutrition: Dict
    ) -> float:
        """Calculate similarity between actual and expected nutrition"""
        if not expected_nutrition:
            return 1.0

        total_diff = 0
        count = 0

        for nutrient, expected_value in expected_nutrition.items():
            if nutrient in actual_nutrition and expected_value > 0:
                actual_value = actual_nutrition[nutrient]
                diff_percentage = abs(actual_value - expected_value) / expected_value
                total_diff += min(diff_percentage, 1.0)
                count += 1

        if count == 0:
            return 1.0

        return 1.0 - (total_diff / count)

    async def _update_user_stats(self, user_id: int, compliance: Dict) -> None:
        """Update user's meal compliance statistics"""
        try:
            user = await self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Update compliance stats
            stats = user.meal_stats or {}
            stats["total_meals"] = stats.get("total_meals", 0) + 1
            stats["compliant_meals"] = stats.get("compliant_meals", 0) + (
                1 if compliance["is_compliant"] else 0
            )
            stats["average_compliance"] = (
                (stats.get("average_compliance", 0) * (stats["total_meals"] - 1) +
                compliance["score"]) / stats["total_meals"]
            )

            user.meal_stats = stats
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error updating user stats: {str(e)}")
            await self.db.rollback()
            raise 