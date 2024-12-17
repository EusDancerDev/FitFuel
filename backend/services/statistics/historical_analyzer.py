from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from ...database.models.user import User
from ...database.models.meal import Meal, MealStatus
from ..notifications.manager import NotificationManager
from ..watch_data.collector import WatchDataCollector
from ..database.cache import RedisCache
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class HistoricalAnalyzer:
    def __init__(
        self,
        notification_manager: NotificationManager,
        watch_collector: WatchDataCollector,
        cache: RedisCache
    ):
        self.notification_manager = notification_manager
        self.watch_collector = watch_collector
        self.cache = cache
        self.cache_duration = timedelta(hours=24)

    async def analyze_trends(
        self,
        user: User,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Analyze historical meal trends and patterns"""
        try:
            cache_key = f"trends:{user.id}:{start_date.date()}:{end_date.date()}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result

            # Gather all required data
            meals = await self._get_meal_history(user, start_date, end_date)
            health_data = await self._get_health_data(user, start_date, end_date)
            
            # Perform analysis
            analysis = {
                "compliance_trends": await self._analyze_compliance_trends(meals),
                "nutritional_trends": await self._analyze_nutritional_trends(meals),
                "timing_patterns": await self._analyze_timing_patterns(meals),
                "health_correlations": await self._analyze_health_correlations(meals, health_data),
                "recommendations": await self._generate_recommendations(meals, health_data)
            }

            # Cache results
            await self.cache.set(cache_key, analysis, expire=int(self.cache_duration.total_seconds()))
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {
                "error": "Failed to analyze trends",
                "details": str(e)
            }

    async def _analyze_compliance_trends(self, meals: List[Dict]) -> Dict:
        """Analyze meal compliance trends over time"""
        df = pd.DataFrame(meals)
        
        weekly_compliance = df.groupby(pd.Grouper(key='scheduled_time', freq='W'))[
            'compliance_score'
        ].mean()

        return {
            "weekly_scores": weekly_compliance.to_dict(),
            "overall_trend": self._calculate_trend(weekly_compliance),
            "best_days": self._find_best_compliance_days(df),
            "challenging_meals": self._identify_challenging_meals(df)
        }

    async def _analyze_nutritional_trends(self, meals: List[Dict]) -> Dict:
        """Analyze nutritional patterns and deviations"""
        df = pd.DataFrame(meals)
        
        nutrient_cols = ['protein', 'carbs', 'fats', 'calories']
        nutrient_trends = {}

        for nutrient in nutrient_cols:
            weekly_avg = df.groupby(pd.Grouper(key='scheduled_time', freq='W'))[
                f'nutrition.{nutrient}'
            ].mean()
            
            nutrient_trends[nutrient] = {
                "weekly_averages": weekly_avg.to_dict(),
                "trend": self._calculate_trend(weekly_avg),
                "consistency_score": self._calculate_consistency(weekly_avg)
            }

        return {
            "nutrient_trends": nutrient_trends,
            "balance_score": self._calculate_nutrient_balance(df),
            "areas_for_improvement": self._identify_nutritional_gaps(df)
        }

    async def _analyze_timing_patterns(self, meals: List[Dict]) -> Dict:
        """Analyze meal timing patterns and consistency"""
        df = pd.DataFrame(meals)
        df['hour'] = df['scheduled_time'].dt.hour
        df['day_of_week'] = df['scheduled_time'].dt.day_name()

        timing_analysis = {
            "meal_time_consistency": self._analyze_time_consistency(df),
            "preferred_times": self._identify_preferred_times(df),
            "skipped_meal_patterns": self._analyze_skip_patterns(df),
            "weekend_vs_weekday": self._compare_weekend_weekday(df)
        }

        return timing_analysis

    async def _analyze_health_correlations(
        self,
        meals: List[Dict],
        health_data: List[Dict]
    ) -> Dict:
        """Analyze correlations between meals and health metrics"""
        meal_df = pd.DataFrame(meals)
        health_df = pd.DataFrame(health_data)

        # Merge meal and health data on date
        merged_df = pd.merge_asof(
            meal_df,
            health_df,
            on='scheduled_time',
            direction='nearest'
        )

        correlations = {
            "energy_levels": self._correlate_with_energy(merged_df),
            "activity_impact": self._analyze_activity_impact(merged_df),
            "sleep_quality": self._analyze_sleep_correlation(merged_df),
            "weight_trajectory": self._analyze_weight_trend(merged_df)
        }

        return correlations

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction and magnitude"""
        if len(series) < 2:
            return "insufficient_data"
            
        slope = np.polyfit(range(len(series)), series.values, 1)[0]
        
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0:
            return "improving" if slope > 0.05 else "slightly_improving"
        else:
            return "declining" if slope < -0.05 else "slightly_declining"

    def _calculate_consistency(self, series: pd.Series) -> float:
        """Calculate consistency score based on variance"""
        if len(series) < 2:
            return 0.0
            
        normalized_std = series.std() / series.mean()
        return max(0, 1 - normalized_std)

    def _identify_challenging_meals(self, df: pd.DataFrame) -> List[Dict]:
        """Identify meals with consistently low compliance"""
        problem_meals = df[df['compliance_score'] < 0.7].groupby('meal_type').agg({
            'compliance_score': ['count', 'mean']
        }).reset_index()
        
        return [
            {
                "meal_type": row['meal_type'],
                "frequency": row['compliance_score']['count'],
                "avg_score": row['compliance_score']['mean']
            }
            for _, row in problem_meals.iterrows()
        ]

    def _analyze_time_consistency(self, df: pd.DataFrame) -> Dict:
        """Analyze meal timing consistency"""
        time_variance = df.groupby('meal_type')['hour'].agg(['std', 'mean'])
        
        return {
            meal_type: {
                "consistency_score": max(0, 1 - std/24),
                "typical_time": f"{int(mean):02d}:00"
            }
            for meal_type, (std, mean) in time_variance.iterrows()
        }

    def _correlate_with_energy(self, df: pd.DataFrame) -> Dict:
        """Analyze correlation between meals and energy levels"""
        energy_impact = {}
        
        for meal_type in df['meal_type'].unique():
            meal_data = df[df['meal_type'] == meal_type]
            
            if len(meal_data) > 0:
                correlation = np.corrcoef(
                    meal_data['compliance_score'],
                    meal_data['energy_level']
                )[0, 1]
                
                energy_impact[meal_type] = {
                    "correlation": float(correlation),
                    "impact_level": self._categorize_correlation(correlation)
                }
        
        return energy_impact

    def _categorize_correlation(self, correlation: float) -> str:
        """Categorize correlation strength"""
        if abs(correlation) < 0.2:
            return "minimal"
        elif abs(correlation) < 0.4:
            return "moderate"
        else:
            return "strong" 

    async def _get_meal_history(
        self,
        user: User,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Retrieve meal history from database"""
        try:
            async with self.db.session() as session:
                meals = await session.query(Meal).filter(
                    Meal.user_id == user.id,
                    Meal.scheduled_time.between(start_date, end_date)
                ).order_by(Meal.scheduled_time.desc()).all()
                return [meal.to_dict() for meal in meals]
        except Exception as e:
            logger.error(f"Error retrieving meal history: {str(e)}")
            return []

    async def _get_health_data(
        self,
        user: User,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Retrieve health data from watch collector"""
        try:
            return await self.watch_collector.collect_health_data(
                user,
                start_time=start_date,
                end_time=end_date
            )
        except Exception as e:
            logger.error(f"Error retrieving health data: {str(e)}")
            return []

    def _find_best_compliance_days(self, df: pd.DataFrame) -> List[Dict]:
        """Find days with highest compliance scores"""
        best_days = df.groupby(df['scheduled_time'].dt.strftime('%A'))[
            'compliance_score'
        ].mean().sort_values(ascending=False)

        return [
            {
                "day": day,
                "average_score": float(score),
                "confidence": self._calculate_confidence(df, day)
            }
            for day, score in best_days.items()
        ]

    def _calculate_confidence(self, df: pd.DataFrame, day: str) -> float:
        """Calculate confidence level for day-based statistics"""
        day_data = df[df['scheduled_time'].dt.strftime('%A') == day]
        if len(day_data) < 3:  # Minimum sample size
            return 0.5
        
        std_dev = day_data['compliance_score'].std()
        sample_size = len(day_data)
        
        # Higher confidence with more samples and lower standard deviation
        confidence = (1 - std_dev) * (1 - 1/sample_size)
        return max(0.1, min(1.0, confidence))

    def _calculate_nutrient_balance(self, df: pd.DataFrame) -> float:
        """Calculate overall nutrient balance score"""
        try:
            # Calculate average daily nutrient ratios
            daily_nutrients = df.groupby(df['scheduled_time'].dt.date).agg({
                'nutrition.protein': 'sum',
                'nutrition.carbs': 'sum',
                'nutrition.fats': 'sum'
            })

            # Calculate macronutrient ratios
            total_calories = (
                daily_nutrients['nutrition.protein'] * 4 +
                daily_nutrients['nutrition.carbs'] * 4 +
                daily_nutrients['nutrition.fats'] * 9
            )

            protein_ratio = daily_nutrients['nutrition.protein'] * 4 / total_calories
            carbs_ratio = daily_nutrients['nutrition.carbs'] * 4 / total_calories
            fats_ratio = daily_nutrients['nutrition.fats'] * 9 / total_calories

            # Score based on ideal macronutrient ratios
            protein_score = 1 - abs(protein_ratio.mean() - 0.25)  # Ideal: 25%
            carbs_score = 1 - abs(carbs_ratio.mean() - 0.50)     # Ideal: 50%
            fats_score = 1 - abs(fats_ratio.mean() - 0.25)       # Ideal: 25%

            return (protein_score + carbs_score + fats_score) / 3

        except Exception as e:
            logger.error(f"Error calculating nutrient balance: {str(e)}")
            return 0.0

    def _identify_nutritional_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Identify areas for nutritional improvement"""
        try:
            daily_nutrients = df.groupby(df['scheduled_time'].dt.date).agg({
                'nutrition.protein': 'sum',
                'nutrition.carbs': 'sum',
                'nutrition.fats': 'sum',
                'nutrition.fiber': 'sum'
            })

            gaps = []
            targets = {
                'protein': {'min': 50, 'max': 100, 'unit': 'g'},
                'carbs': {'min': 225, 'max': 325, 'unit': 'g'},
                'fats': {'min': 44, 'max': 78, 'unit': 'g'},
                'fiber': {'min': 25, 'max': 35, 'unit': 'g'}
            }

            for nutrient, target in targets.items():
                avg_value = daily_nutrients[f'nutrition.{nutrient}'].mean()
                if avg_value < target['min']:
                    gaps.append({
                        'nutrient': nutrient,
                        'current': avg_value,
                        'target': target['min'],
                        'deficit': target['min'] - avg_value,
                        'unit': target['unit'],
                        'severity': 'low'
                    })
                elif avg_value > target['max']:
                    gaps.append({
                        'nutrient': nutrient,
                        'current': avg_value,
                        'target': target['max'],
                        'excess': avg_value - target['max'],
                        'unit': target['unit'],
                        'severity': 'high'
                    })

            return gaps

        except Exception as e:
            logger.error(f"Error identifying nutritional gaps: {str(e)}")
            return [] 

    def _calculate_monthly_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate monthly statistics for display"""
        try:
            # 1. Home vs Outside days
            location_stats = df.groupby(df['scheduled_time'].dt.date)['location'].agg(
                lambda x: 'outside' if 'outside' in x.values else 'home'
            ).value_counts()
            
            days_at_home = int(location_stats.get('home', 0))
            days_outside = int(location_stats.get('outside', 0))

            # 2. Skipped meals by type
            skipped_meals = df[df['status'] == 'SKIPPED'].groupby('meal_type').size().to_dict()

            # 3. Monthly similarity percentages by meal
            avg_similarity = df.groupby('meal_type')['compliance_score'].mean().to_dict()

            # 4. Passes and fails by meal
            meal_results = df.groupby('meal_type').apply(
                lambda x: {
                    'passes': int(sum(x['compliance_score'] >= 0.8)),
                    'fails': int(sum(x['compliance_score'] < 0.8))
                }
            ).to_dict()

            return {
                "location_summary": {
                    "days_at_home": days_at_home,
                    "days_outside": days_outside
                },
                "skipped_meals": {
                    meal_type: int(count) 
                    for meal_type, count in skipped_meals.items()
                },
                "average_similarity": {
                    meal_type: round(score * 100, 1)
                    for meal_type, score in avg_similarity.items()
                },
                "meal_results": meal_results
            }
        except Exception as e:
            logger.error(f"Error calculating monthly stats: {str(e)}")
            return {} 