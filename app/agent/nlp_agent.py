from datetime import datetime
from litellm import acompletion
from app.utils.helpers import format_conversation_history
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLPAgent:
    def __init__(self):
        self.system_prompt = """
            You are an intelligent assistant helping users manage their calendar.
            Extract event details from the conversation. 

            Return a JSON object with the following fields:
            - intent: The user's intent (create, update, delete, query)
            - event_name: The name/title of the event (can be inferred from the conversation)
            - date: The date of the event in YYYY-MM-DD format. If the user refers to a time period such as "next week", "next Monday", or any relative date, infer the specific date(s). For example, if the user says "next Monday", the date should be the next Monday after the current date. If no date is provided, use the current date or the best possible inferred date.
            - start_time: The start time in HH:MM format (if provided or inferred from the context)
            - end_time: The end time in HH:MM format (if provided or inferred from the context)
            - description: Any additional details about the event (inferred from conversation)
            - participants: List of people involved (if mentioned or inferred)
            - confirmation_needed: Whether user confirmation is needed (true/false)

            In the case of vague or ambiguous date references like "next week" or "next Monday":
            - For "next week", the date should be set to the beginning of the next week (the first day of the week, e.g., next Monday).
            - For "next Monday", infer the actual date of the upcoming Monday, and ensure it's formatted as YYYY-MM-DD.
            - If the user asks for an event within a specific range (e.g., "next week" or "this month"), set the date range as needed.

            Make sure to carefully extract the date when ambiguous phrases are used, like "next week", "today", "tomorrow", "next month", etc.

            Here is the conversation history:
            {conversation_history}

            Now, extract the event details based on the most recent message.

            current date is: {current_date}

            JSON:
        """

        
    async def check_relevancy(self, user_message: str, history: list) -> dict:
        """Check if the user message is relevant to calendar tasks."""
        
        system_prompt = """
        You are a classifier that determines if a user message is relevant to calendar-related tasks.
        Calendar-related tasks include scheduling, updating, deleting, or querying events.
        
        If the message is related to scheduling events (e.g., "Schedule a meeting", "Book an appointment"),
        updating events (e.g., "Change my meeting time", "Move my event"),
        deleting events (e.g., "Cancel my meeting", "Remove this event"),
        or querying events (e.g., "What do I have tomorrow?", "Show my schedule"), then it is relevant.

        Otherwise, it is irrelevant. Irrelevant messages include:
        - Greetings ("Hi", "Hello", "Good morning")
        - Small talk ("How are you?", "What's up?")
        - Off-topic questions ("Tell me a joke", "What's your favorite color?")
        - Unclear or ambiguous statements ("Okay", "Sure", "Hmm")

        Return a JSON object with:
        - "relevant": true/false
        - "reason": A short explanation of why it's relevant or not.
        
        Remember to consider the relevance of user message in the context of the conversation history!
        
        Conversation history: "{conversation_history}"

        JSON Response:
        """

        formatted_history = format_conversation_history(history)
        
        response = await acompletion(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt.format(conversation_history=formatted_history)},
                {"role": "user", "content": f"User message: {user_message}"}
            ],
        )

        try:
            relevancy_result = response["choices"][0]["message"]["content"]
            return json.loads(relevancy_result)
        except Exception as e:
            return {"relevant": False, "reason": "Failed to process response"}


    async def extract_intent(self, user_message, conversation_history):
        """Process user message and extract calendar intent and details"""
        try:
            formatted_history = format_conversation_history(conversation_history)
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

            system_message = self.system_prompt.format(conversation_history=formatted_history, current_date=current_datetime)

            response = await acompletion(
                model="gpt-4o",
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
            print(f"Error extracting intent: {e}")
            return {
                "intent": "unknown",
                "error": str(e),
                "confirmation_needed": True
            }