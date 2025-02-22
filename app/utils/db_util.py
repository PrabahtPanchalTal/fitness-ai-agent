import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from urllib.parse import quote_plus

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect_db(self):
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        host = os.getenv("MONGO_HOST")
        port = os.getenv("MONGO_PORT")

        if not all([username, password, host, port]):
            raise ValueError("Missing MongoDB environment variables")

        # Only quote if values exist
        username = quote_plus(str(username))
        password = quote_plus(str(password))
        
        mongodb_url = f"mongodb://{username}:{password}@{host}:{port}"
        self.client = AsyncIOMotorClient(mongodb_url)
        
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
