from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SingleFile(BaseModel):
    public_id: Optional[str] = ''
    title: str
    url: str
    format: str
    content: Optional[str] = None
    embedding: Optional[List[float]] = None
    checked: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class FileListStorage(BaseModel):
    notebookId: str
    file_list: List[SingleFile] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime