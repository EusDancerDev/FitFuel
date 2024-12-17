from typing import Dict, List, Optional
import logging
from .llm_manager import LLMManager
from .vision_manager import VisionManager
from .meal_analysis_service import MealAnalysisService
from ...database.cache import RedisCache
from ...database.models.user import User

logger = logging.getLogger(__name__)

class AICoordinator:
    def __init__(
        self,
        llm_manager: LLMManager,
        vision_manager: VisionManager,
        meal_analysis_service: MealAnalysisService,
        cache: RedisCache
    ):
        self.llm = llm_manager
        self.vision = vision_manager
        self.meal_analyzer = meal_analysis_service
        self.cache = cache
        self.confidence_threshold = 0.8

    async def analyze_meal_compliance(
        self,
        user: User,
        image_path: str,
        expected_meal: Dict
    ) -> Dict:
        """Coordinate AI analysis of meal compliance"""
        try:
            # First, analyze the image with vision models
            vision_result = await self.vision.analyze_image(
                image_path=image_path,
                model_key="clip",  # Start with default model
                context={
                    "food_categories": ["meal", "snack", "drink"],
                    "expected_items": expected_meal["ingredients"]
                }
            )

            # If confidence is low, try other vision models
            if vision_result["confidence"] < self.confidence_threshold:
                logger.info("Low confidence with CLIP, trying other models")
                for model in ["emu2", "idefics", "fuyu", "nomic"]:
                    backup_result = await self.vision.analyze_image(
                        image_path=image_path,
                        model_key=model,
                        context={"expected_items": expected_meal["ingredients"]}
                    )
                    if backup_result["confidence"] > vision_result["confidence"]:
                        vision_result = backup_result

            # Use LLM to analyze compliance
            llm_result = await self.llm.process_request(
                prompt=self._create_analysis_prompt(vision_result, expected_meal),
                model_key="gpt4",  # Start with default model
                context={
                    "vision_result": vision_result,
                    "expected_meal": expected_meal,
                    "user_preferences": user.dietary_preference.value
                }
            )

            # Combine results and calculate final compliance
            return await self._combine_analysis_results(
                vision_result,
                llm_result,
                expected_meal
            )

        except Exception as e:
            logger.error(f"Error in AI coordination: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _create_analysis_prompt(
        self,
        vision_result: Dict,
        expected_meal: Dict
    ) -> str:
        """Create prompt for LLM analysis"""
        return f"""Analyze meal compliance based on:

Vision Analysis:
{vision_result}

Expected Meal:
- Name: {expected_meal['name']}
- Ingredients: {expected_meal['ingredients']}

Please provide:
1. Compliance assessment (0-100%)
2. Missing ingredients
3. Extra ingredients
4. Portion size analysis
5. Nutritional impact of differences
6. Suggestions for improvement

Format response as structured JSON."""

    async def _combine_analysis_results(
        self,
        vision_result: Dict,
        llm_result: Dict,
        expected_meal: Dict
    ) -> Dict:
        """Combine and validate results from different AI models"""
        try:
            # Calculate weighted compliance score
            vision_weight = 0.6  # Vision analysis carries more weight
            llm_weight = 0.4

            compliance_score = (
                vision_result["confidence"] * vision_weight +
                llm_result.get("compliance_score", 0) * llm_weight
            )

            # Validate results
            validation_result = await self._validate_combined_results(
                vision_result,
                llm_result,
                expected_meal
            )

            if not validation_result["valid"]:
                logger.warning(f"Validation failed: {validation_result['reason']}")
                # Adjust confidence score based on validation
                compliance_score *= 0.8

            return {
                "success": True,
                "compliance_score": compliance_score,
                "vision_analysis": vision_result,
                "llm_analysis": llm_result,
                "validation": validation_result,
                "recommendations": llm_result.get("recommendations", []),
                "confidence": min(vision_result["confidence"], llm_result.get("confidence", 1.0))
            }

        except Exception as e:
            logger.error(f"Error combining analysis results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _validate_combined_results(
        self,
        vision_result: Dict,
        llm_result: Dict,
        expected_meal: Dict
    ) -> Dict:
        """Validate combined results for consistency"""
        try:
            # Check for major discrepancies between vision and LLM analysis
            vision_items = set(vision_result.get("detected_items", []))
            llm_items = set(llm_result.get("identified_items", []))
            
            item_agreement = len(vision_items.intersection(llm_items)) / len(vision_items.union(llm_items))
            
            # Validate nutritional analysis
            nutrition_valid = self._validate_nutrition(
                llm_result.get("nutritional_analysis", {}),
                expected_meal.get("nutrition", {})
            )

            # Check portion size consistency
            portion_valid = self._validate_portions(
                vision_result.get("portion_sizes", {}),
                llm_result.get("portion_analysis", {})
            )

            valid = (
                item_agreement >= 0.7 and
                nutrition_valid and
                portion_valid
            )

            return {
                "valid": valid,
                "item_agreement": item_agreement,
                "nutrition_valid": nutrition_valid,
                "portion_valid": portion_valid,
                "reason": None if valid else "Inconsistent analysis results"
            }

        except Exception as e:
            logger.error(f"Error validating results: {str(e)}")
            return {
                "valid": False,
                "reason": str(e)
            }

    def _validate_nutrition(self, analyzed: Dict, expected: Dict) -> bool:
        """Validate nutritional analysis"""
        if not analyzed or not expected:
            return True  # Skip validation if data is missing
            
        # Allow for 20% variance in nutritional values
        for nutrient in ["protein", "carbs", "fats"]:
            if nutrient in analyzed and nutrient in expected:
                variance = abs(analyzed[nutrient] - expected[nutrient]) / expected[nutrient]
                if variance > 0.2:
                    return False
                    
        return True

    def _validate_portions(self, vision_portions: Dict, llm_portions: Dict) -> bool:
        """Validate portion size analysis"""
        if not vision_portions or not llm_portions:
            return True  # Skip validation if data is missing
            
        # Check for major discrepancies in portion assessments
        for item in vision_portions:
            if item in llm_portions:
                vision_size = self._normalize_portion_size(vision_portions[item])
                llm_size = self._normalize_portion_size(llm_portions[item])
                
                if abs(vision_size - llm_size) > 0.3:  # Allow 30% variance
                    return False
                    
        return True

    def _normalize_portion_size(self, size: str) -> float:
        """Normalize portion size descriptions to numerical values"""
        size_map = {
            "very small": 0.2,
            "small": 0.4,
            "medium": 0.6,
            "large": 0.8,
            "very large": 1.0
        }
        return size_map.get(size.lower(), 0.6)  # Default to medium if unknown 