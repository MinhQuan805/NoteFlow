from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from config.database import db
from schemas.slideSchema import Slide, UpdateSlideRequest

slide_collection = "slides"

router = APIRouter(
    prefix="/slides",
    tags=["slides"]
)

@router.post("/", response_model=dict)
async def create_slide(slide: Slide):
    now = datetime.now(timezone.utc)
    slide_data = slide.model_dump()
    slide_data["created_at"] = now
    slide_data["updated_at"] = now
    slide_data["_id"] = str(ObjectId())  # Generate ID for LocalDB
    
    result = await db.insert_one(slide_collection, slide_data)
    slide_data["id"] = str(result.inserted_id)
    slide_data.pop("_id", None)
    
    return slide_data

@router.patch("/{slideId}", response_model=dict)
async def update_slide(slideId: str, slide: UpdateSlideRequest):
    now = datetime.now(timezone.utc)
    update_data = slide.model_dump(exclude_unset=True)
    update_data["updated_at"] = now
    
    result = await db.update_one(
        slide_collection,
        {"_id": slideId},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    updated_slide = await db.find_one(slide_collection, {"_id": slideId})
    if updated_slide:
        updated_slide["id"] = updated_slide.pop("_id", slideId)
    
    return updated_slide

@router.get("/getAll/{notebookId}", response_model=List[dict])
async def get_all_slides(notebookId: str):
    slides = []
    cursor = await db.find(
        slide_collection,
        {"notebookId": notebookId}
    )
    
    for doc in cursor:
        slides.append({
            "id": doc.get("_id", ""),
            "title": doc.get("title", ""),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at")
        })
    
    # Sort by updated_at descending
    slides.sort(key=lambda x: x.get("updated_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return slides

@router.get("/{slideId}", response_model=dict)
async def get_slide(slideId: str):
    doc = await db.find_one(slide_collection, {"_id": slideId})
    if not doc:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    doc["id"] = doc.pop("_id", slideId)
    return doc

@router.delete("/delete/{slideId}", response_model=dict)
async def delete_slide(slideId: str):
    result = await db.delete_one(slide_collection, {"_id": slideId})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    return {"message": "Slide deleted successfully"}
