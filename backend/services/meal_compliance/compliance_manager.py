from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from ...database.models import User, Meal, ComplianceRecord
from ...config import settings
from ..ai.llm_manager import LLMManager
from ..notifications.manager import NotificationManager

logger = logging.getLogger(__name__)

class ComplianceManager:
    def __init__(
        self,
        db_session,
        llm_manager: LLMManager,
        notification_manager: NotificationManager
    ):
        self.db = db_session
        self.llm = llm_manager
        self.notifier = notification_manager
        self.compliance_threshold = settings.COMPLIANCE_THRESHOLD
        self.analysis_window_days = settings.COMPLIANCE_ANALYSIS_WINDOW

    async def analyze_compliance(
        self,
        user_id: int,
        time_window: Optional[int] = None
    ) -> Dict:
        """Analyze user's meal compliance over time"""
        try:
            # Get user data
            user = await self._get_user(user_id)
            window = time_window or self.analysis_window_days

            # Get meal history
            meals = await self._get_meal_history(user_id, window)

            # Analyze compliance patterns
            analysis = await self._analyze_patterns(user, meals)

            # Generate insights and recommendations
            insights = await self._generate_insights(analysis)
            recommendations = await self._generate_recommendations(analysis)

            # Create compliance record
            record = await self._create_compliance_record(
                user_id,
                analysis,
                insights,
                recommendations
            )

            # Send notifications if needed
            await self._handle_notifications(user, analysis)

            return {
                "success": True,
                "analysis": analysis,
                "insights": insights,
                "recommendations": recommendations,
                "record_id": record.id
            }

        except Exception as e:
            logger.error(f"Error analyzing compliance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_user(self, user_id: int) -> User:
        """Get user data"""
        try:
            user = await self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise

    async def _get_meal_history(
        self,
        user_id: int,
        days: int
    ) -> List[Meal]:
        """Get meal history for specified time window"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            meals = await self.db.query(Meal).filter(
                Meal.user_id == user_id,
                Meal.consumed_at >= start_date
            ).order_by(
                Meal.consumed_at.desc()
            ).all()
            return meals
        except Exception as e:
            logger.error(f"Error getting meal history: {str(e)}")
            raise

    async def _analyze_patterns(
        self,
        user: User,
        meals: List[Meal]
    ) -> Dict:
        """Analyze compliance patterns"""
        try:
            meal_types = ["breakfast", "lunch", "dinner", "snack"]
            analysis = {
                "overall_compliance": 0.0,
                "meal_type_compliance": {},
                "location_patterns": {
                    "home": 0,
                    "outside": 0
                },
                "skipped_meals": {},
                "time_patterns": {},
                "nutrition_adherence": 0.0
            }

            for meal_type in meal_types:
                type_meals = [m for m in meals if m.meal_type == meal_type]
                if type_meals:
                    compliance = sum(
                        1 for m in type_meals
                        if m.compliance_score >= self.compliance_threshold
                    ) / len(type_meals)
                    analysis["meal_type_compliance"][meal_type] = compliance

            for meal in meals:
                # Location patterns
                analysis["location_patterns"][meal.location] += 1

                # Skipped meals
                if meal.status == "SKIPPED":
                    analysis["skipped_meals"][meal.meal_type] = \
                        analysis["skipped_meals"].get(meal.meal_type, 0) + 1

                # Time patterns
                hour = meal.consumed_at.hour
                time_slot = f"{hour:02d}:00"
                analysis["time_patterns"][time_slot] = \
                    analysis["time_patterns"].get(time_slot, 0) + 1

            # Calculate overall metrics
            if meals:
                analysis["overall_compliance"] = sum(
                    m.compliance_score for m in meals
                ) / len(meals)

                analysis["nutrition_adherence"] = self._calculate_nutrition_adherence(
                    meals,
                    user.dietary_preferences
                )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            raise

    def _calculate_nutrition_adherence(
        self,
        meals: List[Meal],
        preferences: Dict
    ) -> float:
        """Calculate adherence to nutritional goals"""
        try:
            if not meals:
                return 0.0

            total_adherence = 0.0
            for meal in meals:
                if meal.nutritional_info and preferences.get("nutritional_goals"):
                    meal_adherence = self._compare_nutrition(
                        meal.nutritional_info,
                        preferences["nutritional_goals"]
                    )
                    total_adherence += meal_adherence

            return total_adherence / len(meals)

        except Exception as e:
            logger.error(f"Error calculating nutrition adherence: {str(e)}")
            return 0.0

    def _compare_nutrition(
        self,
        actual: Dict,
        goals: Dict
    ) -> float:
        """Compare actual nutrition with goals"""
        try:
            if not actual or not goals:
                return 0.0

            differences = []
            for nutrient, goal in goals.items():
                if nutrient in actual and goal > 0:
                    diff = abs(actual[nutrient] - goal) / goal
                    differences.append(max(0, 1 - diff))

            return sum(differences) / len(differences) if differences else 0.0

        except Exception as e:
            logger.error(f"Error comparing nutrition: {str(e)}")
            return 0.0

    async def _generate_insights(self, analysis: Dict) -> List[Dict]:
        """Generate insights from compliance analysis"""
        try:
            prompt = self._create_insights_prompt(analysis)
            result = await self.llm.process_request(prompt=prompt)
            return result.get("insights", [])
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []

    async def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate recommendations based on analysis"""
        try:
            prompt = self._create_recommendations_prompt(analysis)
            result = await self.llm.process_request(prompt=prompt)
            return result.get("recommendations", [])
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _create_insights_prompt(self, analysis: Dict) -> str:
        """Create prompt for generating insights"""
        return f"""Generate insights based on this compliance analysis:
        {analysis}
        
        Focus on:
        1. Significant patterns
        2. Areas of success
        3. Areas needing improvement
        4. Unusual behaviors
        5. Trends over time
        
        Format response as list of structured insights in JSON."""

    def _create_recommendations_prompt(self, analysis: Dict) -> str:
        """Create prompt for generating recommendations"""
        return f"""Generate recommendations based on this compliance analysis:
        {analysis}
        
        Requirements:
        1. Actionable suggestions
        2. Realistic goals
        3. Progressive improvements
        4. Consider user context
        5. Prioritize key areas
        
        Format response as list of structured recommendations in JSON."""

    async def _create_compliance_record(
        self,
        user_id: int,
        analysis: Dict,
        insights: List[Dict],
        recommendations: List[Dict]
    ) -> ComplianceRecord:
        """Create compliance record in database"""
        try:
            record = ComplianceRecord(
                user_id=user_id,
                analysis_data=analysis,
                insights=insights,
                recommendations=recommendations,
                created_at=datetime.now()
            )
            
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
            
            return record

        except Exception as e:
            logger.error(f"Error creating compliance record: {str(e)}")
            await self.db.rollback()
            raise

    async def _handle_notifications(
        self,
        user: User,
        analysis: Dict
    ) -> None:
        """Handle notification generation based on analysis"""
        try:
            if analysis["overall_compliance"] < self.compliance_threshold:
                await self._send_compliance_notification(user, analysis)
        except Exception as e:
            logger.error(f"Error handling notifications: {str(e)}")

    async def _send_compliance_notification(
        self,
        user: User,
        analysis: Dict
    ) -> None:
        """Send compliance-related notification"""
        try:
            await self.notifier.create_notification(
                user_id=user.id,
                notification_type="COMPLIANCE_ALERT",
                content={
                    "compliance_score": analysis["overall_compliance"],
                    "message": "Your meal compliance needs attention",
                    "analysis_summary": analysis
                },
                priority=2
            )
        except Exception as e:
            logger.error(f"Error sending compliance notification: {str(e)}") 