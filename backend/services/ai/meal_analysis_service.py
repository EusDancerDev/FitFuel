from typing import Dict, List, Optional
import logging
from .llm_manager import LLMManager
from .vision_manager import VisionManager
from ...database.cache import RedisCache
from ...database.models.user import User

logger = logging.getLogger(__name__)

class MealAnalysisService:
    def __init__(
        self,
        llm_manager: LLMManager,
        vision_manager: VisionManager,
        cache: RedisCache
    ):
        self.llm = llm_manager
        self.vision = vision_manager
        self.cache = cache
        self.confidence_threshold = 0.8

    async def analyze_meal_photo(
        self,
        user: User,
        image_path: str,
        expected_meal: Dict = None
    ) -> Dict:
        """Analyze meal photo using both vision and LLM models"""
        try:
            # First, analyze the image with vision models
            vision_result = await self.vision.analyze_image(
                image_path=image_path,
                context={
                    "food_categories": ["meal", "snack", "drink"],
                    "expected_items": expected_meal["ingredients"] if expected_meal else None
                }
            )

            if vision_result["confidence"] < self.confidence_threshold:
                logger.warning("Low confidence in vision analysis")

            # Use LLM to analyze vision results and provide insights
            llm_context = {
                "vision_result": vision_result,
                "expected_meal": expected_meal,
                "user_preferences": user.dietary_preference.value,
                "meal_history": await self._get_meal_history(user)
            }

            llm_result = await self.llm.process_request(
                prompt=self._create_analysis_prompt(llm_context),
                context=llm_context
            )

            return {
                "success": True,
                "vision_analysis": vision_result,
                "llm_analysis": llm_result,
                "combined_confidence": (
                    vision_result["confidence"] + 
                    llm_result.get("confidence", 0.5)
                ) / 2
            }

        except Exception as e:
            logger.error(f"Error in meal analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _create_analysis_prompt(self, context: Dict) -> str:
        """Create prompt for LLM analysis"""
        vision_result = context["vision_result"]
        expected_meal = context.get("expected_meal")
        
        prompt = f"""Analyze this meal based on the vision model results:
        Detected items: {vision_result.get('detections', [])}
        
        User dietary preference: {context['user_preferences']}
        """

        if expected_meal:
            prompt += f"""
            Expected meal:
            - Name: {expected_meal['name']}
            - Ingredients: {expected_meal['ingredients']}
            
            Please analyze:
            1. Compliance with expected meal
            2. Nutritional adequacy
            3. Portion sizes
            4. Suggestions for improvement
            """
        else:
            prompt += """
            Please analyze:
            1. Meal composition
            2. Nutritional value
            3. Alignment with dietary preferences
            4. Suggestions for improvement
            """

        return prompt

    async def _get_meal_history(self, user: User) -> List[Dict]:
        """Get recent meal history for context"""
        try:
            async with self.db.session() as session:
                meals = await session.query(Meal).filter(
                    Meal.user_id == user.id
                ).order_by(
                    Meal.created_at.desc()
                ).limit(5).all()
                
                return [meal.to_dict() for meal in meals]
        except Exception as e:
            logger.error(f"Error getting meal history: {str(e)}")
            return [] 