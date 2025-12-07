from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from config.database import db
from schemas.noteSchema import Note, NoteContainer, UpdateNoteRequest

note_collection = "notes"

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

@router.post("/", response_model=dict)
async def create_note(note: NoteContainer):
    new_note = note.model_dump()

    result = await db.insert_one(note_collection, new_note)
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
    result = await db.update_one(
        note_collection,
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
    docs = await db.find(
        note_collection,
        {"notebookId": notebookId},
        projection={"blocks": 0, "created_at": 0},
        sort=[("updated_at", -1)]
    )

    for doc in docs:
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

    doc = await db.find_one(note_collection, {"_id": obj_id})
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

    result = await db.delete_one(note_collection, {"_id": obj_id})

    if result.modified_count == 1:
        return {"status": True, "message": "Note permanently deleted"}
    raise HTTPException(status_code=404, detail="Note not found")
