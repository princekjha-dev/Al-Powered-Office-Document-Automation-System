# 🤖 Intellidoc — AI Office Document Automation Platform

> Your smart AI office assistant — available as a **Telegram bot** and a **full web platform**.  
> Upload any document (PDF, Word, Excel, PowerPoint), then analyze, summarize, compare, score, translate, and generate new docs — all powered by AI, with built-in anti-hallucination safeguards.

`Python 3.10+` · `Anti-Hallucination` · `Multi-Language` · `Context-Aware AI` · `Telegram Bot` · `Web Platform` · `REST API + CLI`

---

## 🌐 Two Ways to Access Intellidoc

Intellidoc runs on two parallel surfaces that share the same AI engine, the same document processing pipeline, and the same anti-hallucination system. Choose the interface that fits your workflow — or use both.

| Interface | Description | Best For |
|-----------|-------------|----------|
| 📱 **Telegram Bot** | No installs. No accounts beyond Telegram. Send a file, get instant AI analysis. Full command set via `/commands`. Works on any device, anywhere. | Quick tasks, on-the-go use, zero setup |
| 🌐 **Web Platform** | Full-featured browser interface with drag-and-drop uploads, visual dashboards, comparison views, gallery management, and team collaboration. | Power users, organizations, visual workflows |

> **The core insight:** Documents dominate office work — contracts, reports, proposals, invoices. People spend hours reading, summarizing, and comparing them manually. AI can handle the thinking. Telegram makes it universally accessible. The web platform unlocks deeper workflows for teams.

---

## ✨ Core Features (15 total)

### Main Features
| # | Feature | Description |
|---|---------|-------------|
| 01 | 💬 **Context-Aware AI Chatbot** | Conversational AI grounded entirely in your uploaded documents. Maintains session context across turns. Will not answer outside the document scope. |
| 02 | 🛡️ **Anti-Hallucination Engine** | Every AI-generated claim is cross-referenced against source content. Confidence scores surface uncertain statements. Refusal logic prevents fabricated facts when evidence is absent. |
| 03 | 🎨 **Document Image Generation** | Generate contextual images from a document or presentation prompt — diagrams, infographics, cover art — using FLUX.1 with document content as reference context. |
| 04 | 🔎 **Smart Error Detection** | Multi-pass document linting: grammar, factual inconsistencies, broken references, structural gaps, and formatting anomalies — all flagged with location pointers. |
| 05 | 🌍 **Multi-Language Intelligence** | Detect and process 30+ languages. Analysis, Q&A, and generation adapt to the document's language. Cross-language comparison and translation with linguistic accuracy grading. |

### Core Features
| # | Feature | Description |
|---|---------|-------------|
| 06 | 📄 **Document Analysis** | Upload PDF, DOCX, XLSX, or PPTX and receive a structured intelligence report: summary, key points, entities, action items, quality scores, and category classification. |
| 07 | 🔍 **Document Comparison** | Structural diff combined with semantic drift analysis. Identifies what changed, what was removed, what contradicts, and what the implications are — across any two documents. |
| 08 | ✏️ **Document Generation** | Generate professional DOCX or PDF output from a topic prompt or an existing reference document. Supports templates, tone controls, and length constraints. |
| 09 | 📊 **Quality Scoring** | Five-dimension assessment — clarity, grammar, coherence, completeness, professionalism — with dimension-level feedback and an overall score on a 10-point scale. |
| 10 | 📂 **Auto-Categorization** | Classify documents into predefined or custom category trees with confidence scores. Tags extracted from content and appended for downstream filtering. |
| 11 | 🧠 **Session & Context Management** | Per-user session state tracks active documents, conversation history, and preference settings. Context is carried across all operations within a session. |
| 12 | 🖼️ **Image Gallery** | Persistent per-user gallery for all generated images. Searchable by tag, document source, and date. Exportable as a zip archive or embedded into a generated document. |

