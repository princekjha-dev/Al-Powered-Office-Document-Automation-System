# AI-Powered Office Document Automation System

A Telegram bot that automates office document analysis using Claude AI API.

## Features

- Accept PDF, Word (.docx), Excel (.xlsx) files
- Auto-detect file type and process accordingly
- Extract text from documents
- Send text to Claude API for analysis
- Return: Summary, 5 Key Points, 1 Smart Insight, Action Items

## Commands

- `/start` - Welcome message
- `/help` - Show available commands

## Tech Stack

- Python 3.10+
- python-telegram-bot library
- anthropic library (Claude API)
- PyPDF2 (for PDF reading)
- python-docx (for Word files)
- openpyxl (for Excel files)

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   CLAUDE_API_KEY=your_claude_api_key_here
   ```
4. Run the bot: `python bot.py`

## Error Handling

- File too large (>20MB) → send error message
- Unsupported file → tell user
- API fail → retry once then notify user

## Project Structure

- `bot.py` - Main bot logic
- `document_reader.py` - File parsing
- `claude_handler.py` - API calls
- `.env` - API keys (not committed)
- `requirements.txt` - Dependencies