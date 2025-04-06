from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.services.telegram import TelegramBotService, send_telegram_message
from app.services.ai_service import get_ai_response, get_small_talk_response
from app.api.models import TelegramUpdate, Message
from app.services.conversation import conversation_state
from app.agent.nlp_agent import NLPAgent
from app.services.brain_service import brain_service

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()
telegram_service = TelegramBotService()
nlp_agent = NLPAgent()

access_token = None

@router.post("/test-webhook")
async def test_webhook(request: Request):
    """Test endpoint to verify webhook is working"""
    body = await request.json()
    print("Test webhook received:", body)
    return {"status": "ok"}


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram messages"""
    logger.info("========================")
    logger.info("Webhook endpoint hit!")
    logger.info(f"Received update: {update}")
    
    if not update.message:
        logger.info("No message in update")
        return {"status": "ok"}
    
    chat_id = update.message.chat.id
    user_message = update.message.text
    message_type = "text"
    
    if not user_message:
        logger.info("No text in message")
        await send_telegram_message(
            chat_id,
            "I can help you manage your notes and information. Please send me a text message!"
        )
        return {"status": "ok"}
    
    # Add user message to conversation history
    conversation_state.add_message(chat_id, "user", user_message, message_type)
    history = conversation_state.get_conversation_history(chat_id)
    logger.info(f"Conversation history: {history}")
    
    try:
        # First try sending a simple response to test message delivery
        logger.info("Attempting to send test response...")
        await send_telegram_message(
            chat_id,
            "I received your message! Let me process it...",
            parse_mode=None
        )
        
        # Check relevancy before extracting intent
        logger.info("Checking message relevancy...")
        relevancy_result = await nlp_agent.check_relevancy(user_message, history)
        logger.info(f"Relevancy result: {relevancy_result}")
        
        if not relevancy_result["relevant"]:
            logger.info("Message not relevant, getting small talk response...")
            ai_response = await get_small_talk_response(user_message, history)
            await send_telegram_message(chat_id, ai_response, parse_mode=None)
            conversation_state.add_message(chat_id, "assistant", ai_response)
            return {"status": "ok"}
        
        logger.info("Message relevant, extracting intent...")
        intent = await nlp_agent.extract_intent(user_message, history)
        logger.info(f"Extracted intent: {intent}")

        if intent["confirmation_needed"] is False:
            logger.info("No confirmation needed, getting AI response...")
            ai_response = await get_ai_response(intent, history)
            await send_telegram_message(chat_id, ai_response, parse_mode=None)
            conversation_state.add_message(chat_id, "assistant", ai_response)
            return {"status": "success"}
        else:
            logger.info("Confirmation needed, sending confirmation request...")
            confirmation_message = f"Would you like me to {intent['intent']}? Please confirm."
            await send_telegram_message(chat_id, confirmation_message, parse_mode=None)
            conversation_state.add_message(chat_id, "assistant", confirmation_message)
            return {"status": "confirmation_needed"}

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        try:
            await send_telegram_message(
                chat_id,
                "I apologize, but I'm having trouble processing your message right now. Please try again later.",
                parse_mode=None
            )
        except Exception as send_error:
            logger.error(f"Error sending error message: {str(send_error)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notes")
async def list_notes(query: str = None, tags: str = None):
    """List all notes, optionally filtered by search query or tags"""
    try:
        tag_list = tags.split(',') if tags else None
        notes = await brain_service.search_notes(query=query, tags=tag_list)
        return {"status": "success", "notes": notes}
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notes/{note_id}")
async def get_note(note_id: str):
    """Get a specific note by ID"""
    try:
        note = await brain_service.get_note(note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"status": "success", "note": note}
    except Exception as e:
        logger.error(f"Error getting note: {e}")
        raise HTTPException(status_code=500, detail=str(e))