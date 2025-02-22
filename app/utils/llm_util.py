import openai
import os
import random
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
from app.models import (
    DailyLog, Recommendation, User
)
from bson import ObjectId
from dotenv import load_dotenv

class FitnessLLMAgent:
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """Initialize OpenAI client with API key from environment variable and default parameters."""
        # Load environment variables from .env file
        load_dotenv()
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

    def generate_next_day_plan(self, user: dict, daily_log: DailyLog) -> List[Recommendation]:
        """
        Generate personalized guidance for the next day based on today's activity log.
        
        Args:
            user: User object containing user details
            daily_log: DailyLog object containing today's activity data
        
        Returns:
            Recommendation: Personalized recommendation object with guidance for tomorrow
        """
        # Calculate averages from the last 7 days of logs
        recent_logs = sorted(user.get('daily_logs', [])[-7:], key=lambda x: x["date"])
        avg_calories = sum(log["calories"] for log in recent_logs) / len(recent_logs) if recent_logs else 0
        avg_activity = sum(log["activity_level"] for log in recent_logs) / len(recent_logs) if recent_logs else 0


        prompt = f"""Based on today's activity log and user profile, create specific, actionable tasks for tomorrow:

User Profile:
- Age: {user["age"]}
- Weight: {user["weight"]}
- Height: {user["height"]}
- Location: {user["geography"]}

Today's Activity:
- Calories: {daily_log.calories}
- Activity Level: {daily_log.activity_level}

7-Day Averages:
- Average Calories: {avg_calories:.0f}
- Average Activity Level: {avg_activity:.1f}


Requirements:
1. Generate 3-4 specific, actionable tasks
2. Include at least one exercise-related task
3. Include at least one nutrition-related task
4. Tasks should be achievable within 24 hours
5. Consider user's activity level trend when suggesting intensity

Output Format:
Provide ONLY tasks separated by pipe symbols (|). Example:
Complete 30 minutes of jogging | Drink 8 glasses of water | Do 3 sets of 15 push-ups | Prepare healthy meal prep for tomorrow

Do not include any other text or explanations in the output."""
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
            # Create and return a Recommendation object
            return [Recommendation(
                user_id=str(user["_id"]),
                task=msg,
                due_date=datetime.now(timezone.utc) + timedelta(days=1)  # Set due date to tomorrow
            ) for msg in response.choices[0].message.content.split("|")]

            # FALLBACK_TASKS = [
            #     "Complete 30 minutes of moderate-intensity cardio and focus on staying hydrated throughout the day.",
            #     "Do a full-body strength training workout with 3 sets of 12 reps each. Don't forget to stretch!",
            #     "Take a rest day focusing on light stretching and getting 8 hours of sleep tonight.",
            #     "Try HIIT workout: 30 seconds high intensity followed by 30 seconds rest, repeat 10 times.",
            #     "Focus on core strength today with a 20-minute ab workout and maintain a balanced diet.",
            #     "Go for a 45-minute walk and include 5 minutes of brisk walking every 10 minutes.",
            #     "Practice yoga or mobility exercises for 30 minutes to improve flexibility.",
            #     "Do bodyweight exercises: 20 push-ups, 30 squats, 15 burpees, repeat 3 times.",
            #     "Combine 20 minutes of cardio with 20 minutes of strength training for a balanced workout.",
            #     "Focus on recovery: light swimming or cycling, followed by 10 minutes of meditation."
            # ]

            # # Create recommendation using the model's expected format
            # return [Recommendation(
            #     user_id=str(user["_id"]),
            #     task=random.choice(FALLBACK_TASKS),
            #     due_date=datetime.now(timezone.utc) + timedelta(days=1)
            # )]
        except Exception as e:
            raise Exception(f"Error generating next day plan: {str(e)}")
