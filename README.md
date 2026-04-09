# IntelliDoc

AI-powered document analysis platform. Upload PDFs, Word, or Excel files -- get summaries, insights, quality scoring, and answers in seconds.

Built with Flask, vanilla JavaScript, and OpenRouter AI.

---

## Features

- **Document Analysis** -- Upload PDF, DOCX, or XLSX files for automatic text extraction, language detection, categorization, and AI-powered content analysis.
- **Quality Scoring** -- Get a detailed quality assessment across five dimensions: clarity, grammar, coherence, completeness, and professionalism.
- **Document Q&A** -- Ask natural language questions about uploaded documents and receive contextual answers.
- **Document Generation** -- Generate professional Word or PDF documents from any topic using AI.
- **Document Comparison** -- Compare two documents and view a detailed diff with similarity scoring.
- **Image Generation** -- Create images from text prompts using Hugging Face models.
- **Quick Tools** -- Standalone language detection, categorization, and quality scoring for any text.
- **CLI Interface** -- Command-line tool for document analysis, generation, and image management.
- **Telegram Bot** -- Full-featured Telegram bot interface with all the same capabilities.

---

## Project Structure

```
.
├── website/                    # Web frontend
│   ├── web_app.py              # Flask server and API endpoints
│   ├── templates/
│   │   └── index.html          # Single-page application
│   └── static/
│       ├── css/style.css       # Minimal dark theme
│       └── js/app.js           # Frontend logic
├── src/                        # Core backend
│   ├── config/
│   │   └── settings.py         # Centralized configuration
│   ├── services/
│   │   ├── ai_generation.py    # OpenRouter AI integration
│   │   ├── document_reader.py  # PDF/DOCX/XLSX text extraction
│   │   ├── document_generator.py # DOCX/PDF creation
│   │   ├── document_chat.py    # Contextual Q&A over documents
│   │   ├── document_comparison.py # Text diff and similarity
│   │   ├── document_categorization.py # Content classification
│   │   ├── document_quality.py # Quality scoring engine
│   │   ├── language_detection.py # Language identification
│   │   ├── image_generator.py  # HuggingFace image generation
│   │   ├── image_gallery.py    # Image storage management
│   │   └── chat_image_generator.py # Chat-based image prompts
│   ├── models/
│   │   ├── user.py             # User model and management
│   │   └── storage.py          # Session and gallery storage
│   ├── handlers/
│   │   └── image_routes.py     # Image routing logic
│   └── utils/
│       └── helpers.py          # Logging and utility functions
├── bot.py                      # Telegram bot entry point
├── cli.py                      # Command-line interface
├── dashboard.py                # FastAPI dashboard (legacy)
├── tests/                      # Unit and integration tests
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup verification script
├── .env.example                # Environment variable template
└── .gitignore
```

---

## Setup

### Prerequisites

- Python 3.10 or higher
- An OpenRouter API key ([openrouter.ai](https://openrouter.ai))
- A Hugging Face token (optional, for image generation)
- A Telegram bot token (optional, for the Telegram bot)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/intellidoc.git
cd intellidoc

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your keys
cp .env.example .env
```

### Environment Variables

Edit `.env` with your API keys:

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional -- Telegram bot
TELEGRAM_TOKEN=your_telegram_bot_token

# Optional -- Image generation
HF_TOKEN=your_huggingface_token

# AI model (default: openai/gpt-4o-mini)
OPENROUTER_MODEL=openai/gpt-4o-mini
```

See `.env.example` for the full list of configuration options.

---

## Usage

### Web Application

```bash
python website/web_app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### Telegram Bot

```bash
python bot.py
```

### CLI

```bash
# Analyze a document
python cli.py document analyze path/to/file.pdf

# Generate a document
python cli.py document generate --topic "Quarterly Report" --format docx

# Generate an image
python cli.py image generate --prompt "A mountain landscape" --style realistic
```

### Setup Verification

```bash
python setup.py
```

Runs checks on Python version, dependencies, environment variables, and directory structure.

---

## API Endpoints

The web application exposes the following REST API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check and service status |
| `POST` | `/api/analyze` | Upload and analyze a document |
| `POST` | `/api/ask` | Ask a question about an uploaded document |
| `POST` | `/api/compare` | Compare two texts or documents |
| `POST` | `/api/generate` | Generate a DOCX or PDF document |
| `POST` | `/api/image` | Generate an image from a text prompt |
| `POST` | `/api/language` | Detect the language of a text |
| `POST` | `/api/categorize` | Categorize a text |
| `POST` | `/api/quality` | Score text quality |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Web Server | Flask |
| AI Backend | OpenRouter (GPT-4o-mini default) |
| Image Generation | Hugging Face Inference API |
| Document Processing | PyPDF2, python-docx, openpyxl |
| Document Creation | reportlab (PDF), python-docx (Word) |
| Language Detection | langdetect, sentence-transformers |
| Bot | python-telegram-bot |
| CLI | click, tabulate |

---

## License

This project is provided as-is for educational and personal use.
