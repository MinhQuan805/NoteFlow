from fastapi import APIRouter, HTTPException, Depends
from schemas.conversationSchema import Conversation, MessageItem
from config.database import db
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from bson.errors import InvalidId
import uuid
from typing import List
from schemas.querySchema import QueryRequest, QueryResponse
from ai.rag_manager import RAGManager

conversation_collection = "conversations"
notebook_collection = "notebooks"

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"]
)

@router.post("/query/{notebookId}/{conversationId}", response_model=QueryResponse)
async def query_rag(notebookId: str, conversationId: str, request: QueryRequest):
    rag = RAGSystem(config_path="ai/config.yaml", notebook_id=notebookId)
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

        conversation = await db.find_one(conversation_collection, {"_id": obj_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get notebookId to use correct RAG instance
        notebookId = conversation.get("notebookId")
        if not notebookId:
             raise HTTPException(status_code=500, detail="Conversation missing notebookId")
            
        rag = RAGManager.get_rag(notebookId)

        await db.update_one(
            conversation_collection,
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
        print(f"[DEBUG] Intent: {intent}")
        print(f"[DEBUG] File filters: {request.file_filters}")
        
        response_text = rag.query(request.query, file_filters=request.file_filters)
        print(f"[DEBUG] Response received: {response_text[:200] if response_text else 'None'}...")
        
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

        await db.update_one(
            conversation_collection,
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
        import traceback
        error_msg = str(e)
        print(f"[ERROR] Query failed: {error_msg}")
        traceback.print_exc()
        
        # Return more specific error messages
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            raise HTTPException(status_code=429, detail=f"API rate limit exceeded: {error_msg}")
        elif "404" in error_msg or "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Model or resource not found: {error_msg}")
        else:
            raise HTTPException(status_code=500, detail=f"Query error: {error_msg}")

@router.post("/generate_slides/{conversationId}", response_model=QueryResponse)
async def generate_slides(conversationId: str, request: QueryRequest):
    """
    Generate interactive HTML slides based on RAG retrieval.
    """
    now = datetime.now(timezone.utc)
    
    try:
        try:
            obj_id = ObjectId(conversationId)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid conversationId")

        conversation = await db.find_one(conversation_collection, {"_id": obj_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        notebookId = conversation.get("notebookId")
        if not notebookId:
            raise HTTPException(status_code=500, detail="Conversation missing notebookId")
        
        rag = RAGManager.get_rag(notebookId)

        # Add user message to conversation
        await db.update_one(
            conversation_collection,
            {"_id": obj_id},
            {
                "$push": {"messages": request.message_item.model_dump()},
                "$set": {
                    "updated_at": now,
                    "expireAt": now + timedelta(days=3)
                }
            }
        )

        # Generate slides HTML
        html_content = rag.generate_slides_html(request.query, file_filters=request.file_filters)
        
        # Create assistant message with slides
        assistant_message = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "parts": [
                {
                    "type": "slides",
                    "text": html_content
                }
            ]
        }

        # Save assistant message to conversation
        await db.update_one(
            conversation_collection,
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
            "intent": "Slides_Generation",
            "mode": "RAG"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_slides/{notebookId}/{conversationId}", response_model=QueryResponse)
async def generate_slides(notebookId: str, conversationId: str, request: QueryRequest):
    """
    Generate interactive HTML slides based on RAG retrieval.
    """
    rag = RAGSystem(config_path="ai/config.yaml", notebook_id=notebookId)
    now = datetime.now(timezone.utc)
    
    try:
        # Validate conversationId
        try:
            obj_id = ObjectId(conversationId)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid conversationId")

        conversation = await conversation_collection.find_one({"_id": obj_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Add user message to conversation
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

        # Generate slides HTML
        html_content = rag.generate_slides_html(request.query, file_filters=request.file_filters)
        
        # Create assistant message with slides
        assistant_message = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "parts": [
                {
                    "type": "slides",
                    "text": html_content
                }
            ]
        }

        # Save assistant message to conversation
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
            "intent": "Slides_Generation",
            "mode": "RAG"
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
    result = await db.update_one(
        conversation_collection,
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
    docs = await db.find(
        conversation_collection,
        {"notebookId": notebookId, "deleted": {"$ne": True}},
        projection={"messages": 0, "deleted": 0},
        sort=[("updated_at", -1)]
    )
    for doc in docs:
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

    doc = await db.find_one(conversation_collection, {"_id": obj_id})
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

    result = await db.insert_one(conversation_collection, new_conversation)
    conversationId = str(result.inserted_id)
    return {"conversationId": conversationId}

# Update title of conversation
@router.patch("/update_title/{session_id}")
async def update_title(session_id: str, title: str):
    try:
        session_obj_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session_id format")
    
    result = await db.update_one(
        conversation_collection,
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
    result = await db.update_one(
        conversation_collection,
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