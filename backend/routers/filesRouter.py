from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from schemas.fileSchema import SingleFile
from config.database import db
from datetime import datetime, timedelta, timezone
from typing import List
from libs.cloudinary import delete_cloud_file
from libs.cloudinary import upload_files
from fastapi import Body
import os
import shutil
from ai.rag_system import RAGSystem

rag = RAGSystem("ai/config.yaml")
file_collection = db["files"]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/files",
    tags=["files"]
)

# Cleanup Old Files
async def cleanup_expired_files(notebookId: str):
    now = datetime.now(timezone.utc)
    files = await file_collection.find_one({"notebookId": notebookId})
    if not files:
        return

    for file in files.get("file_list", []):
        updated_at = file["updated_at"]
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        if updated_at + timedelta(days=7) < now:
            await delete_cloud_file(file["public_id"], "raw")
            await file_collection.update_one(
                {"notebookId": notebookId},
                {"$pull": {"file_list": {"public_id": file["public_id"]}}}
            )

# Get All File
@router.get("/{notebookId}")
async def get_all_files(notebookId: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_expired_files, notebookId)
    files = await file_collection.find_one(
        {"notebookId": notebookId},
        {"_id": 0, "file_list": 1}
    )
    if not files:
        return []

    sorted_files = sorted(files.get("file_list", []), key=lambda f: f["updated_at"], reverse=True)
    return sorted_files

# Upload file

@router.post("/upload_files/{notebookId}")
async def upload_endpoint(notebookId: str, files: List[UploadFile] = File(...)):
    try:
        # Save physical files locally and collect their paths for ingestion
        saved_paths = []
        for file in files:
            file.file.seek(0)
            
            file_path = os.path.join(UPLOAD_DIR, file.filename)

            # Write file content to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                buffer.flush()
                os.fsync(buffer.fileno())

            saved_paths.append(file_path)

        # Ingest the saved files into the RAG pipeline
        rag.ingest(saved_paths)

        for f in files:
            f.file.seek(0)

        # Upload files (store them in your storage system)
        # This returns metadata for each uploaded file
        uploaded_files = await upload_files(files)

        # Update database with uploaded file metadata
        now = datetime.now(timezone.utc)
        await file_collection.update_one(
            {"notebookId": notebookId},
            {
                # Append the new files into the file_list array
                "$push": {"file_list": {"$each": uploaded_files}},
                # Update the timestamp
                "$set": {"updated_at": now}
            },
            upsert=True  # Create the document if it doesn't exist
        )

        # Return success response
        return {
            "message": f"Uploaded and ingested {len(saved_paths)} files successfully.",
            "uploaded_files": uploaded_files,
            "ingested_files": [os.path.basename(p) for p in saved_paths]
        }
    except:
        raise HTTPException(status_code=400, detail="Upload File Error")

# @router.post("/ingest")
# async def ingest_files(files: List[UploadFile] = File(...)):
#     """
#     Ingest uploaded PDF files.
#     """
#     saved_paths = []
#     try:
#         for file in files:
#             file_path = os.path.join(UPLOAD_DIR, file.filename)
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
#             saved_paths.append(file_path)
        
#         rag.ingest(saved_paths)
        
#         return {
#             "message": f"Successfully ingested {len(saved_paths)} files.",
#             "files": [os.path.basename(p) for p in saved_paths]
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Upload source
@router.post("/upload_url/{notebookId}")
async def upload_url_endpoint(notebookId: str, sources: List[SingleFile] = Body(...)):
    try:
        now = datetime.now(timezone.utc)
        newSources = []
        for source in sources:
            source_dict = source.model_dump()
            source_dict["created_at"] = now
            source_dict["updated_at"] = now
            newSources.append(source_dict)
        await file_collection.update_one(
            {"notebookId": notebookId},
            {
                "$push": {"file_list": {"$each": newSources}},
                "$set": {"updated_at": now}
            }
        )
        return newSources
    except:
        raise HTTPException(status_code=400, detail="Upload Url Error")

# Create new file storage
@router.post("/create/{notebookId}")
async def create_file_storage(notebookId: str):
    now = datetime.now(timezone.utc)
    new_file_storage = {
        "notebookId": notebookId,
        "file_list": [],
        "created_at": now,
        "updated_at": now,
    }

    result = await file_collection.insert_one(new_file_storage)
    fileStorageId = str(result.inserted_id)
    return {"fileStorageId": fileStorageId}

# Delete single file upload permanently
@router.delete("/delete/{notebookId}/{public_id}/{format}")
async def delete_single_file(notebookId: str, public_id: str, format: str):
    if format != "url":
        await delete_cloud_file(public_id, "raw")

    result = await file_collection.update_one(
        {"notebookId": notebookId},
        {"$pull": {"file_list": {"public_id": public_id}}}
    )

    if result.modified_count == 1:
        return {"status": True, "message": "File upload deleted permanently"}
    else:
        raise HTTPException(status_code=404, detail="File upload not found")
    

# Update title for file
@router.patch("/update_title/{notebookId}/{public_id}")
async def update_title(notebookId: str, public_id: str, title: str):
    try:
        result = await file_collection.update_one(
            {"notebookId": notebookId, "file_list.public_id": public_id},
            {
                "$set": {
                    "file_list.$.title": title,
                    "file_list.$.updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.modified_count == 1:
            return {"status": True, "message": "File title updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update checked for file
@router.patch("/update_checked/{notebookId}/{public_id}")
async def update_checked(notebookId: str, public_id: str, checked: bool):
    now = datetime.now(timezone.utc)
    result = await file_collection.update_one(
        {"notebookId": notebookId, "file_list.public_id": public_id},
        {"$set": {"file_list.$.checked": checked, "file_list.$.updated_at": now}}
    )
    if result.modified_count == 1:
        return {"status": True, "message": f"Checked updated to {checked}"}
    raise HTTPException(status_code=404, detail="File not found")


import aiohttp
from fastapi.responses import Response
import mimetypes

@router.get("/download_file/{notebookId}/{public_id}")
async def download_file(notebookId: str, public_id: str):
    # Find notebook in MongoDB
    file_doc = await file_collection.find_one({"notebookId": notebookId})
    if not file_doc:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Find file in file_list
    file_item = next((f for f in file_doc.get("file_list", []) if f["public_id"] == public_id), None)
    if not file_item:
        raise HTTPException(status_code=404, detail="File not found")

    file_url = file_item["url"]
    title = file_item["title"]

    content_type, _ = mimetypes.guess_type(title)
    if not content_type:
        content_type = "application/octet-stream"
    # Download file data from Cloudinary
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch file")

            # Read all data
            data = await response.read()

            # Return a response containing that data
            return Response(
                content=data,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; title={title}"
                }
            )
