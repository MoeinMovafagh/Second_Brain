import httpx
from app.config import TELEGRAM_API_TOKEN
import logging

logger = logging.getLogger(__name__)
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}"

def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2"""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def send_telegram_message(chat_id: int, text: str, parse_mode: str = None):
    """Send message to Telegram chat"""
    try:
        # Only escape markdown if using markdown parse mode
        if parse_mode and parse_mode.lower().startswith('markdown'):
            text = escape_markdown(text)
            
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_BASE}/sendMessage",
                json=payload
            )
            resp_json = response.json()
            if not resp_json.get("ok"):
                logger.error(f"Error sending message: {resp_json}")
                # Try sending without parse_mode if it fails
                if parse_mode:
                    return await send_telegram_message(chat_id, text, parse_mode=None)
            return resp_json
    except Exception as e:
        logger.error(f"Exception while sending message: {e}")
        # Try one more time without parse_mode
        if parse_mode:
            return await send_telegram_message(chat_id, text, parse_mode=None)
        raise


class TelegramBotService:
    def start(self):
        print("Telegram bot started...")  # For debugging

    def stop(self):
        print("Telegram bot stopped...")  # For debugging









