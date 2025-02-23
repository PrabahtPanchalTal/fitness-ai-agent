from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectID")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

# Daily Log model for embedded documents
class DailyLog(BaseModel):
    calories: int
    activity_level: int
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# User model
class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    weight: float
    height: float
    age: int
    geography: str
    daily_logs: List[DailyLog] = []
    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True

# Recommendation model
class Recommendation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    task: str
    due_date: datetime
    is_done: bool = Field(default=False)
    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True

