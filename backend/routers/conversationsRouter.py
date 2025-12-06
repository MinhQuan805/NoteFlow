from fastapi import APIRouter, HTTPException, Depends
from schemas.conversationSchema import Conversation, MessageItem
from config.database import db
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from bson.errors import InvalidId
import uuid
from typing import List
from schemas.querySchema import QueryRequest, QueryResponse
from ai.rag_system import RAGSystem

rag = RAGSystem("ai/config.yaml")

conversation_collection = db["conversations"]
notebook_collection = db["notebooks"]

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"]
)

@router.post("/query/{conversationId}", response_model=QueryResponse)
async def query_rag(conversationId: str, request: QueryRequest):
    """
    Query the RAG system.
    """
    now = datetime.now(timezone.utc)
    try:
        # Get intent for metadata
        try:
            obj_id = ObjectId(conversationId)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid conversationId")

        conversation = await conversation_collection.find_one({"_id": obj_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        await conversation_collection.update_one(
            {"_id": obj_id},
            {
                "$push": {"messages": request.message_item.model_dump()},
                "$set": {
                    "updated_at": now,
                    "expireAt": now + timedelta(days=3)
                }
            }
        )

        intent = rag.intent_classifier.predict(request.query)
        
        response_text = rag.query(request.query, file_filters=request.file_filters)
        
        assistant_message = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "parts": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }

        await conversation_collection.update_one(
            {"_id": obj_id},
            {
                "$push": {"messages": assistant_message},
                "$set": {
                    "updated_at": now,
                    "expireAt": now + timedelta(days=3)
                }
            }
        )
        
        return {
            "response_message": assistant_message,
            "intent": intent,
            "mode": "Hybrid/Full"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add 1 message into conversation
@router.patch("/{conversationId}", response_model=dict)
async def update_conversation(
    conversationId: str,
    message_item: MessageItem
):
    try:
        obj_id = ObjectId(conversationId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid conversationId format")

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
@router.get("/{session_id}", response_model=dict)
async def get_conversation(session_id: str):
    try:
        obj_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    doc = await conversation_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "title": doc["title"],
        "messages": [MessageItem(**m) for m in doc.get("messages", [])]
    }

# Create new conversation
@router.post("/create/{notebookId}")
async def create_conversation(notebookId: str):
    try:
        _ = ObjectId(notebookId)
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