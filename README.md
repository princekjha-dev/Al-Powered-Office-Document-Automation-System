<div align="center">

<img src="https://img.shields.io/badge/-%F0%9F%A7%A0%20IntelliDoc-1a1a2e?style=for-the-badge&labelColor=1a1a2e" height="60" alt="IntelliDoc"/>

# IntelliDoc

**AI-Powered Office Document Automation System**

> Upload PDFs, Word docs, or spreadsheets — get instant analysis, quality scoring,
> AI summaries, contextual Q&A, image generation, and voice transcription.

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white&style=flat-square" alt="Python 3.10+"/></a>
  <a href="https://flask.palletsprojects.com"><img src="https://img.shields.io/badge/Flask-2.x-000000?logo=flask&style=flat-square" alt="Flask"/></a>
  <a href="https://core.telegram.org/bots"><img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&style=flat-square" alt="Telegram Bot"/></a>
  <a href="https://openrouter.ai"><img src="https://img.shields.io/badge/OpenRouter-GPT--4o--mini-ff6b35?style=flat-square" alt="OpenRouter"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="MIT License"/></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-setup">Setup</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-reference">API</a> •
  <a href="#%EF%B8%8F-tech-stack">Tech Stack</a>
</p>

---

</div>

## ✨ Features

### 📄 Document Intelligence

| Feature | Description |
|---------|-------------|
| **Document Analysis** | Upload PDF, DOCX, or XLSX for automatic text extraction, language detection, categorization, tag generation, and AI-powered content analysis |
| **Quality Scoring** | Five-dimension assessment: clarity, grammar, coherence, completeness, and professionalism (scored 0–10) |
| **Document Q&A (RAG)** | Ask natural-language questions and receive contextually-grounded answers from your documents |
| **Document Comparison** | Side-by-side diff with similarity scoring, change summaries, and AI semantic analysis |
| **Summarization** | Full-document or per-page AI summaries |
| **Auto Outline** | Generate a structured outline from any document |
| **Keyword Search** | Find content inside loaded documents |

### ✏️ Document Generation

| Feature | Description |
|---------|-------------|
| **AI Document Creation** | Generate professional Word (DOCX) or PDF documents on any topic using AI |
| **Translation** | Translate document content to 100+ languages |

### 🎨 Image Generation

| Feature | Description |
|---------|-------------|
| **Text-to-Image** | Create images from text prompts using Hugging Face FLUX models |
| **Multiple Styles** | Realistic, artistic, sketch, anime, cinematic, and more |
| **Image Gallery** | Browse, manage, and export generated images |
| **Gallery Export** | Download your entire gallery as a ZIP archive |

### 🎙️ Voice Transcription

| Feature | Description |
|---------|-------------|
| **Voice-to-Text** | Send voice messages and get instant transcription |
| **Groq Whisper** | Powered by `whisper-large-v3-turbo` via Groq's free API (falls back to OpenAI Whisper) |
| **Auto-Analysis** | Voice transcripts are automatically summarized and available for Q&A |

### 🖥️ Three Interfaces

| Interface | Entry Point | Description |
|-----------|-------------|-------------|
| 🌐 **Web Dashboard** | `python website/web_app.py` | Premium dark-theme SPA with glassmorphism, micro-animations, and sidebar navigation |
| 💬 **Telegram Bot** | `python bot.py` | Full-featured bot with inline keyboards, voice support, and typing indicators |
| ⌨️ **CLI** | `python cli.py` | Command-line tool for scripting and automation |

---

## 🏗️ Project Structure

```
intellidoc/
│
├── website/                            # Web frontend & API server
│   ├── web_app.py                      # Flask server (all REST endpoints)
│   ├── templates/
│   │   └── index.html                  # Single-page application
│   └── static/
│       ├── css/style.css               # Premium dark theme + animations
│       └── js/app.js                   # Frontend logic & API client
│
├── src/                                # Core backend services
│   ├── config/
│   │   └── settings.py                 # Centralized configuration
│   ├── services/
│   │   ├── ai_generation.py            # OpenRouter / Groq / OpenAI integration
│   │   ├── document_reader.py          # PDF / DOCX / XLSX text extraction
│   │   ├── document_generator.py       # DOCX & PDF creation
│   │   ├── document_chat.py            # RAG-style contextual Q&A
│   │   ├── document_comparison.py      # Text diff & similarity scoring
│   │   ├── document_categorization.py  # Content classification & tagging
│   │   ├── document_quality.py         # Five-dimension quality scoring
│   │   ├── language_detection.py       # Language identification
│   │   ├── image_generator.py          # Hugging Face image generation
│   │   ├── image_gallery.py            # Image storage & management
│   │   └── chat_image_generator.py     # Chat-based image prompts
│   ├── models/
│   │   ├── user.py                     # User model & statistics
│   │   └── storage.py                  # Session & gallery persistence
│   ├── handlers/
│   │   └── image_routes.py             # Image API routing
│   └── utils/
│       └── helpers.py                  # Logging & utility functions
│
├── bot.py                              # Telegram bot (v2 — full-featured)
├── cli.py                              # Command-line interface
├── dashboard.py                        # FastAPI dashboard (legacy)
├── tests/                              # Unit & integration tests
├── data/                               # Runtime data (sessions, galleries)
├── requirements.txt                    # Python dependencies
├── setup.py                            # Setup verification script
├── .env.example                        # Environment variable template
└── .gitignore
```

