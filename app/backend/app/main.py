import uvicorn
import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.services.telegram import TelegramBotService
from app.config import API_HOST, API_PORT, TELEGRAM_API_TOKEN

# Global Telegram service instance
telegram_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    global telegram_service
    
    # Startup: Initialize Telegram bot service
    telegram_service = TelegramBotService()
    telegram_service.start()
    
    # Set up Telegram webhook
    backend_url = "https://cb9c-207-5-31-67.ngrok-free.app"
    WEBHOOK_URL = f"{backend_url}/webhook"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        if response.status_code != 200 or not response.json().get("ok"):
            print(f"Error setting webhook: {response.status_code} - {response.text}")
            print("Continuing with polling method...")

    yield  # Hand control back to FastAPI

    # Shutdown: Clean up Telegram service
    if telegram_service:
        telegram_service.stop()
    
    # Remove webhook on shutdown
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/deleteWebhook")

app = FastAPI(title="Calendar AI Agent", lifespan=lifespan)
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Calendar AI Agent is running"}

def start():
    """Start the FastAPI application"""
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)

if __name__ == "__main__":
    start()