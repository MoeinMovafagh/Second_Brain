from datetime import datetime
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.utils.helpers import format_conversation_history
from app.services.brain_service import brain_service
from litellm import acompletion
from typing import Dict
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ai_response(intent_data: Dict, conversation_history: list) -> str:
    """Generate AI response based on the intent and perform necessary actions"""
    try:
        if len(conversation_history) == 0:
            return "Sorry, I'm not sure how to respond to that."
        
        # Process the intent and perform corresponding actions
        intent = intent_data.get('intent', 'unknown')
        response_message = ""

        if intent == 'save':
            # Save new note
            note = await brain_service.save_note(
                title=intent_data.get('title', 'Untitled Note'),
                content=intent_data.get('content', ''),
                tags=intent_data.get('tags', [])
            )
            response_message = f"✅ Note saved successfully with ID: {note.id}"

        elif intent == 'update':
            # Update existing note
            note = await brain_service.update_note(
                note_id=intent_data.get('note_id'),
                title=intent_data.get('title'),
                content=intent_data.get('content'),
                tags=intent_data.get('tags')
            )
            response_message = f"✅ Note {note.id} updated successfully"

        elif intent == 'delete':
            # Delete note
            success = await brain_service.delete_note(intent_data.get('note_id'))
            response_message = "✅ Note deleted successfully" if success else "❌ Note not found"

        elif intent == 'query':
            # Search notes
            notes = await brain_service.search_notes(
                query=intent_data.get('search_query'),
                tags=intent_data.get('tags')
            )
            if notes:
                response_message = "📝 Here are the matching notes:\n\n"
                for note in notes[:5]:  # Limit to 5 results
                    response_message += f"- {note.title} (ID: {note.id})\n"
                if len(notes) > 5:
                    response_message += f"\n...and {len(notes) - 5} more notes."
            else:
                response_message = "No matching notes found."

        else:
            response_message = "I'm not sure how to handle that request. Please try again."

        return response_message
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again."


async def get_small_talk_response(user_message: str, conversation_history: list) -> str:
    """Handle non-task related conversation while guiding back to Second Brain functionality"""
    try:
        system_prompt = """
        You are a friendly AI assistant that helps users manage their Second Brain - a personal knowledge management system.
        The user has sent a message that isn't directly related to saving or retrieving information.
        
        Respond naturally but briefly, and try to guide the conversation back to how you can help them organize their knowledge.
        
        User message: {user_message}
        Conversation history: {conversation_history}
        """
        
        formatted_history = format_conversation_history(conversation_history)
        messages = [
            {
                "role": "system", 
                "content": system_prompt.format(
                    user_message=user_message,
                    conversation_history=formatted_history
                )
            },
            {"role": "user", "content": user_message}
        ]
        
        response = await acompletion(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error getting small talk response: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."