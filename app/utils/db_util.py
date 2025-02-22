import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv

class Database:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect_db(self):
        mongodb_uri = os.getenv("MONGO_URI")

        if not all([mongodb_uri]):
            raise ValueError("Missing MongoDB environment variables")
        
        self.client = AsyncIOMotorClient(mongodb_uri)
        
        # Get database name from environment variable
        # db_name = os.getenv("MONGO_DB_NAME")
        # if not db_name:
        #     raise ValueError("Missing MONGO_DB_NAME environment variable")
            
        self.db = self.client["fitness_app"]
        
        # Initialize collections as properties
        self.users = self.db["users"]
        self.recommendations = self.db["recommendations"]
        self.user_profiles = self.db["user_profiles"]

    async def close_db(self):
        if self.client is not None:
            self.client.close()


# Create a singleton instance
db = Database()
