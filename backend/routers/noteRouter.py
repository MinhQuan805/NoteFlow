from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from config.database import db
from schemas.noteSchema import Note

note_collection = db["notes"]

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

@router.patch("/{note_id}", response_model=dict)
async def update_note_blocks(note_id: str, blocks: List[Note]):
    try:
        obj_id = ObjectId(note_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid note_id format")

    block_data = [b.model_dump() for b in blocks]

    result = await note_collection.update_one(
        {"_id": obj_id},
        {"$set": {"blocks": block_data, "updated_at": datetime.now(timezone.utc)}}
    )

    if result.modified_count == 1:
        return {"status": True, "message": "Note updated"}
    raise HTTPException(status_code=404, detail="Note not found")


@router.get("/getAll/{notebookId}", response_model=List[dict])
async def get_all_notes(notebookId: str):
    notes = []
    cursor = note_collection.find(
        {"notebookId": notebookId},
        {"blocks": 0}
    ).sort("updated_at", -1)

    async for doc in cursor:
        notes.append({
            "id": str(doc["_id"]),
            "title": doc["title"]
        })
    return notes

@router.get("/{note_id}", response_model=dict)
async def get_note(note_id: str):
    try:
        obj_id = ObjectId(note_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid note_id format")

    doc = await note_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Note not found")

    blocks = [Note(**b) for b in doc.get("notes", [])]

    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "notebookId": doc["notebookId"],
        "blocks": blocks,
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"]
    }

@router.post("/create/{notebookId}", response_model=dict)
async def create_note(notebookId: str):
    """Tạo note mới trong notebook"""
    try:
        _ = ObjectId(notebookId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notebookId format")

    now = datetime.now(timezone.utc)
    new_note = {
        "title": "New note",
        "notebookId": notebookId,
        "blocks": [],
        "created_at": now,
        "updated_at": now
    }

    result = await note_collection.insert_one(new_note)
    return {"noteId": str(result.inserted_id)}

@router.patch("/update_title/{note_id}", response_model=dict)
async def update_note_title(note_id: str, title: str):
    try:
        obj_id = ObjectId(note_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid note_id format")

    result = await note_collection.update_one(
        {"_id": obj_id},
        {"$set": {"title": title, "updated_at": datetime.now(timezone.utc)}}
    )

    if result.modified_count == 1:
        return {"status": True, "message": "Title updated"}
    raise HTTPException(status_code=404, detail="Note not found")

@router.delete("/delete/{note_id}", response_model=dict)
async def delete_note(note_id: str):
    try:
        obj_id = ObjectId(note_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid note_id format")

    result = await note_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 1:
        return {"status": True, "message": "Note permanently deleted"}
    raise HTTPException(status_code=404, detail="Note not found")
