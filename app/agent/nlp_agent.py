from datetime import datetime
from litellm import acompletion
from app.utils.helpers import format_conversation_history
from app.config import OPENAI_API_KEY, OPENAI_MODEL
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPAgent:
    def __init__(self):
        self.system_prompt = """
            You are an intelligent assistant helping users manage their Second Brain - a personal knowledge management system.
            Your role is to help users save, organize, and retrieve their notes, documents, and information.

            Return a JSON object with the following fields:
            - intent: The user's intent (save, update, delete, query)
            - title: The title/name of the note or document (if applicable)
            - content: The content to save or update (if applicable)
            - tags: List of relevant tags for categorizing the content
            - search_query: The search terms when querying (if applicable)
            - confirmation_needed: Whether user confirmation is needed (true/false)

            Here is the conversation history:
            {conversation_history}

            Now, extract what should be done based on the most recent message.

            JSON:
        """
        
    async def check_relevancy(self, user_message: str, history: list) -> dict:
        """Check if the user message is relevant to Second Brain tasks."""
        
        system_prompt = '''
        You are a classifier that determines if a user message is relevant to Second Brain tasks.
        Second Brain-related tasks include:
        - Saving information (e.g., "Save this note", "Remember this", "Store this information")
        - Updating saved content (e.g., "Update my note", "Edit this document")
        - Deleting content (e.g., "Delete this note", "Remove this information")
        - Querying/retrieving information (e.g., "What notes do I have?", "Find information about X")
        - Organizing content (e.g., "Tag this note", "Categorize this")

        Return a JSON object with:
        - "relevant": true/false
        - "reason": A short explanation of why it's relevant or not.
        
        Consider the conversation history for context: "{conversation_history}"

        JSON Response:
        '''

        formatted_history = format_conversation_history(history)
        
        try:
            response = await acompletion(
                model=OPENAI_MODEL,
                api_key=OPENAI_API_KEY,
                messages=[
                    {"role": "system", "content": system_prompt.format(conversation_history=formatted_history)},
                    {"role": "user", "content": f"User message: {user_message}"}
                ]
            )

            relevancy_result = response["choices"][0]["message"]["content"]
            return json.loads(relevancy_result)
        except Exception as e:
            logger.error(f"Error checking relevancy: {e}")
            return {"relevant": False, "reason": "Failed to process response"}

    async def extract_intent(self, user_message, conversation_history):
        """Process user message and extract Second Brain intent and details"""
        try:
            formatted_history = format_conversation_history(conversation_history)
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

            system_message = self.system_prompt.format(
                conversation_history=formatted_history,
                current_date=current_datetime
            )

            response = await acompletion(
                model=OPENAI_MODEL,
                api_key=OPENAI_API_KEY,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result = response['choices'][0]['message']['content']
            parsed_result = json.loads(result)
            return parsed_result
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return {
                "intent": "unknown",
                "error": str(e),
                "confirmation_needed": True
            }