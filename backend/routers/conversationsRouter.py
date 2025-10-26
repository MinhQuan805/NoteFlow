from fastapi import APIRouter, HTTPException, Depends
from schemas.conversationSchema import Conversation, MessageItem
from config.database import db
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

conversation_collection = db["conversations"]
notebook_collection = db["notebooks"]

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"]
)


# Get all conversations
@router.get("/getAll/{notebookId}", response_model=List[dict])
async def get_all_conversation(notebookId: str):
    conversations = []
    cursor = conversation_collection.find(
        {"notebookId": notebookId, "deleted": {"$ne": True}},
        {"messages": 0, "deleted": 0}).sort("updated_at", -1)
    async for doc in cursor:
        conversations.append({
            "id": str(doc["_id"]),
            "title": doc["title"]
        })
    return conversations

# Get conversation by session_id
@router.get("/{session_id}", response_model=Conversation)
async def get_conversation(session_id: str):
    try:
        obj_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    doc = await conversation_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return Conversation(
        title=doc["title"],
        messages=[MessageItem(**m) for m in doc.get("messages", [])],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        deleted=doc.get("deleted", False),
        expireAt=doc.get("expireAt"),
    )

# Create new conversation
@router.post("/create/{notebookId}")
async def create_conversation(notebookId: str):
    try:
        notebook_obj_id = ObjectId(notebookId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notebookId format")
    now = datetime.now(timezone.utc)
    new_conversation = {
        "title": "New chat",
        "notebookId": notebookId,
        "messages": [],
        "created_at": now,
        "updated_at": now,
        "deleted": False,
        "expireAt": now + timedelta(days=3)
    }

    result = await conversation_collection.insert_one(new_conversation)
    conversationId = str(result.inserted_id)
    return {"conversationId": conversationId}

# Update title of conversation
@router.patch("/update_title/{session_id}")
async def update_title(session_id: str, title: str):
    try:
        session_obj_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session_id format")
    
    result = await conversation_collection.update_one(
        {"_id": session_obj_id},
        {
            "$set": {
                "title": title
            }
        }
    )

    if result.modified_count == 1:
        return
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

# Add 1 message into conversation
@router.patch("/{session_id}", response_model=dict)
async def update_conversation(
    session_id: str,
    message_item: MessageItem
):
    try:
        obj_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    now = datetime.now(timezone.utc)
    result = await conversation_collection.update_one(
        {"_id": obj_id},
        {
            "$push": {"messages": message_item.model_dump()},
            "$set": {
                "updated_at": now,
                "expireAt": now + timedelta(days=3)
            }
        }
    )

    if result.modified_count == 1:
        return {"status": True, "message": "Conversation has been updated"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

# Delete conversation by id (soft delete + TTL)
@router.delete("/delete/{session_id}", response_model=dict)
async def delete_conversation(session_id: str):
    try:
        obj_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    now = datetime.now(timezone.utc)
    result = await conversation_collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "deleted": True,
                "deleted_at": now,
                "expireAt": now + timedelta(days=3)
            }
        }
    )

    if result.modified_count == 1:
        return {"status": True, "message": "Conversation will be deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")
    

