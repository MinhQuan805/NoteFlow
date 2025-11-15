from fastapi import APIRouter, HTTPException, UploadFile, status
from schemas.notebookSchema import Notebook
from config.database import db
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from routers.conversationsRouter import create_conversation
from routers.filesRouter import create_file_storage
from libs.cloudinary import upload_image, delete_cloud_file
from typing import Optional

notebook_collection = db["notebooks"]
conversation_collection = db["conversations"]

file_collection = db["files"]
router = APIRouter(
    prefix="/notebooks",
    tags=["notebooks"]
)


# Get all notebooks
@router.get("/", response_model=list)
async def get_all_notebooks():
    docs = notebook_collection.find({}, sort=[("updated_at", -1)])
    notebooks = []
    async for doc in docs:
        notebooks.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "avatar": doc.get("avatar", ""),
            "idAvatar": doc.get("idAvatar", ""),
            "bgcolor": doc.get("bgcolor", ""),
            "created_at": doc["created_at"],
            "updated_at": doc.get("updated_at")
        })
    return notebooks


# Get a single notebook by ID
@router.get("/{notebookId}", response_model=dict)
async def get_notebook(notebookId: str):
    doc = await notebook_collection.find_one({"_id": ObjectId(notebookId)})
    if not doc:
        raise HTTPException(status_code=404, detail="Notebook not found")
    now = datetime.now(timezone.utc)
    await notebook_collection.update_one(
        {"_id": ObjectId(notebookId)},
        {"$set": {"updated_at": now}}
    )
    conversation = await conversation_collection.find_one(
        {"notebookId": notebookId},
    )
    return {
        "conversationId": str(conversation["_id"]),
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at")
    }


# Create a new notebook
@router.post("/create")
async def create_notebook(upload: Notebook):
    now = datetime.now(timezone.utc)
    data = upload.model_dump()

    # Hash password
    # if data.get("password"):
    #     hashed_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    #     data["password"] = hashed_pw.decode("utf-8")
    data.update({"created_at": now, "updated_at": now})

    result = await notebook_collection.insert_one(data)

    notebookId = str(result.inserted_id)

    # Create new conversation for
    conversation = await create_conversation(notebookId)

    # Create new file storage for
    fileStorage = await create_file_storage(notebookId)

    return {"notebookId": notebookId, "conversationId": conversation["conversationId"], "fileStorageId": fileStorage["fileStorageId"]}

# Update title of notebook
@router.patch("/update_title/{notebookId}")
async def update_title(notebookId: str, title: str):
    try:
        notebook_obj_id = ObjectId(notebookId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notebook_id format")
    
    result = await notebook_collection.update_one(
        {"_id": notebook_obj_id},
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
    
# Update a notebook
@router.patch("/{notebookId}", response_model=Notebook)
async def update_notebook(notebookId: str, upload: Notebook):
    try:
        notebook_obj_id = ObjectId(notebookId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notebookId format")
    now = datetime.now(timezone.utc)
    result = await notebook_collection.update_one(
        {"_id": notebook_obj_id},
        {"$set": {**upload.model_dump(exclude_unset=True), "updated_at": now}}
    )

    if result.modified_count == 1:
        doc = await notebook_collection.find_one({"_id": ObjectId(notebookId)})
        return Notebook(
            title=doc["title"],
            avatar=doc.get("avatar", ""),
            bgcolor=doc.get("bgcolor", ""),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at")
        )
    else:
        raise HTTPException(status_code=404, detail="Notebook not found")

@router.post("/upload_image")
async def handle_upload(image: UploadFile):
    try:
        res = await upload_image(image)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
# Delete a notebook
@router.delete("/delete/{notebookId}/{idAvatar}")
async def delete_notebook(notebookId: str, idAvatar: str):
    if idAvatar != "noAvatar":
        await delete_cloud_file(idAvatar, "image")
    result = await notebook_collection.delete_one({"_id": ObjectId(notebookId)})
    # Delete file storage for notebook
    if result.deleted_count == 1:
        return {"status": True, "message": "Notebook deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Notebook not found")    