---

## 🚀 Setup

### Prerequisites

Before you begin, make sure you have the following:

- **Python 3.10+** (tested on 3.13)
- **OpenRouter API key** — [openrouter.ai](https://openrouter.ai) *(required for AI features)*
- **Groq API key** — [console.groq.com](https://console.groq.com) *(free — for voice transcription)*
- **Hugging Face token** — [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) *(optional — image generation)*
- **Telegram bot token** — [@BotFather](https://t.me/BotFather) *(optional — Telegram interface)*

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/intellidoc.git
cd intellidoc

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template and fill in your keys
cp .env.example .env
```

### Environment Variables

Open `.env` and configure your API keys:

```env
# ─── Required ────────────────────────────────────────────────
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini        # or any OpenRouter model
AI_PROVIDER=openrouter                      # openrouter | openai | groq

# ─── Voice Transcription (free via Groq) ─────────────────────
GROQ_API_KEY=your_groq_api_key

# ─── Telegram Bot (optional) ─────────────────────────────────
TELEGRAM_TOKEN=your_telegram_bot_token

# ─── Image Generation (optional) ─────────────────────────────
HF_TOKEN=your_huggingface_token
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-Krea-dev

# ─── Optional OpenAI (fallback for Whisper) ──────────────────
OPENAI_API_KEY=                             # only needed if no Groq key
```

> 💡 See [`.env.example`](.env.example) for the full list of configuration options including session timeouts, file size limits, and language defaults.

### Verify Setup

```bash
python setup.py
```

Runs automated checks on your Python version, installed dependencies, API key presence, and directory structure.

---

## 📖 Usage

### 🌐 Web Dashboard

```bash
python website/web_app.py
```

Then open **[http://localhost:5000](http://localhost:5000)** in your browser.

The web dashboard includes:
- Drag-and-drop document upload
- Interactive quality score gauges
- Real-time document Q&A chat
- Side-by-side document comparison
- AI image generation with style picker
- Responsive sidebar navigation with glassmorphism effects

---

### 💬 Telegram Bot

```bash
python bot.py
```

**Available commands:**

| Command | Description |
|---------|-------------|
| `/start` | Create your profile & open the main menu |
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
| `/clear` | Clear the current session |
| 🎙️ *Voice note* | Send audio → auto-transcribe & analyze |

**Bot architecture highlights:**
- Circuit-breaker pattern on AI calls (auto-disables after repeated failures)
- Exponential back-off retry with configurable attempts
- Per-user sliding-window rate limiter
- Native "typing…" indicators during processing
- Concurrent analysis via `asyncio.gather()`
- Graceful `SIGTERM` shutdown (Docker / systemd compatible)

---

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

The web application exposes a REST API at `http://localhost:5000`.

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check & service status |
| `POST` | `/api/analyze` | Upload and analyze a document *(multipart)* |
| `POST` | `/api/ask` | Ask a question about an analyzed document |
| `POST` | `/api/compare` | Compare two documents or text blocks |
| `POST` | `/api/generate` | Generate a DOCX or PDF from a topic |
| `POST` | `/api/image` | Generate an image from a text prompt |

### Quick Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/language` | Detect the language of text |
| `POST` | `/api/categorize` | Categorize and tag text |
| `POST` | `/api/quality` | Score text quality across 5 dimensions |

### Chat Image Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat-generate-image` | Generate an image within a chat session |
| `GET` | `/api/chat-gallery/<user_id>` | Retrieve all images in a user's gallery |
| `GET` | `/api/chat-session-images/<session_id>` | Get images from a specific session |
| `GET` | `/api/image-status` | List available APIs & styles |

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
| **Document Creation** | ReportLab (PDF), python-docx (DOCX) |
| **Language Detection** | langdetect, sentence-transformers |
| **Telegram Bot** | python-telegram-bot (async) |
| **CLI** | Click, Tabulate |
| **HTTP Client** | aiohttp (async), requests |

---

## 📋 Dependencies

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
aiohttp                # Async HTTP (Telegram voice transcription)
```

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss any changes you'd like to make, then submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is provided under the **MIT License** for educational and personal use. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ using Python, Flask, and the Anthropic/OpenRouter AI ecosystem</sub>
</div>
