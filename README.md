# Second Brain

A Telegram bot that helps you manage your personal knowledge using natural language processing. Save, organize, and retrieve your notes effortlessly through chat interactions.

## Features

- Save notes with titles, content, and tags
- Search through your notes using natural language
- Organize information with tags
- Interactive chat interface through Telegram

## Prerequisites

- Python 3.12+
- A Telegram Bot Token
- An OpenAI API Key
- ngrok (for local development)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MoeinMovafagh/Second_Brain
cd Second_Brain
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

## Running the Application

1. Start ngrok (for local development):
```bash
ngrok http 8060
```

2. Start the FastAPI application:
```bash
python -m uvicorn app.main:app --port 8060
```

## Usage

1. Start a chat with your Telegram bot
2. Send messages to:
   - Save notes: "Save this note: [content]"
   - Search notes: "Find notes about [topic]"
   - Tag notes: "Tag the last note with [tags]"

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
