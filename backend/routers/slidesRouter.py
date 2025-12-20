from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from config.database import db
from schemas.slideSchema import Slide, UpdateSlideRequest

slide_collection = db["slides"]

router = APIRouter(
    prefix="/slides",
    tags=["slides"]
)

@router.post("/", response_model=dict)
async def create_slide(slide: Slide):
    now = datetime.now(timezone.utc)
    slide_data = slide.model_dump()
    slide_data.update({"created_at": now, "updated_at": now})
    
    result = await slide_collection.insert_one(slide_data)
    slide_data["id"] = str(result.inserted_id)
    slide_data.pop("_id", None)
    
    return slide_data

@router.patch("/{slideId}", response_model=dict)
async def update_slide(slideId: str, slide: UpdateSlideRequest):
    try:
        obj_id = ObjectId(slideId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid slideId format")
    
    now = datetime.now(timezone.utc)
    update_data = slide.model_dump()
    update_data["updated_at"] = now
    
    result = await slide_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    updated_slide = await slide_collection.find_one({"_id": obj_id})
    updated_slide["id"] = str(updated_slide.pop("_id"))
    
    return updated_slide

@router.get("/getAll/{notebookId}", response_model=List[dict])
async def get_all_slides(notebookId: str):
    slides = []
    cursor = slide_collection.find(
        {"notebookId": notebookId},
        {"html_content": 0}
    ).sort("updated_at", -1)
    
    async for doc in cursor:
        slides.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        })
    
    return slides

@router.get("/{slideId}", response_model=dict)
async def get_slide(slideId: str):
    try:
        obj_id = ObjectId(slideId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid slideId format")
    
    doc = await slide_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.delete("/delete/{slideId}", response_model=dict)
async def delete_slide(slideId: str):
    try:
        obj_id = ObjectId(slideId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid slideId format")
    
    result = await slide_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    return {"message": "Slide deleted successfully"}
