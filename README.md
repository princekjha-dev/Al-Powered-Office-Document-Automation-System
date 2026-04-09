# 🤖 AI-Powered Office Document Automation System

A Telegram bot + REST API + CLI for intelligent document analysis, generation, and AI-powered image creation.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📄 **Document Analysis** | Upload PDF, DOCX, XLSX → get AI-powered summary, key points, and insights |
| 💬 **Document Q&A (RAG)** | Ask natural language questions about documents with context-grounded answers |
| 🔍 **Document Comparison** | Compare two documents — structural diff + AI semantic analysis |
| 📂 **Auto-Categorization** | Auto-classify documents into 10 categories with confidence scores |
| 🌍 **Language Detection** | Detect 10+ languages with confidence scoring + AI translation |
| 📊 **Quality Scoring** | 5-dimension quality assessment (clarity, grammar, coherence, completeness, professionalism) |
| ✏️ **Document Generation** | Generate professional DOCX/PDF from topic prompts |
| 🎨 **Image Generation** | Generate images via Hugging Face FLUX.1-Krea-dev model (fal-ai provider) |
| 📸 **Image Gallery** | Persistent per-user gallery with search, tags, and export |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Telegram Bot Token](https://t.me/BotFather)
- [OpenRouter API Key](https://openrouter.ai/keys)
- (Optional) [Hugging Face Token](https://huggingface.co/settings/tokens) for image generation

### Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd Al-Powered-Office-Document-Automation-System

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration below)

# 5. Verify setup
python setup.py

# 6. Run the bot
python bot.py
```

## 🔐 Configuration

Create a `.env` file with these keys:

```env
# Required
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini

# Image Generation (optional — falls back to placeholders without it)
HF_TOKEN=your_huggingface_token
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-Krea-dev

# Image Settings
IMAGE_GENERATION_ENABLED=true
DEFAULT_IMAGE_STYLE=realistic
MAX_IMAGES_PER_DOCUMENT=3

# Optional AI Providers
OPENAI_API_KEY=
GROQ_API_KEY=
GEMII_API_KEY=
AI_PROVIDER=openrouter
```

## 🎮 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/generate` | Generate a DOCX or PDF document from a topic |
| `/image` | Generate an image from a text prompt |
| `/gallery` | View your image gallery |
| `/stats` | Your usage statistics |
| `/cancel` | Cancel current operation |
| **Send a file** | Upload PDF/DOCX/XLSX to get a full analysis report |

### Document Analysis Flow

When you upload a document, the bot returns a **single consolidated report**:

```
📄 Document Report
━━━━━━━━━━━━━━━━━━━━

🌐 Language: English (en) — 85%
📂 Category: REPORT — 72%
🏷 Tags: analysis, data, summary

📊 Quality: 7.2/10 (Good 👍)
   Clarity: 8.1 · Grammar: 9.2 · Coherence: 6.3

📏 Stats: 1,250 words · 89 lines · ~5 pages
```

Followed by a detailed **AI Analysis** with summary, key points, insights, and action items.

## 💻 Three Interfaces

### 1. Telegram Bot
```bash
python bot.py
```

### 2. REST API Dashboard
```bash
python dashboard.py
# Runs on http://localhost:5000
```

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/documents/analyze` | Analyze uploaded document |
| `POST` | `/api/documents/generate` | Generate document from topic |
| `POST` | `/api/images/generate` | Generate image from prompt |
| `GET` | `/api/galleries/<user_id>` | Get user's gallery |
| `GET` | `/api/galleries/<user_id>/stats` | Gallery statistics |
| `POST` | `/api/users` | Create user |
| `GET` | `/api/users/<user_id>` | Get user info |
| `GET` | `/api/settings` | System settings |

### 3. Command-Line Interface
```bash
python cli.py --help
python cli.py document analyze file.pdf
python cli.py document generate --topic "Python Best Practices" --format pdf
python cli.py image generate --prompt "A sunset over mountains" --style realistic
python cli.py gallery stats --user-id 123
python cli.py user create --user-id 123 --first-name "Rajat"
```

## 🏗️ Project Structure

```
├── bot.py                          # Telegram bot (main entry point)
├── dashboard.py                    # Flask REST API
├── cli.py                          # Command-line interface
├── setup.py                        # Setup verification script
├── test_bot.py                     # Quick test script
├── requirements.txt                # Python dependencies
├── .env                            # API keys (not committed)
├── .env.example                    # Example environment template
│
├── src/
│   ├── config/
│   │   └── settings.py             # Centralized configuration
│   ├── models/
│   │   ├── user.py                 # User model & UserManager
│   │   └── storage.py              # Gallery storage & session management
│   ├── services/
│   │   ├── ai_generation.py        # OpenRouter AI text generation
│   │   ├── document_reader.py      # PDF/DOCX/XLSX text extraction
│   │   ├── document_generator.py   # DOCX & PDF creation
│   │   ├── image_generator.py      # HF InferenceClient image generation
│   │   ├── image_gallery.py        # Gallery CRUD & search
│   │   ├── document_chat.py        # RAG-based document Q&A
│   │   ├── document_comparison.py  # Document diff & semantic analysis
│   │   ├── document_categorization.py  # Auto-categorization & tagging
│   │   ├── language_detection.py   # Multi-language detection
│   │   └── document_quality.py     # Quality scoring (5 dimensions)
│   └── utils/
│       └── helpers.py              # Logging, formatting utilities
│
└── data/                           # Auto-created at runtime
    ├── users/                      # User profiles (JSON)
    ├── galleries/                  # Per-user image galleries
    └── sessions/                   # Temporary session data
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Bot Framework** | python-telegram-bot |
| **AI Text** | OpenRouter API (GPT-4o-mini) |
| **AI Images** | Hugging Face InferenceClient (FLUX.1-Krea-dev via fal-ai) |
| **RAG Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Language Detection** | langdetect |
| **Document Parsing** | PyPDF2, python-docx, openpyxl |
| **Document Generation** | python-docx, reportlab |
| **Image Processing** | Pillow |
| **REST API** | Flask + Flask-CORS |
| **CLI** | Click + tabulate |

## 🧪 Testing

```bash
# Quick setup verification
python setup.py

# Quick bot test
python test_bot.py

# Test CLI
python cli.py version
```

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `TELEGRAM_TOKEN is required` | Add your bot token to `.env` |
| `API failed after retry` | Check your `OPENROUTER_API_KEY` is valid |
| Images show placeholders | Add `HF_TOKEN` to `.env` or check quota |
| `409 Conflict` errors | Another bot instance is running — kill all `python` processes first |
| Unicode/emoji errors on Windows | Run with `$env:PYTHONIOENCODING='utf-8'` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |

## 📄 License

This project is provided as-is for educational and development purposes.

---

**Version:** 1.0.0 · **Python:** 3.10+ · **Status:** Production Ready ✅