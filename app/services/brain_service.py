import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.api.models import Note
import logging

logger = logging.getLogger(__name__)

class BrainService:
    def __init__(self):
        self.data_dir = "data/notes"
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_note_path(self, note_id: str) -> str:
        """Get the full path for a note file"""
        return os.path.join(self.data_dir, f"{note_id}.json")

    async def save_note(self, title: str, content: str, tags: List[str] = [], metadata: Dict[str, Any] = {}) -> Note:
        """Save a new note"""
        try:
            note = Note(
                id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                title=title,
                content=content,
                tags=tags,
                metadata=metadata
            )
            
            with open(self._get_note_path(note.id), 'w', encoding='utf-8') as f:
                json.dump(note.dict(), f, default=str)
            
            return note
        except Exception as e:
            logger.error(f"Error saving note: {e}")
            raise

    async def update_note(self, note_id: str, title: Optional[str] = None, 
                         content: Optional[str] = None, tags: Optional[List[str]] = None) -> Note:
        """Update an existing note"""
        try:
            note_path = self._get_note_path(note_id)
            if not os.path.exists(note_path):
                raise FileNotFoundError(f"Note {note_id} not found")

            with open(note_path, 'r', encoding='utf-8') as f:
                note_data = json.load(f)
                
            note = Note(**note_data)
            if title:
                note.title = title
            if content:
                note.content = content
            if tags is not None:
                note.tags = tags
            note.updated_at = datetime.now()

            with open(note_path, 'w', encoding='utf-8') as f:
                json.dump(note.dict(), f, default=str)

            return note
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            raise

    async def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        try:
            note_path = self._get_note_path(note_id)
            if os.path.exists(note_path):
                os.remove(note_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            raise

    async def get_note(self, note_id: str) -> Optional[Note]:
        """Retrieve a specific note"""
        try:
            note_path = self._get_note_path(note_id)
            if not os.path.exists(note_path):
                return None

            with open(note_path, 'r', encoding='utf-8') as f:
                note_data = json.load(f)
                return Note(**note_data)
        except Exception as e:
            logger.error(f"Error retrieving note: {e}")
            raise

    async def search_notes(self, query: str = None, tags: List[str] = None) -> List[Note]:
        """Search notes by content and/or tags"""
        try:
            notes = []
            for filename in os.listdir(self.data_dir):
                if not filename.endswith('.json'):
                    continue

                with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                    note_data = json.load(f)
                    note = Note(**note_data)

                    # Filter by query
                    if query and query.lower() not in note.title.lower() and query.lower() not in note.content.lower():
                        continue

                    # Filter by tags
                    if tags and not all(tag in note.tags for tag in tags):
                        continue

                    notes.append(note)

            return sorted(notes, key=lambda x: x.updated_at, reverse=True)
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            raise

brain_service = BrainService()