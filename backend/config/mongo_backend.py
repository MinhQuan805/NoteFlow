import os
from typing import List, Dict, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from config.db_interface import DatabaseInterface

class MongoBackend(DatabaseInterface):
    def __init__(self):
        MONGO_URI = os.getenv("MONGO_URI")
        DB_NAME = os.getenv("DB_NAME")
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]

    async def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        return await self.db[collection].find_one(query)

    async def find(self, collection: str, query: Dict, projection: Dict = None, sort: List = None) -> List[Dict]:
        cursor = self.db[collection].find(query, projection)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=None)

    async def insert_one(self, collection: str, doc: Dict) -> Any:
        return await self.db[collection].insert_one(doc)

    async def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False) -> Any:
        return await self.db[collection].update_one(query, update, upsert=upsert)

    async def delete_one(self, collection: str, query: Dict) -> Any:
        return await self.db[collection].delete_one(query)

    async def create_ttl_index(self, collection: str, field: str, expireAfterSeconds: int):
        indexes = await self.db[collection].index_information()
        index_name = f"{field}_1"
        if index_name not in indexes:
            await self.db[collection].create_index(field, expireAfterSeconds=expireAfterSeconds)
