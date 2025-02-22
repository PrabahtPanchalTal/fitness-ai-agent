import uvicorn
import json
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from datetime import datetime, timezone
from bson import ObjectId
from contextlib import asynccontextmanager

from app.models import User, DailyLog, Recommendation
from app.utils.db_util import db  # Assuming you have database.py with MongoDB connection
from app.utils.llm_util import FitnessLLMAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect_db()
    yield
    # Shutdown
    await db.close_db()

app = FastAPI(lifespan=lifespan)

@app.post("/api/onboarding")
async def user_onboarding(user: User):
    user_dict = user.model_dump(by_alias=True)
    user_result = await db.users.insert_one(user_dict)
    return {
        "message": "User onboarded successfully",
        "userId": str(user_result.inserted_id)
    }

@app.post("/api/log")
async def submit_daily_log(log_data: dict):
    user_id = log_data.get("userId")
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Fetch the user object first
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    daily_log = DailyLog(
        calories=log_data["calories"],
        activity_level=log_data["activityLevel"]
    )
    
    fitness_llm_agent = FitnessLLMAgent()
    message = fitness_llm_agent.generate_next_day_plan(user, daily_log)  # Pass user object instead of user_id

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"daily_logs": daily_log.model_dump()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": message}

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    recommendations = await db.recommendations.find(
        {"user_id": ObjectId(user_id)}
    ).to_list(length=None)
    
    return {
        "recommendations": [
            {
                "task": rec["task"],
                "dueDate": rec["due_date"].isoformat()
            }
            for rec in recommendations
        ]
    }

@app.get("/api/profile/{user_id}")
async def get_user_profile(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = await db.user_profiles.find_one({"user_id": ObjectId(user_id)})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user["_id"])
    if profile:
        profile["_id"] = str(profile["_id"])
        profile["user_id"] = str(profile["user_id"])
    
    return {
        "user": user,
        "profile": profile
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

