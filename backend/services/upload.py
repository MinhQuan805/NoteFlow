from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException, status
from typing import List
from libs.cloudinary import upload_to_cloudinary
from libs.docling import create_file_embedding

async def upload_files(files: List[UploadFile]):
    results = []
    now = datetime.now(timezone.utc)

    accept_ext = ["pdf", "docx", "pptx", "txt", "md", "svg", "csv", "json"]

    for file in files:
        ext = file.filename.split(".")[-1].lower()

        if ext not in accept_ext:
            raise HTTPException(
                status_code=400,
                detail=f"File type .{ext} not supported"
            )

        # Upload file to Cloudianry
        # cloudinary_info = await upload_to_cloudinary(file)
        # Embedding
        embed_info = await create_file_embedding(file)
        print(embed_info)
        # Merge data
        results.append({
            # **cloudinary_info,
            **embed_info,
            "checked": True,
            "created_at": now,
            "updated_at": now
        })

    return results
