import os
import cloudinary
from cloudinary.uploader import upload, destroy
from fastapi import UploadFile, HTTPException, status
from typing import List
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Cloudinary Config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Function for pload file
async def upload_files(files: List[UploadFile]):
    uploaded = []
    now = datetime.now(timezone.utc)
    # Accepted Extension
    accept_ext = ["pdf", "docx", "pptx", "txt", "md", "svg", "csv", "json"]
    try:
        for file in files:
            ext = file.filename.split(".")[-1].lower()
            if ext in accept_ext:
                upload_result = upload(
                    file.file,
                    folder="Note_Learning",  
                    resource_type="raw"
                )
                uploaded.append({
                    "public_id": upload_result.get("public_id").split("/")[-1], # Split folder and key, get only key,
                    "title": file.filename,
                    "url": upload_result.get("secure_url"),
                    "format": file.filename.split(".")[-1],
                    "checked": True,
                    "created_at": now,
                    "updated_at": now,
                })

        return uploaded

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}"
        )
    
async def delete_file_cloud(public_id: str):
    try:
        folder = "Note_Learning"
        full_public_id = f"{folder}/{public_id}"
        result = destroy(full_public_id, resource_type="raw")
        if result.get("result") not in ["ok", "not found"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete from Cloudinary: {result}"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )