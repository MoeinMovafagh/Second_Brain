import uvicorn
import httpx
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.services.telegram import TelegramBotService
from app.config import API_HOST, API_PORT, TELEGRAM_API_TOKEN, WEBHOOK_BASE_URL, USE_NGROK

# Global Telegram service instance
telegram_service = None

async def get_webhook_url():
    """Get the webhook URL, using ngrok in development if enabled"""
    if WEBHOOK_BASE_URL:
        return f"{WEBHOOK_BASE_URL}/webhook"
    
    if USE_NGROK:
        # Get the public URL from ngrok
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:4040/api/tunnels")
                if response.status_code == 200:
                    tunnels = response.json()["tunnels"]
                    for tunnel in tunnels:
                        if tunnel["proto"] == "https":
                            return f"{tunnel['public_url']}/webhook"
        except Exception as e:
            print(f"Error getting ngrok URL: {e}")
            print("Please make sure ngrok is running with: ngrok http 8060")
            return None
    
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    global telegram_service
    
    # Create data directory for notes if it doesn't exist
    os.makedirs("data/notes", exist_ok=True)
    
    # Startup: Initialize Telegram bot service
    telegram_service = TelegramBotService()
    telegram_service.start()
    
    # Set up Telegram webhook
    webhook_url = await get_webhook_url()
    if webhook_url:
        print(f"Setting webhook URL to: {webhook_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/setWebhook",
                params={"url": webhook_url}
            )
            if response.status_code != 200 or not response.json().get("ok"):
                print(f"Error setting webhook: {response.status_code} - {response.text}")
                print("Continuing with polling method...")
    else:
        print("No webhook URL available. Please start ngrok or set WEBHOOK_BASE_URL")

    yield  # Hand control back to FastAPI

    # Shutdown: Clean up Telegram service
    if telegram_service:
        telegram_service.stop()
    
    # Remove webhook on shutdown
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/deleteWebhook")

app = FastAPI(title="Second Brain Agent", lifespan=lifespan)
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Second Brain Agent is running"}

def start():
    """Start the FastAPI application"""
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)

if __name__ == "__main__":
    start()