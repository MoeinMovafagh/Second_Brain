from datetime import datetime
from typing import Dict

class ConversationState:
    def __init__(self):
        self.conversations: Dict[int, list] = {}
        
    def add_message(self, user_id: int, role: str, content: str, message_type: str = "text"):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": role,
            "content": content,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_conversation_history(self, user_id: int, max_messages: int = 10) -> list:
        return self.conversations.get(user_id, [])[-max_messages:]

conversation_state = ConversationState()