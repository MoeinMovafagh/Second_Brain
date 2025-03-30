def format_conversation_history(history: list) -> str:
        """Format the conversation history into a structured format"""
        formatted_history = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in history]
        )
        return formatted_history
    