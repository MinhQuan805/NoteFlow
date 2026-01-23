from typing import List, Dict, Optional, Any
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os
from datetime import datetime
from bson import ObjectId
from config.db_interface import DatabaseInterface

class LocalBackend(DatabaseInterface):
    def __init__(self, db_dir: str = "db"):
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)
        self._dbs = {}

    def _get_db(self, collection: str) -> TinyDB:
        if collection not in self._dbs:
            path = os.path.join(self.db_dir, f"{collection}.json")
            self._dbs[collection] = TinyDB(path, storage=CachingMiddleware(JSONStorage))
        return self._dbs[collection]
    
    def _flush(self, collection: str):
        """Flush the caching middleware to persist data to disk immediately"""
        if collection in self._dbs:
            storage = self._dbs[collection].storage
            if hasattr(storage, 'flush'):
                storage.flush()
        
    def _serialize(self, doc: Dict) -> Dict:
        """Convert objects like ObjectId/datetime to JSON-serializable formats"""
        new_doc = doc.copy()
        for k, v in new_doc.items():
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif isinstance(v, datetime):
                new_doc[k] = v.isoformat()
            elif isinstance(v, list):
                 new_doc[k] = [self._serialize_item(item) for item in v]
            elif isinstance(v, dict):
                 new_doc[k] = self._serialize(v)
        return new_doc

    def _serialize_item(self, item: Any) -> Any:
        if isinstance(item, ObjectId):
            return str(item)
        elif isinstance(item, datetime):
            return item.isoformat()
        elif isinstance(item, dict):
            return self._serialize(item)
        return item
        
    async def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        db = self._get_db(collection)
        
        def match_func(doc):
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        return False
                elif doc.get(k) != v:
                    return False
            return True
            
        results = db.search(match_func)
        return results[0] if results else None

    async def find(self, collection: str, query: Dict, projection: Dict = None, sort: List = None) -> List[Dict]:
        db = self._get_db(collection)
        
        def match_func(doc):
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        return False
                elif isinstance(v, dict):
                     for op, op_val in v.items():
                         if op == "$ne" and doc.get(k) == op_val:
                             return False
                elif doc.get(k) != v:
                    return False
            return True

        docs = db.search(match_func) if query else db.all()
        
        if sort:
            key, direction = sort[0]
            reverse = direction < 0
            docs.sort(key=lambda x: x.get(key, ""), reverse=reverse)

        return docs

    async def insert_one(self, collection: str, doc: Dict) -> Any:
        db = self._get_db(collection)
        doc = self._serialize(doc)
        if "_id" not in doc:
            doc["_id"] = str(ObjectId())
        
        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
                
        db.insert(doc)
        self._flush(collection)  # Persist immediately
        return InsertOneResult(doc["_id"])

    async def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False) -> Any:
        db = self._get_db(collection)
        
        def update_func(doc):
            if "$set" in update:
                for k, v in update["$set"].items():
                    doc[k] = self._serialize_item(v)
            if "$push" in update:
                for k, v in update["$push"].items():
                    if k not in doc:
                        doc[k] = []
                    if isinstance(v, dict) and "$each" in v:
                        for item in v["$each"]:
                            doc[k].append(self._serialize_item(item))
                    else:
                        doc[k].append(self._serialize_item(v))
            if "$pull" in update:
                for k, v in update["$pull"].items():
                    if k in doc and isinstance(doc[k], list):
                         new_list = []
                         for item in doc[k]:
                             match = False
                             if isinstance(v, dict):
                                 if all(item.get(sk) == sv for sk, sv in v.items()):
                                     match = True
                             elif item == v:
                                 match = True
                             if not match:
                                 new_list.append(item)
                         doc[k] = new_list

        def match_func(doc):
             for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        return False
                elif k in doc and doc[k] != v:
                     return False
             return True
        
        docs = db.search(match_func)
        if not docs and upsert:
            new_doc = query.copy()
            update_func(new_doc)
            if "_id" not in new_doc:
                new_doc["_id"] = str(ObjectId())
            db.insert(self._serialize(new_doc))
            class UpdateResult:
                modified_count = 1
            return UpdateResult()
            
        modified_count = 0
        for doc in docs:
             update_func(doc)
             # Serialize entire doc to handle pre-existing datetime objects
             doc_id = doc.doc_id
             serialized_doc = self._serialize(dict(doc))
             serialized_doc.pop('doc_id', None)  # Remove TinyDB internal field
             db.update(serialized_doc, doc_ids=[doc_id])
             modified_count += 1
             
        class UpdateResult:
            def __init__(self, c): self.modified_count = c
        self._flush(collection)  # Persist immediately
        return UpdateResult(modified_count)

    async def delete_one(self, collection: str, query: Dict) -> Any:
        db = self._get_db(collection)
        
        def match_func(doc):
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        return False
                elif doc.get(k) != v:
                    return False
            return True
            
        removed = db.remove(match_func)
        
        class DeleteResult:
            def __init__(self, c): self.modified_count = c
        self._flush(collection)  # Persist immediately
        return DeleteResult(len(removed))

    async def create_ttl_index(self, collection: str, field: str, expireAfterSeconds: int):
        # TinyDB doesn't support TTL indexes
        pass
