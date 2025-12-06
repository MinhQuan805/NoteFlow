from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class MessagePart(BaseModel):
    type: Literal["text", "code", "image", "source-url", "reasoning"]
    text: str

class MessageItem(BaseModel):
    id: str
    role: Literal["user", "system", "assistant"]
    parts: List[MessagePart]

class Conversation(BaseModel):
    title: str = ''
    notebookId: str
    messages: List[MessageItem]  # Message List
    created_at: datetime
    updated_at: datetime
    deleted: bool = False
    deleted_at: Optional[datetime] = None
    expireAt: Optional[datetime] = None
