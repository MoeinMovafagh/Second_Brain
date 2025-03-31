from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict] = None

class TelegramMessage(BaseModel):
    chat_id: int
    message: str
    message_id: int

class ConfirmationRequest(BaseModel):
    chat_id: int
    confirmed: bool
    event_data: Dict[str, Any]

class EventResponse(BaseModel):
    success: bool
    message: str
    confirmation_needed: bool
    event_data: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    event_link: Optional[str] = None
    events: Optional[List[Dict[str, Any]]] = None