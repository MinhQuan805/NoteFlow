from typing import List, Union, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

Styles = Dict[str, bool]

class StyledText(BaseModel):
    type: str = "text"
    text: str
    styles: Optional[Styles] = Field(default_factory=dict)

class Link(BaseModel):
    type: str = "link"
    content: List[StyledText]
    href: str

class CustomInlineContent(BaseModel):
    type: str
    content: Optional[List[StyledText]] = None
    props: Dict[str, Union[bool, int, float, str]] = Field(default_factory=dict)

InlineContent = Union[Link, StyledText, CustomInlineContent]

class TableContent(BaseModel):
    rows: Optional[List[List[StyledText]]] = None

class Note(BaseModel):
    id: str
    type: str
    props: Dict[str, Union[bool, int, float, str]] = Field(default_factory=dict)
    content: Optional[Union[List[InlineContent], TableContent]] = None
    children: List["Note"] = Field(default_factory=list)

# Rebuild the model to resolve forward references (required for self-referential models)
Note.model_rebuild()

class NoteContainer(BaseModel):
    title: str
    notebookId: str
    blocks : List[Note] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime
