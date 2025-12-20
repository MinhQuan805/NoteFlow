from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Slide(BaseModel):
    title: str
    notebookId: str
    html_content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UpdateSlideRequest(BaseModel):
    title: Optional[str] = None
    html_content: Optional[str] = None
