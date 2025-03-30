from datetime import datetime
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.prompts import agent_system_prompt, small_talk_system_prompt
from app.utils.helpers import format_conversation_history
from litellm import acompletion
from typing import Dict
import httpx
import logging
import json
import litellm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_ai_response(event_data: Dict, conversation_history: list) -> str:
    
    if len(conversation_history) == 0:
        return "Sorry, I'm not sure how to respond to that."
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    messages = [{"role": "system", "content": agent_system_prompt.format(event_data=event_data, current_date=current_date)}]
    user_message = conversation_history[-1]["content"]
    messages.append({"role": "user", "content": user_message})
    
    # for msg in conversation_history[-1:]:
    #     messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
    
    response = await acompletion(
        api_key=OPENAI_API_KEY, model=OPENAI_MODEL, messages=messages, max_tokens=200
    )
    logger.info(f'------------------------------------>Response: {response["choices"][0]["message"]["content"]}')
    return response["choices"][0]["message"]["content"]


async def get_small_talk_response(user_message: str, conversation_history: list) -> str:
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    formatted_history = format_conversation_history(conversation_history)
    messages = [{"role": "system", "content": small_talk_system_prompt.format(user_message=user_message, conversation_history=formatted_history, current_date=current_date)}]
    messages.append({"role": "user", "content": user_message})
    
    response = await acompletion(
        api_key=OPENAI_API_KEY, model=OPENAI_MODEL, messages=messages, max_tokens=200
    )
    return response["choices"][0]["message"]["content"]