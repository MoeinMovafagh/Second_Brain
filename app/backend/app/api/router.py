from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.services.telegram import TelegramBotService, send_telegram_message
from app.services.ai_service import get_ai_response, get_small_talk_response
from app.api.models import TelegramUpdate
from app.services.conversation import conversation_state
from app.agent.nlp_agent import NLPAgent

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()
telegram_service = TelegramBotService()
nlp_agent = NLPAgent()

access_token = None


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram messages"""
    
    # logger.info(f"------------------------------------>Received update: {update}")
    if not update.message:
        return {"status": "ok"}
    
    chat_id = update.message["chat"]["id"]
    user_message = None
    message_type = "text"
    
    # Handle different message types
    if "text" in update.message:
        user_message = update.message["text"]
    
    if not user_message:
        await send_telegram_message(
            chat_id,
            "I'm sorry, I didn't understand that. Can you please rephrase your message?"
        )
        return {"status": "ok"}
    
    

    
    # Add user message to conversation history
    conversation_state.add_message(chat_id, "user", user_message, message_type)
    history = conversation_state.get_conversation_history(chat_id)
    
    # logger.info(f"---------------------Conversation history: {history}")
    
    # Check relevancy before extracting intent
    relevancy_result = await nlp_agent.check_relevancy(user_message, history)
    # logger.info(f"------------------>RELEVANCY:{relevancy_result}")
    if not relevancy_result["relevant"]:
        ai_response = await get_small_talk_response(user_message, history)
        await send_telegram_message(chat_id, ai_response)
        conversation_state.add_message(chat_id, "assistant", ai_response)
        return {"status": "ok"}  
    
    
    try:
        event_data = await nlp_agent.extract_intent(user_message, history)
        # logger.info(f"===========> Event data: {event_data}")

        # If no confirmation is needed, proceed with the action
        if event_data["confirmation_needed"] is False:
            if event_data["intent"] == "create":
                # Create event in Google Calendar
                s= 10