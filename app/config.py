import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Changed to a valid model name
OAUTH_REDIRECT_PATH = "/oauth2callback"

API_HOST = os.getenv('API_HOST', 'localhost')
API_PORT = int(os.getenv('API_PORT', '8060'))  # Changed back to 8060 to match ngrok

# Get webhook URL from environment variable or use ngrok to generate one
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', None)  # Set this when in production
USE_NGROK = os.getenv('USE_NGROK', 'true').lower() == 'true'  # Use ngrok by default in development