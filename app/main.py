import uvicorn
import json
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from datetime import datetime, timezone
from bson import ObjectId, json_util
from contextlib import asynccontextmanager

from app.models import User, DailyLog, Recommendation
from app.utils.db_util import db  # Assuming you have database.py with MongoDB connection
from app.utils.llm_util import FitnessLLMAgent
from app.models import User  # Add this import

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
    
    user_dict = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    
    daily_log = DailyLog(
        calories=int(log_data["calories"]),
        activity_level=int(log_data["activityLevel"])
        # date will be automatically set by the default_factory
    )
    print(user_dict)
    fitness_llm_agent = FitnessLLMAgent()
    recommendations = fitness_llm_agent.generate_next_day_plan(user_dict, daily_log)
    
    # Update recommendations to include user_id
    for rec in recommendations:
        rec.user_id = ObjectId(user_id)
    
    recommendation_dicts = [rec.model_dump(by_alias=True, exclude={"_id"}) for rec in recommendations]
    await db.recommendations.insert_many(recommendation_dicts)
    
    # Store the daily log
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"daily_logs": daily_log.model_dump(by_alias=True)}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return { "message": "Log submitted successfully" }

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    recommendations = await db.recommendations.find(
        {"user_id": ObjectId(user_id)}
    ).to_list(length=None)
    
    # Convert MongoDB document to JSON-serializable format
    json_compatible_recommendations = json.loads(json_util.dumps(recommendations))
    
    return {"recommendations": json_compatible_recommendations}

@app.get("/api/profile/{user_id}")
async def get_user_profile(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = json.loads(json_util.dumps(user))
    
    return {"user": user}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

