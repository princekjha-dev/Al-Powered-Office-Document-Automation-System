# 🚀 Quick Start Guide

## ⚡ Get Running in 3 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup API Keys
Edit the `.env` file with your API keys:
```bash
# Required
TELEGRAM_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional (for image generation)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 3. Run Setup Check
```bash
python setup.py
```

### 4. Start the Bot
```bash
python bot.py
```

## 🎯 Test Your Bot

1. **Start the bot**: Send `/start` to your Telegram bot
2. **Test document analysis**: Send a PDF/DOCX file
3. **Test document generation**: Use `/generate`
4. **Test image generation**: Use `/image` (if API key configured)
5. **View gallery**: Use `/gallery`

## 🔧 Troubleshooting

### Common Issues:

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**"API key missing" errors:**
- Edit `.env` file with your actual API keys
- Get Telegram token from [@BotFather](https://t.me/botfather)
- Get OpenRouter key from [openrouter.ai](https://openrouter.ai)

**"Directory not found" errors:**
```bash
python setup.py
```

### API Keys Setup:

1. **Telegram Bot Token:**
   - Go to [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token to `.env`

2. **OpenRouter API Key:**
   - Go to [openrouter.ai](https://openrouter.ai)
   - Sign up and get your API key
   - Copy to `.env`

3. **Hugging Face API Key (for images):**
   - Go to [huggingface.co](https://huggingface.co)
   - Create account and get API token
   - Copy to `.env`

## 📚 Features Overview

### Document Analysis
- Upload PDF, Word, or Excel files
- Get AI-powered summaries and insights
- Automatic image generation suggestions

### Document Generation
- `/generate` - Create professional documents
- Choose Word or PDF format
- AI-generated content with proper formatting

### Image Generation
- `/image` - Generate images from text prompts
- Multiple styles: Realistic, Abstract, Artistic
- Personal gallery with statistics

### Gallery Management
- `/gallery` - View your generated images
- `/gallery_stats` - See your statistics
- Persistent storage with metadata

## 🎉 You're Ready!

Once setup is complete, your AI-powered document and image assistant is ready to help with:
- 📄 Document analysis and insights
- ✏️ Professional document creation
- 🎨 AI image generation
- 📊 Gallery management and statistics

Happy automating! 🤖✨