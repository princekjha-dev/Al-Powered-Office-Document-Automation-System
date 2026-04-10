<![CDATA[<div align="center">

# 🧠 IntelliDoc

**AI-Powered Office Document Automation System**

Upload PDFs, Word docs, or spreadsheets — get instant analysis, quality scoring,
AI summaries, contextual Q&A, image generation, and voice transcription.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask)](https://flask.palletsprojects.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ✨ Features

### 📄 Document Intelligence
- **Document Analysis** — Upload PDF, DOCX, or XLSX for automatic text extraction, language detection, categorization, tag generation, and AI-powered content analysis.
- **Quality Scoring** — Five-dimension assessment: clarity, grammar, coherence, completeness, and professionalism (scored 0–10).
- **Document Q&A (RAG)** — Ask natural-language questions about uploaded documents and receive contextual answers grounded in the content.
- **Document Comparison** — Side-by-side diff with similarity scoring, change summaries, and AI semantic analysis.
- **Summarization** — Full-document or per-page AI summaries.
- **Auto Outline** — Generate a structured outline from any document.
- **Keyword Search** — Find content inside loaded documents.

### ✏️ Document Generation
- **AI Document Creation** — Generate professional Word (DOCX) or PDF documents from any topic using AI.
- **Translation** — Translate document content to 100+ languages.

### 🎨 Image Generation
- **Text-to-Image** — Create images from text prompts using Hugging Face FLUX models.
- **Multiple Styles** — Realistic, artistic, sketch, anime, cinematic, and more.
- **Image Gallery** — Browse, manage, and export generated images.
- **Gallery Export** — Download entire gallery as a ZIP archive.

### 🎙️ Voice Transcription
- **Voice-to-Text** — Send voice messages and get instant transcription.
- **Powered by Groq Whisper** — Uses `whisper-large-v3-turbo` via Groq's free API (falls back to OpenAI Whisper if needed).
- **Auto-Analysis** — Voice transcripts are automatically summarized and made available for Q&A.

### 🤖 Three Interfaces
| Interface | Entry Point | Description |
|-----------|-------------|-------------|
| 🌐 **Web Dashboard** | `python website/web_app.py` | Premium dark-theme SPA with glassmorphism, micro-animations, and sidebar navigation |
| 💬 **Telegram Bot** | `python bot.py` | Full-featured bot with inline keyboards, voice support, and typing indicators |
| ⌨️ **CLI** | `python cli.py` | Command-line tool for scripting and automation |

---

## 🏗️ Project Structure

```
.
├── website/                        # Web frontend & API server
│   ├── web_app.py                  # Flask server (all REST endpoints)
│   ├── templates/
│   │   └── index.html              # Single-page application
│   └── static/
│       ├── css/style.css           # Premium dark theme + animations
│       └── js/app.js               # Frontend logic & API client
│
├── src/                            # Core backend services
│   ├── config/
│   │   └── settings.py             # Centralized configuration
│   ├── services/
│   │   ├── ai_generation.py        # OpenRouter / Groq / OpenAI integration
│   │   ├── document_reader.py      # PDF / DOCX / XLSX text extraction
│   │   ├── document_generator.py   # DOCX & PDF creation
│   │   ├── document_chat.py        # RAG-style contextual Q&A
│   │   ├── document_comparison.py  # Text diff & similarity scoring
│   │   ├── document_categorization.py  # Content classification & tagging
│   │   ├── document_quality.py     # Five-dimension quality scoring
│   │   ├── language_detection.py   # Language identification
│   │   ├── image_generator.py      # Hugging Face image generation
│   │   ├── image_gallery.py        # Image storage & management
│   │   └── chat_image_generator.py # Chat-based image prompts
│   ├── models/
│   │   ├── user.py                 # User model & statistics
│   │   └── storage.py             # Session & gallery persistence
│   ├── handlers/
│   │   └── image_routes.py         # Image API routing
│   └── utils/
│       └── helpers.py              # Logging & utility functions
│
├── bot.py                          # Telegram bot (v2 — full-featured)
├── cli.py                          # Command-line interface
├── dashboard.py                    # FastAPI dashboard (legacy)
├── tests/                          # Unit & integration tests
├── data/                           # Runtime data (sessions, galleries)
├── requirements.txt                # Python dependencies
├── setup.py                        # Setup verification script
├── .env.example                    # Environment variable template
└── .gitignore
```

---

## 🚀 Setup

### Prerequisites

- **Python 3.10+** (tested on 3.13)
- **OpenRouter API key** — [openrouter.ai](https://openrouter.ai) (required for AI features)
- **Groq API key** — [console.groq.com](https://console.groq.com) (free — for voice transcription)
- **Hugging Face token** — [huggingface.co](https://huggingface.co/settings/tokens) (optional — image generation)
- **Telegram bot token** — [@BotFather](https://t.me/BotFather) (optional — Telegram interface)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/intellidoc.git
cd intellidoc

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your keys
cp .env.example .env
```

### Environment Variables

Edit `.env` with your API keys:

```env
# ─── Required ────────────────────────────────────
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini        # or any OpenRouter model
AI_PROVIDER=openrouter                      # openrouter | openai | groq

# ─── Voice Transcription (free via Groq) ─────────
GROQ_API_KEY=your_groq_api_key              # free at console.groq.com

# ─── Telegram Bot (optional) ─────────────────────
TELEGRAM_TOKEN=your_telegram_bot_token

# ─── Image Generation (optional) ─────────────────
HF_TOKEN=your_huggingface_token
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-Krea-dev

# ─── Optional OpenAI (fallback for Whisper) ──────
OPENAI_API_KEY=                             # only needed if no Groq key
```

> See [`.env.example`](.env.example) for the full list of configuration options including session timeouts, file size limits, and language defaults.

### Verify Setup

```bash
python setup.py
```

Runs checks on Python version, dependencies, API keys, and directory structure.

---

## 📖 Usage

### 🌐 Web Dashboard

```bash
python website/web_app.py
```

Open [http://localhost:5000](http://localhost:5000) — features a premium dark-theme interface with:
- Drag-and-drop document upload
- Interactive quality score gauges
- Real-time document Q&A chat
- Side-by-side document comparison
- AI image generation with style picker
- Responsive sidebar navigation with glassmorphism effects

### 💬 Telegram Bot

```bash
python bot.py
```

Key commands:

| Command | Description |
|---------|-------------|
| `/start` | Create profile & show main menu |
| `/menu` | Open the interactive menu |
| `/analyze` | Upload & analyze a document |
| `/summarize [page]` | Summarize full doc or a specific page |
| `/outline` | Auto-generate a structured outline |
| `/search <query>` | Find content in loaded documents |
| `/translate <lang>` | Translate document content |
| `/compare` | Compare two documents |
| `/ask` or `/chat` | Start Q&A over your document |
| `/generate` | Generate a Word or PDF document |
| `/image` | Create an AI image |
| `/gallery` | View your image gallery |
| `/export` | Download gallery as ZIP |
| `/stats` | View your usage statistics |
| `/clear` | Clear current session |
| 🎙️ Voice | Send a voice note → auto-transcribe & analyze |

**Bot architecture highlights:**
- Circuit-breaker pattern on AI calls (auto-disables after repeated failures)
- Exponential back-off retry with configurable attempts
- Per-user sliding-window rate limiter
- Native "typing..." indicators during processing
- Concurrent analysis via `asyncio.gather()`
- Graceful SIGTERM shutdown (Docker / systemd compatible)

### ⌨️ CLI

```bash
# Analyze a document
python cli.py document analyze path/to/file.pdf

# Generate a document
python cli.py document generate --topic "Quarterly Report" --format docx

# Generate an image
python cli.py image generate --prompt "A mountain landscape" --style realistic
```

---

## 🔌 API Reference

The web application exposes the following REST API at `http://localhost:5000`:

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check & service status |
| `POST` | `/api/analyze` | Upload and analyze a document (multipart) |
| `POST` | `/api/ask` | Ask a question about an analyzed document |
| `POST` | `/api/compare` | Compare two documents or text blocks |
| `POST` | `/api/generate` | Generate a DOCX or PDF from a topic |
| `POST` | `/api/image` | Generate an image from a text prompt |

### Quick Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/language` | Detect the language of text |
| `POST` | `/api/categorize` | Categorize and tag text |
| `POST` | `/api/quality` | Score text quality (5 dimensions) |

### Chat Image Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat-generate-image` | Generate image within a chat session |
| `GET` | `/api/chat-gallery/<user_id>` | Get all images in a user's gallery |
| `GET` | `/api/chat-session-images/<session_id>` | Get images from a specific session |
| `GET` | `/api/image-status` | Available APIs & styles |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Web Server** | Flask + Flask-CORS |
| **AI Backend** | OpenRouter (GPT-4o-mini default), Groq, OpenAI |
| **Voice Transcription** | Groq Whisper (`whisper-large-v3-turbo`) |
| **Image Generation** | Hugging Face Inference API (FLUX.1) |
| **Document Parsing** | PyPDF2, python-docx, openpyxl |
| **Document Creation** | ReportLab (PDF), python-docx (Word) |
| **Language Detection** | langdetect, sentence-transformers |
| **Telegram Bot** | python-telegram-bot (async) |
| **CLI** | Click, Tabulate |
| **HTTP Client** | aiohttp (async), requests |

---

## 📋 Requirements

All Python dependencies are listed in [`requirements.txt`](requirements.txt):

```
python-telegram-bot    # Telegram bot framework
requests               # HTTP client
PyPDF2                 # PDF text extraction
python-docx            # Word document read/write
openpyxl               # Excel file support
python-dotenv          # .env file loading
reportlab              # PDF generation
pillow                 # Image processing
fastapi                # Legacy dashboard
uvicorn                # ASGI server
flask                  # Web app server
flask-cors             # CORS support
click                  # CLI framework
tabulate               # CLI table formatting
tqdm                   # Progress bars
sentence-transformers  # Semantic embeddings
numpy                  # Numerical processing
langdetect             # Language detection
huggingface_hub        # HF Inference API
```

> **Note:** `aiohttp` is also required at runtime for the Telegram bot's voice transcription and is installed automatically.

---

## 📄 License

This project is provided as-is for educational and personal use.
]]>
