from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from config.database import db
from schemas.noteSchema import Note, NoteContainer, UpdateNoteRequest

note_collection = db["notes"]

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

@router.post("/", response_model=dict)
async def create_note(note: NoteContainer):
    new_note = note.model_dump()

    result = await note_collection.insert_one(new_note)
    return {
        "id": str(result.inserted_id),
        "title": new_note["title"]
    }

@router.patch("/{noteId}", response_model=dict)
async def update_note_block(noteId: str, note: UpdateNoteRequest):
    try:
        obj_id = ObjectId(noteId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid noteId format")

    note_data = [item.model_dump() for item in note.blocks]
    result = await note_collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "title": note.title,
                "blocks": note_data,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.modified_count == 1:
        return {
            "id": noteId,
            "title": note.title
        }
    raise HTTPException(status_code=404, detail="Note not found")


@router.get("/getAll/{notebookId}", response_model=List[dict])
async def get_all_notes(notebookId: str):
    notes = []
    cursor = note_collection.find(
        {"notebookId": notebookId},
        {"blocks": 0, "created_at": 0}
    ).sort("updated_at", -1)

    async for doc in cursor:
        notes.append({
            "id": str(doc["_id"]),
            "title": doc["title"]
        })
    return notes

@router.get("/{noteId}", response_model=dict)
async def get_note(noteId: str):
    try:
        obj_id = ObjectId(noteId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid note_id format")

    doc = await note_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Note not found")

    blocks = [Note(**b) for b in doc.get("blocks", [])]

    return {
        "title": doc["title"],
        "blocks": blocks,
    }


@router.delete("/delete/{noteId}", response_model=dict)
async def delete_note(noteId: str):
    try:
        obj_id = ObjectId(noteId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid noteId format")

    result = await note_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 1:
        return {"status": True, "message": "Note permanently deleted"}
    raise HTTPException(status_code=404, detail="Note not found")