### Web Platform Features
| # | Feature | Description |
|---|---------|-------------|
| 13 | 🖥️ **Web Dashboard** | Full browser-based interface with drag-and-drop uploads, document history, side-by-side comparison views, and a visual quality scoring panel. No Telegram account required. |
| 14 | 👥 **Team Collaboration** | Share documents and analysis reports across team members. Comment threads, version history, and role-based permissions for organizations. |
| 15 | 🗂️ **Document History & Search** | Full searchable history of all processed documents. Filter by date, category, language, quality score, or tags. Re-run any previous analysis instantly. |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Telegram Bot Token](https://t.me/BotFather) — for the bot interface
- [OpenRouter API Key](https://openrouter.ai/keys)
- Node.js 18+ — for the web platform frontend
- (Optional) [Hugging Face Token](https://huggingface.co/settings/tokens) — for image generation; falls back to placeholder stub without it

### Installation

```bash
# 1. Clone and enter
git clone <repo-url>
cd intellidoc

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration below)

# 5. Verify setup
python setup.py

# 6. Run preferred interface
python bot.py          # Telegram Bot
python web.py          # Web Platform on :3000
python dashboard.py    # REST API on :5000
python cli.py          # Command-line
```

---

## 🔐 Configuration

Create a `.env` file with the following keys:

```env
# ── Required ─────────────────────────────────────────────
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini

# ── Platform Toggles ─────────────────────────────────────
ENABLE_TELEGRAM=true
ENABLE_WEB=true

# ── Web Platform ─────────────────────────────────────────
WEB_PORT=3000
WEB_SECRET_KEY=your_secret_key   # python -c "import secrets; print(secrets.token_hex(32))"

# ── Image Generation (optional) ──────────────────────────
HF_TOKEN=your_huggingface_token
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-Krea-dev
IMAGE_GENERATION_ENABLED=true
DEFAULT_IMAGE_STYLE=realistic
MAX_IMAGES_PER_DOCUMENT=3

# ── AI Provider ──────────────────────────────────────────
AI_PROVIDER=openrouter           # openrouter | openai | groq
OPENAI_API_KEY=
GROQ_API_KEY=

# ── Quality & Safety ─────────────────────────────────────
HALLUCINATION_THRESHOLD=0.72     # Claims below this are flagged or withheld
DEFAULT_LANGUAGE=en              # Fallback when language detection is inconclusive
```

### All Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | ✅ | Bot token from BotFather. Authenticates the Telegram polling loop. |
| `OPENROUTER_API_KEY` | ✅ | Primary AI provider key. Routes to any model on OpenRouter. |
| `ENABLE_TELEGRAM` | ✅ | Toggle the Telegram bot interface independently of the web platform. |
| `ENABLE_WEB` | ✅ | Toggle the web platform independently of the Telegram bot. |
| `OPENROUTER_MODEL` | — | Model string, e.g. `openai/gpt-4o-mini`. Controls cost vs. capability tradeoff. |
| `HF_TOKEN` | — | Hugging Face token. Required for document-aware image generation via FLUX.1-Krea-dev. |
| `HF_IMAGE_MODEL` | — | Image model path. Defaults to `black-forest-labs/FLUX.1-Krea-dev`. |
| `AI_PROVIDER` | — | Active AI backend: `openrouter`, `openai`, or `groq`. Swappable at runtime. |
| `WEB_PORT` | — | Port for the web platform server. Default: `3000`. |
| `WEB_SECRET_KEY` | — | Secret key for web session signing and JWT generation. Required for web platform. |
| `HALLUCINATION_THRESHOLD` | — | Confidence floor (0.0–1.0) below which claims are flagged. Default: `0.72`. |
| `DEFAULT_LANGUAGE` | — | Fallback language for generation when detection is inconclusive. Default: `en`. |

---

## 🎮 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize a new session and display the welcome message. |
| `/help` | Full command reference with usage examples. |
| `/chat` | Enter context-aware Q&A mode grounded to the active document. Auto-exits after 5 min inactivity. |
| `/analyze` | Re-run a full analysis report on the currently active document. |
| `/compare` | Compare the active document against a second uploaded document. Returns structural diff + semantic analysis. |
| `/generate` | Generate a DOCX or PDF from a topic prompt. Optionally ground in the active document for style/content. |
| `/image` | Generate an image using the active document or PPTX as context. Prompt is auto-enriched from document content. |
| `/gallery` | Browse your image gallery. Search by tag, document source, and date range. |
| `/errors` | Run smart error detection. Returns a structured report with severity levels and fix suggestions. |
| `/translate` | Translate the active document to a target language. Preserves formatting and structure. |
| `/stats` | Session usage statistics: documents processed, questions asked, images generated, tokens consumed. |
| `/language` | Show detected language and confidence for the active document. Override with `/language set [code]`. |
| `/clear` | Clear active document and reset session context. |
| `/cancel` | Cancel any in-progress operation immediately. |
| **Send a file** | Upload PDF, DOCX, XLSX, or PPTX to set it as the active document and trigger automatic analysis. |

---

## 🌐 Web Platform Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard home. Recent documents, quick upload, and usage stats at a glance. |
| `/upload` | Drag-and-drop upload. Supports PDF, DOCX, XLSX, PPTX. Triggers automatic analysis on upload. |
| `/documents` | Searchable document history. Filter by category, language, quality score, date, and tags. |
| `/documents/:id` | Full document view with analysis report, quality scores, category, tags, and Q&A chat panel. |
| `/compare` | Side-by-side document comparison with structural diff and semantic change analysis. |
| `/generate` | Document generation wizard. Enter a topic or reference an existing doc; download DOCX or PDF. |
| `/gallery` | Visual image gallery. Browse, search, and download AI-generated images by tag and document source. |
| `/team` | Team workspace. Shared documents, comment threads, member roles, and permission management. |
| `/settings` | User preferences: AI provider, language defaults, notification settings, API key management. |
| `/api/health` | Public health check endpoint showing service status and active AI provider. |

---

## 🔌 REST API

All endpoints accept `multipart/form-data` for file uploads. JSON responses include a `confidence` field and a `warnings` array for hallucination-related disclosures. Authentication uses Bearer tokens via the `Authorization` header.

```
POST   /api/analyze          # Analyze an uploaded document
POST   /api/chat             # Send a message to the context-aware chatbot
POST   /api/compare          # Compare two documents
POST   /api/generate/doc     # Generate DOCX or PDF from prompt
POST   /api/generate/image   # Generate image with doc/ppt context
POST   /api/translate        # Translate document to target language
POST   /api/errors           # Run smart error detection
GET    /api/gallery          # List user gallery images
GET    /api/stats            # Session usage statistics
GET    /api/health           # Service health + provider status
```

---

## 🏗️ System Architecture

Four interfaces, one shared engine:

| Layer | Component | Description |
|-------|-----------|-------------|
| **Interface** | Telegram Bot, Web Platform, REST API, CLI | All share the same core AI engine. Each handles its own session transport but delegates all intelligence to the shared service layer. |
| **Orchestration** | Context Manager | Tracks per-user state: active document, conversation history, detected language, and session preferences. Passes full context to every downstream call. |
| **Intelligence** | AI Engine (OpenRouter / OpenAI / Groq) | Provider-agnostic AI layer. Each operation type uses optimized prompt templates with anti-hallucination constraints injected at system level. |
| **Document Processing** | Parser + Chunker + Indexer | Handles PDF, DOCX, XLSX, PPTX. Extracts text, tables, and embedded metadata. Splits into semantically coherent chunks. Indexes into an in-process vector store for RAG. |
| **Image Generation** | Document-Aware Image Pipeline | Accepts a prompt plus a document as reference context. Derives enriched generation prompts from content, terminology, and structure. |
| **Error Handling** | Smart Error Detection Layer | Two-pass system: structural pass (parsing errors, malformed tables) and semantic pass (contradictions, missing sections). Errors returned as structured objects with location, severity, and suggested fix. |

### Anti-Hallucination Pipeline

Every AI response passes through 5 stages before reaching the user:

```
Stage 1: Retrieval          → Relevant chunks extracted from indexed document
Stage 2: Grounded Generation → AI generates with explicit source constraints
Stage 3: Claim Verification  → Each claim cross-checked against source chunks
Stage 4: Confidence Scoring  → Low-confidence claims flagged or withheld
Stage 5: Delivery            → Response with inline source references delivered
```

> When the system cannot verify a claim against source material, it says so. Fabrication is treated as a critical fault, not an acceptable fallback.

---

## 📋 Sample Analysis Report

```
Document Report
───────────────────────────────────────────────────────────

Language:          English (en) — 94% confidence
Category:          Technical Report — 81% confidence
Tags:              infrastructure, quarterly, compliance
Error Count:       2 warnings (low severity), 0 critical

Quality Score:     7.8 / 10 (Good)
  Clarity          8.4
  Grammar          9.1
  Coherence        6.9
  Completeness     7.0
  Professionalism  8.2

Stats:             3,410 words · 214 lines · ~14 pages

── AI Analysis (grounded, confidence: 0.91) ──────────────

Summary:           ...
Key Points:        ...
Identified Gaps:   ...
Action Items:      ...
Hallucination Log: 0 claims flagged
```

---

## ✅ Success Criteria

**Telegram:** User uploads a messy contract → gets instant analysis, auto-tags, and quality score → asks a question → gets answers grounded in actual document content, not hallucinations → sends two doc versions → sees exactly what changed, semantically.

**Web Platform:** Team member drags in a PDF via browser → reviews the visual analysis dashboard → shares the report with a colleague → both leave comments → manager downloads a generated follow-up document, all without touching Telegram.

**Both Platforms:** User in another country uploads a doc → works in their language from day one. Developer wants to swap AI providers → takes 5 minutes via config, not a rewrite. Feature works identically on bot and web.

---

*Intellidoc — AI Office Document Automation Platform · Documentation v3.0 · Telegram Bot + Web Platform · Python 3.10+*
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
