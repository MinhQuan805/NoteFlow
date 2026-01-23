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
from ai.rag_manager import RAGManager

file_collection = "files"

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/files",
    tags=["files"]
)

# Cleanup Old Files
async def cleanup_expired_files(notebookId: str):
    now = datetime.now(timezone.utc)
    files = await db.find_one(file_collection, {"notebookId": notebookId})
    if not files:
        return

    for file in files.get("file_list", []):
        updated_at = file.get("updated_at")
        if updated_at is None:
            continue
        # Handle string dates
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                continue
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        if updated_at + timedelta(days=7) < now:
            await delete_cloud_file(file["public_id"], "raw")
            await db.update_one(
                file_collection,
                {"notebookId": notebookId},
                {"$pull": {"file_list": {"public_id": file["public_id"]}}}
            )

# Get All File
@router.get("/{notebookId}")
async def get_all_files(notebookId: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_expired_files, notebookId)
    files = await db.find_one(file_collection, {"notebookId": notebookId})
    if not files:
        return []

    sorted_files = sorted(
        files.get("file_list", []), 
        key=lambda f: str(f.get("updated_at", "")),  # Convert to string for consistent comparison
        reverse=True
    )
    return sorted_files

# Upload file
@router.post("/upload_files/{notebookId}")
async def upload_endpoint(notebookId: str, files: List[UploadFile] = File(...)):
    rag = RAGSystem(config_path="ai/config.yaml", notebook_id=notebookId)
    try:
        # Get per-notebook RAG instance
        rag = RAGManager.get_rag(notebookId)
        
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
        uploaded_files = await upload_files(files)

        # Update database with uploaded file metadata
        now = datetime.now(timezone.utc)
        await db.update_one(
            file_collection,
            {"notebookId": notebookId},
            {
                "$push": {"file_list": {"$each": uploaded_files}},
                "$set": {"updated_at": now}
            },
            upsert=True
        )

        return {
            "message": f"Uploaded and ingested {len(saved_paths)} files successfully.",
            "uploaded_files": uploaded_files,
            "ingested_files": [os.path.basename(p) for p in saved_paths]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload File Error: {str(e)}")

# Sync web content fetcher (proven approach from main_branch)
import requests
from bs4 import BeautifulSoup

def fetch_web_content(url: str) -> str:
    """Fetch and extract text content from a URL"""
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"[Discover] Failed to fetch {url}: {e}")
        return ""

# Upload source URL
@router.post("/upload_url/{notebookId}")
async def upload_url_endpoint(notebookId: str, sources: List[SingleFile] = Body(...)):
    rag = RAGSystem(config_path="ai/config.yaml", notebook_id=notebookId)
    try:
        # Get per-notebook RAG instance
        rag = RAGManager.get_rag(notebookId)
        
        now = datetime.now(timezone.utc)
        newSources = []
        ingested_count = 0
        
        for source in sources:
            try:
                # Fetch web content
                print(f"[Discover] Fetching: {source.url}")
                content = fetch_web_content(source.url)
                
                if content:
                    # Save to temp file for ingestion
                    temp_path = os.path.join(UPLOAD_DIR, f"{source.public_id}.txt")
                    with open(temp_path, "w", encoding="utf-8") as f:
                        f.write(f"Source: {source.title}\nURL: {source.url}\n\n{content}")
                    
                    # Ingest into RAG with title as source name (for filtering)
                    rag.ingest([temp_path], source_names={temp_path: source.title})
                    ingested_count += 1
                    print(f"[Discover] Ingested: {source.title} ({len(content)} chars)")
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    
                    # Only add to database if successfully ingested
                    source_dict = source.model_dump()
                    source_dict["created_at"] = now
                    source_dict["updated_at"] = now
                    newSources.append(source_dict)
                else:
                    print(f"[Discover] No content for: {source.title} - skipping from source list")
                
            except Exception as e:
                print(f"[Discover] Error processing {source.title}: {e} - skipping from source list")
                continue
        
        # Update database
        if newSources:
            await db.update_one(
                file_collection,
                {"notebookId": notebookId},
                {
                    "$push": {"file_list": {"$each": newSources}},
                    "$set": {"updated_at": now}
                }
            )
        
        return {
            "message": f"Uploaded {len(newSources)} sources, ingested {ingested_count} into RAG",
            "sources": newSources
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Upload Url Error: {str(e)}")

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

    result = await db.insert_one(file_collection, new_file_storage)
    fileStorageId = str(result.inserted_id)
    return {"fileStorageId": fileStorageId}

# Delete single file upload permanently
@router.delete("/delete/{notebookId}/{public_id}/{format}")
async def delete_single_file(notebookId: str, public_id: str, format: str):
    if format != "url":
        await delete_cloud_file(public_id, "raw")

    result = await db.update_one(
        file_collection,
        {"notebookId": notebookId},
        {"$pull": {"file_list": {"public_id": public_id}}}
    )

    if result.modified_count == 1:
        return {"status": True, "message": "File upload deleted permanently"}
    else:
        raise HTTPException(status_code=404, detail="File upload not found")
    

# Update title for file (using fetch-update-save pattern for LocalDB compatibility)
@router.patch("/update_title/{notebookId}/{public_id}")
async def update_title(notebookId: str, public_id: str, title: str):
    try:
        doc = await db.find_one(file_collection, {"notebookId": notebookId})
        if not doc:
            raise HTTPException(status_code=404, detail="File storage not found")
        
        file_list = doc.get("file_list", [])
        updated = False
        for f in file_list:
            if f.get("public_id") == public_id:
                f["title"] = title
                f["updated_at"] = datetime.now(timezone.utc)
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="File not found")
        
        await db.update_one(
            file_collection,
            {"notebookId": notebookId},
            {"$set": {"file_list": file_list}}
        )
        
        return {"status": True, "message": "File title updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update checked for file (using fetch-update-save pattern for LocalDB compatibility)
@router.patch("/update_checked/{notebookId}/{public_id}")
async def update_checked(notebookId: str, public_id: str, checked: bool):
    now = datetime.now(timezone.utc)
    
    doc = await db.find_one(file_collection, {"notebookId": notebookId})
    if not doc:
        raise HTTPException(status_code=404, detail="File storage not found")
    
    file_list = doc.get("file_list", [])
    updated = False
    for f in file_list:
        if f.get("public_id") == public_id:
            f["checked"] = checked
            f["updated_at"] = now
            updated = True
            break
    
    if not updated:
        raise HTTPException(status_code=404, detail="File not found")
    
    await db.update_one(
        file_collection,
        {"notebookId": notebookId},
        {"$set": {"file_list": file_list}}
    )
    
    return {"status": True, "message": f"Checked updated to {checked}"}


import aiohttp
from fastapi.responses import Response
import mimetypes

@router.get("/download_file/{notebookId}/{public_id}")
async def download_file(notebookId: str, public_id: str):
    file_doc = await db.find_one(file_collection, {"notebookId": notebookId})
    if not file_doc:
        raise HTTPException(status_code=404, detail="Notebook not found")

    file_item = next((f for f in file_doc.get("file_list", []) if f["public_id"] == public_id), None)
    if not file_item:
        raise HTTPException(status_code=404, detail="File not found")

    file_url = file_item["url"]
    title = file_item["title"]

    content_type, _ = mimetypes.guess_type(title)
    if not content_type:
        content_type = "application/octet-stream"
        
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch file")

            data = await response.read()

            return Response(
                content=data,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; title={title}"
                }
            )
