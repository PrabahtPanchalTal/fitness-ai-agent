import openai
import os
from typing import List, Optional, Dict
from datetime import datetime, timezone
from app.models import (
    DailyLog, Recommendation, User
)

class FitnessLLMAgent:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """Initialize OpenAI client with API key from environment variable and default parameters."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.system_prompt = """You are an expert fitness coach, nutritionist, and wellness advisor. 
        Your goal is to help users transform their lives through personalized fitness guidance, 
        nutrition advice, and healthy lifestyle recommendations. You have extensive knowledge of:
        - Exercise physiology and workout programming
        - Nutrition and dietary planning
        - Behavior change psychology
        - Injury prevention and recovery
        - Wellness and stress management
        Always provide evidence-based, safe, and personalized recommendations."""
    
    def create_fitness_plan(
        self,
        user: User,
        goals: List[str],
        constraints: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a personalized fitness plan based on user profile and goals.
        
        Args:
            user: User object containing basic user details
            goals: List of fitness goals as strings
            constraints: List of limitations or constraints (injuries, equipment, etc.)
        """
        prompt = self._construct_fitness_plan_prompt(user, goals, constraints)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating fitness plan: {str(e)}")

    def get_workout_advice(
        self,
        exercise: str,
        user_level: str,
    ) -> str:
        """
        Get specific advice for an exercise or workout.
        
        Args:
            exercise: Name of the exercise or workout type
            user_level: Beginner, Intermediate, or Advanced
        """
        prompt = f"Provide detailed guidance for performing {exercise} safely and effectively for a {user_level} level individual."
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating workout advice: {str(e)}")

    def get_nutrition_guidance(
        self,
        dietary_preferences: List[str],
        health_conditions: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
    ) -> str:
        """
        Generate personalized nutrition guidance.
        
        Args:
            dietary_preferences: List of dietary preferences (vegan, keto, etc.)
            health_conditions: List of health conditions to consider
            goals: List of nutrition-related goals
        """
        prompt = self._construct_nutrition_prompt(dietary_preferences, health_conditions, goals)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating nutrition guidance: {str(e)}")

    def get_progress_feedback(
        self,
        initial_stats: Dict,
        current_stats: Dict,
        goals: List[str],
        timeframe: str,
    ) -> str:
        """
        Analyze progress and provide feedback and adjustments.
        
        Args:
            initial_stats: Dict of starting measurements/stats
            current_stats: Dict of current measurements/stats
            goals: List of fitness goals
            timeframe: Time period of progress
        """
        prompt = self._construct_progress_prompt(initial_stats, current_stats, goals, timeframe)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating progress feedback: {str(e)}")

    def _construct_fitness_plan_prompt(
        self,
        user: User,
        goals: List[str],
        constraints: Optional[List[str]]
    ) -> str:
        """Construct a detailed prompt for fitness plan generation."""
        prompt = f"""Based on the following user profile and goals, create a detailed fitness plan:

User Profile:
- Age: {user.age}
- Weight: {user.weight}
- Height: {user.height}
- Location: {user.geography}

Goals:
{chr(10).join('- ' + goal for goal in goals)}
"""
        if constraints:
            prompt += f"\nConstraints/Limitations:\n{chr(10).join('- ' + constraint for constraint in constraints)}"
        
        return prompt

    def _construct_nutrition_prompt(
        self,
        dietary_preferences: List[str],
        health_conditions: Optional[List[str]],
        goals: Optional[List[str]]
    ) -> str:
        """Construct a detailed prompt for nutrition guidance."""
        prompt = f"""Create a personalized nutrition plan considering:

Dietary Preferences:
{chr(10).join('- ' + pref for pref in dietary_preferences)}

"""
        if health_conditions:
            prompt += f"\nHealth Conditions:\n{chr(10).join('- ' + cond for cond in health_conditions)}"
        
        if goals:
            prompt += f"\nNutrition Goals:\n{chr(10).join('- ' + goal for goal in goals)}"
        
        return prompt

    def _construct_progress_prompt(
        self,
        initial_stats: Dict,
        current_stats: Dict,
        goals: List[str],
        timeframe: str
    ) -> str:
        """Construct a detailed prompt for progress analysis."""
        return f"""Analyze the following fitness progress and provide detailed feedback:

Initial Stats:
{chr(10).join(f'- {k}: {v}' for k, v in initial_stats.items())}

Current Stats:
{chr(10).join(f'- {k}: {v}' for k, v in current_stats.items())}

Goals:
{chr(10).join('- ' + goal for goal in goals)}

Timeframe: {timeframe}

Please provide:
1. Progress analysis
2. Areas of improvement
3. Recommended adjustments
4. Motivation and encouragement
"""

    async def generate_recommendations(
        self,
        user: User,
        daily_logs: List[DailyLog],
    ) -> List[Recommendation]:
        """
        Generate recommendations based on user data and daily logs.
        
        Args:
            user: User object containing user details
            daily_logs: List of DailyLog objects
        """
        prompt = f"""Based on the following user data and logs, generate personalized recommendations:

User Details:
- Age: {user.age}
- Weight: {user.weight}
- Height: {user.height}
- Location: {user.geography}

Recent Activity Logs:
{chr(10).join(f'- Date: {log.date}, Calories: {log.calories}, Activity Level: {log.activity_level}' for log in daily_logs[-5:])}

Please provide specific, actionable recommendations for improving fitness and health outcomes.
"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            # Parse the response and create Recommendation objects
            recommendations = []
            # Add logic to parse LLM response and create Recommendation objects
            # This is a placeholder implementation
            recommendation = Recommendation(
                user_id=user.id,
                task=response.choices[0].message.content,
                due_date=datetime.now(timezone.utc)
            )
            recommendations.append(recommendation)
            return recommendations
            
        except Exception as e:
            raise Exception(f"Error generating recommendations: {str(e)}")

    def generate_next_day_plan(self, user: Dict, daily_log: DailyLog) -> str:
        """
        Generate personalized guidance for the next day based on today's activity log.
        
        Args:
            user: Dictionary containing user details (age, weight, height, geography)
            daily_log: DailyLog object containing today's activity data
        
        Returns:
            str: Personalized message with guidance for tomorrow
        """
        prompt = f"""Based on today's activity log and user profile, provide personalized guidance for tomorrow:

User Profile:
- Age: {user.get('age')}
- Weight: {user.get('weight')}
- Height: {user.get('height')}
- Location: {user.get('geography')}
Today's Activity:
- Calories: {daily_log.calories}
- Activity Level: {daily_log.activity_level}

Please provide:
1. A brief analysis of today's activity
2. Specific recommendations for tomorrow's workout and nutrition
3. Any adjustments needed based on today's performance
4. A motivational message
"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating next day plan: {str(e)}")
