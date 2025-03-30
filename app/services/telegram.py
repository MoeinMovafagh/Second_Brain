import httpx
from app.config import TELEGRAM_API_TOKEN

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}"

def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2"""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def send_telegram_message(chat_id: int, text: str, parse_mode: str = "MarkdownV2"):
        """Send message to Telegram chat"""
        # escaped_text = escape_markdown(text)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_BASE}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    parse_mode: parse_mode,
                }
            )
            return response.json()


class TelegramBotService:
    def start(self):
        print("Telegram bot started...")  # For debugging

    def stop(self):
        print("Telegram bot stopped...")  # For debugging
        
    
    

        
        

        
        
