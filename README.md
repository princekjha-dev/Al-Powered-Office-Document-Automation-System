# AI-Powered Office Document Automation System

A Telegram bot that automates office document analysis using AI APIs.

## Features

- Accept PDF, Word (.docx), Excel (.xlsx) files
- Auto-detect file type and process accordingly
- Extract text from documents
- Send text to OpenRouter, OpenAI, Groq, or Gemii APIs for analysis
- Return: Summary, 5 Key Points, 1 Smart Insight, Action Items

## Commands

- `/start` - Welcome message
- `/help` - Show available commands

## Tech Stack

- Python 3.10+
- python-telegram-bot library
- requests (for OpenRouter API requests)
- PyPDF2 (for PDF reading)
- python-docx (for Word files)
- openpyxl (for Excel files)
- python-dotenv (for environment variables)

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=gpt-4o-mini
   OPENAI_API_KEY=your_openai_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   GEMII_API_KEY=your_gemii_api_key_here
   AI_PROVIDER=openrouter
   ```
4. Run the bot: `python bot.py`

## Configuration

- `config.py` centralizes environment variables for all supported AI providers.
- `AI_PROVIDER` is optional and defaults to `openrouter`.

## Error Handling

- File too large (>20MB) → send error message
- Unsupported file → tell user
- API fail → retry once then notify user

## Project Structure

- `bot.py` - Main bot logic
- `document_reader.py` - File parsing
- `openrouter_handler.py` - OpenRouter API calls
- `config.py` - Environment configuration and API keys
- `.env` - API keys (not committed)
- `.env.example` - Example environment variables
- `requirements.txt` - Dependencies