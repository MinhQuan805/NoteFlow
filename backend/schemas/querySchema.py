from pydantic import BaseModel
from typing import List, Optional
from .conversationSchema import MessageItem

class QueryRequest(BaseModel):
    message_item: MessageItem
    query: str
    file_filters: Optional[List[str]] = None


class QueryResponse(BaseModel):
    response_message: MessageItem
    intent: str
    mode: str
