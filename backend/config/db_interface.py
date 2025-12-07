from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class DatabaseInterface(ABC):
    @abstractmethod
    async def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    async def find(self, collection: str, query: Dict, projection: Dict = None, sort: List = None) -> List[Dict]:
        pass

    @abstractmethod
    async def insert_one(self, collection: str, doc: Dict) -> Any:
        pass

    @abstractmethod
    async def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False) -> Any:
        pass

    @abstractmethod
    async def delete_one(self, collection: str, query: Dict) -> Any:
        pass

    @abstractmethod
    async def create_ttl_index(self, collection: str, field: str, expireAfterSeconds: int):
        pass
