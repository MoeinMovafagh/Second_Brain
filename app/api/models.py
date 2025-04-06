from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class Chat(BaseModel):
    id: int
    type: str
    
class Message(BaseModel):
    message_id: int
    chat: Chat
    text: Optional[str] = None

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Message] = None

class TelegramMessage(BaseModel):
    chat_id: int
    message: str
    message_id: int

class Note(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class DataResponse(BaseModel):
    success: bool
    message: str
    confirmation_needed: bool
    data: Optional[Dict[str, Any]] = None
    note_id: Optional[str] = None
    notes: Optional[List[Note]] = None