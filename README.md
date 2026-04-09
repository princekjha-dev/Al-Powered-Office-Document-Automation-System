# Intellidoc — AI Document Intelligence System

> A Telegram bot and web platform that acts as your smart office assistant.  
> Upload any document and it will analyze, summarize, compare, score, translate, and generate new documents for you — powered by AI with built-in anti-hallucination safeguards.

---

## Why This Exists

Three converging realities make this system worth building:

**1. Documents dominate office work.**  
Contracts, reports, proposals, invoices — people spend hours reading, summarizing, and comparing them manually. Most of that work is mechanical and repeatable.

**2. AI can handle the thinking.**  
Modern language models understand document content at depth. But most tools are clunky, require special software, or hallucinate facts without warning the user.

**3. Access should be universal.**  
Telegram is already on every phone globally. A web dashboard handles power users and developers. No installs, no accounts, no training required to start.

> **The insight:** if the interface is something people already use every day, the adoption barrier drops to zero. That is the design principle behind everything here.

---

## Two Interfaces, One Engine

Both interfaces share the same AI engine, document processor, context manager, and session state.

### Telegram Bot
- Zero-installation document intelligence — send a file directly in chat
- Conversational Q&A grounded to the active document
- Multi-turn session memory per user
- Command-based workflow: `/chat`, `/compare`, `/generate`, and more
- Works on any device with Telegram installed

### Web Platform + REST API
- Drag-and-drop document upload and management
- Side-by-side document comparison view
- Batch analysis across document collections
- REST API with Bearer token authentication
- Image gallery with search, filter, and export
- Session history and usage analytics

---

## Core Features

### Main Features

| Feature | Description |
|---------|-------------|
| **Context-Aware AI Chatbot** | Conversational AI grounded entirely in your uploaded document. Ask questions in plain English and receive answers sourced from the document text, not general knowledge. Maintains full conversation memory across turns. |
| **Anti-Hallucination Engine** | Every AI-generated claim is cross-referenced against source content before delivery. Configurable confidence threshold. The system says "I cannot find this in the document" rather than fabricating an answer. |
| **Smart Error Detection** | Two-pass linting: structural pass (broken references, malformed tables, encoding issues) and semantic pass (contradictions, missing sections, logical gaps). Each error returned with location, severity, and suggested fix. |
| **Multi-Language Intelligence** | Detects and processes 30+ languages natively. Analysis, Q&A, comparison, and generation all adapt to the document's language automatically. Cross-language comparison supported. |

### Core Features

| Feature | Description |
|---------|-------------|
| **Document Analysis** | Upload PDF, DOCX, XLSX, or PPTX. Receive: summary, five key points, one non-obvious insight, action items, entity extraction, quality scores, language detection, and auto-categorization. |
| **Document Comparison** | Structural diff plus semantic drift analysis. Shows what changed and what the meaning implications are — not just a text diff. |
| **Document-Aware Image Generation** | Generate contextual visuals for documents and presentations using the file as reference context. The system reads the document's content and terminology to derive an enriched generation prompt. |
| **Document Generation** | Generate a properly structured DOCX or PDF from a topic prompt. Can use an existing document as a style or content reference. |
| **Quality Scoring** | Five-dimension assessment (clarity, grammar, coherence, completeness, professionalism), each on a 10-point scale with actionable improvement notes. |
| **Auto-Categorization** | Classifies documents into category trees (contract, invoice, memo, report, proposal…) with a confidence score and extracted content tags. |
| **Session and Context Management** | Per-user session state tracks active document, conversation history, detected language, and preferences. Context threads through every operation. |
| **Image Gallery and Export** | Persistent per-user gallery, searchable by tag, source document, and date. Exportable as zip or embeddable into generated reports. |

---

## What Happens When You Upload a Document

Every upload triggers a five-stage pipeline automatically. No commands required for the initial report.

```
Stage 1 — Language Detection
  "Document detected in Spanish (94% confidence) — processing natively."

Stage 2 — Auto-Categorization
  "This looks like a Contract (87% confident). Tags: legal, payment, SLA."

Stage 3 — Error Detection
  Structural and semantic passes run simultaneously before AI analysis begins.

Stage 4 — Quality Scoring
  "Quality: 7.2 / 10 — Good clarity, but completeness could be improved."

Stage 5 — AI Analysis and Chat Readiness
  Summary + five key points + one non-obvious insight + action items.
  Document is now indexed. Conversation begins.
```

---

## Anti-Hallucination System

The system is designed to fail loudly — surfacing uncertainty rather than masking it.

> **Design principle:** When the system cannot verify a claim against source material, it says so. "I cannot find this in the document" is a valid and correct answer. Fabrication is treated as a critical fault, not an acceptable fallback.

**Five-stage verification pipeline:**

1. **Retrieval** — Relevant chunks extracted via semantic similarity search (sentence-transformers)
2. **Grounded Generation** — AI generates with explicit source constraints at the system prompt level; the model is instructed to cite or decline, never invent
3. **Claim Verification** — Each claim is cross-checked against retrieved source chunks
4. **Confidence Scoring** — Claims below `HALLUCINATION_THRESHOLD` are flagged inline or withheld
5. **Delivery** — Response delivered with inline source references and a hallucination log appended to the session record

---

## Quick Start

**Prerequisites:** Python 3.10+ — Telegram Bot Token (BotFather) — OpenRouter API Key  
Hugging Face token is optional; image generation falls back gracefully without it.

```bash
# 1. Clone and enter
git clone https://github.com/your-org/intellidoc
cd intellidoc

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your API keys

# 5. Verify setup
python setup.py

# 6. Run your preferred interface
python bot.py          # Telegram bot
python dashboard.py    # Web platform — http://localhost:5000
python cli.py          # Command-line interface
```

No Docker required. No database required for basic operation — all state is in-process per session.

---

## Configuration

```env
# Required
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key

# AI provider (swappable: openrouter | openai | groq)
AI_PROVIDER=openrouter
OPENROUTER_MODEL=openai/gpt-4o-mini

# Image generation (optional — falls back to placeholder without it)
HF_TOKEN=your_huggingface_token
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-Krea-dev

# Anti-hallucination
HALLUCINATION_THRESHOLD=0.72    # 0.0–1.0 confidence floor

# Language
DEFAULT_LANGUAGE=en             # Fallback when detection is inconclusive

# Session
SESSION_TIMEOUT_MINUTES=30      # Bot warns user at T-5 minutes
MAX_DOCUMENT_SIZE_MB=20
```

Swapping AI providers requires only a config key change — no code changes, no prompt rewrites.

---

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize a new session with quick-start guide |
| `/help` | Full command reference with usage examples |
| `/chat` | Context-aware Q&A mode grounded to the active document |
| `/analyze` | Re-run the full five-stage analysis pipeline |
| `/compare` | Compare active document against a second uploaded document |
| `/generate` | Generate DOCX or PDF from a topic prompt |
| `/image` | Generate image using active document or PPTX as reference context |
| `/gallery` | Browse image gallery — search by tag, document, date; export as zip |
| `/errors` | Run smart error detection — structured report with severity levels |
| `/translate` | Translate active document to a target language |
| `/quality` | Five-dimension quality scorecard with improvement notes |
| `/summary` | Re-generate AI summary for the active document |
| `/export` | Export session reports and chat history as DOCX or PDF bundle |
| `/stats` | Usage statistics: documents, questions, images, tokens |
| `/language` | Show detected language. Override with `/language set [code]` |
| `/clear` | Clear active document and reset context (gallery preserved) |
| `/cancel` | Cancel any in-progress operation |
| Send a file | Upload PDF, DOCX, XLSX, or PPTX to trigger automatic analysis |

---

## REST API

All endpoints accept `multipart/form-data` for file uploads.  
JSON responses include a `confidence` field and a `warnings[]` array for hallucination disclosures.  
Authentication: Bearer token in the `Authorization` header.

```
POST   /api/analyze              Full five-stage document analysis
POST   /api/chat                 Context-aware chatbot message
POST   /api/compare              Structural + semantic document comparison
POST   /api/generate/doc         Generate DOCX or PDF from prompt
POST   /api/generate/image       Generate image with doc/ppt reference context
POST   /api/translate            Translate document to target language
POST   /api/errors               Smart error detection report
POST   /api/quality              Five-dimension quality scorecard
POST   /api/export               Export session reports as DOCX or PDF bundle
GET    /api/gallery              List user gallery images
GET    /api/session              Current session state and active document
GET    /api/stats                Session usage statistics
DELETE /api/session              Clear session context
GET    /api/health               Service health and AI provider status
```

---

## Sample Analysis Output

```
Document Report
──────────────────────────────────────────────────

Language:          English (en) — 94% confidence
Category:          Technical Report — 81% confidence
Tags:              infrastructure, quarterly, compliance
Error Count:       2 warnings (low), 0 critical

Quality Score:     7.8 / 10  (Good)
  Clarity          8.4
  Grammar          9.1
  Coherence        6.9
  Completeness     7.0
  Professionalism  8.2

Stats:             3,410 words · 214 lines · ~14 pages

── AI Analysis (grounded, confidence: 0.91) ──────

Summary:           ...
Key Points:        1. ... 2. ... 3. ... 4. ... 5. ...
Main Insight:      ...
Identified Gaps:   ...
Action Items:      ...
Hallucination Log: 0 claims flagged
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.10+ |
| Telegram interface | python-telegram-bot |
| REST API and web dashboard | FastAPI |
| AI providers (swappable) | OpenRouter / OpenAI / Groq |
| RAG vector indexing | sentence-transformers |
| PDF parsing | PyPDF2 |
| DOCX read/write | python-docx |
| XLSX processing | openpyxl |
| PPTX parsing and generation | python-pptx |
| PDF generation | reportlab |
| Language detection | langdetect |
| Document-aware image generation | FLUX.1-Krea-dev via Hugging Face |
| Image processing | Pillow |

---

## Success Criteria

- User uploads a messy contract → Gets instant language detection, auto-categorization, error flags, quality score, and a grounded analysis report — before typing a single command.

- User asks "what are the payment terms?" → Gets an answer sourced directly from the document text with source reference and confidence score. If the document does not contain payment terms, the system says so.

- User sends two contract versions → Sees exactly what text changed and what the meaning implications are — not just a diff, but a semantic change summary.

- User in another country uploads a document in their language → System detects the language, processes it natively, delivers analysis in that language. No configuration needed.

- User asks for an image for their presentation → System reads the active PPTX, derives relevant visual context, generates an image suited to the presentation content.

- Developer wants to swap from OpenRouter to Groq → Change `AI_PROVIDER` in `.env`, restart. Done.

- User accesses the system via the web dashboard → Same document intelligence, same AI engine, same session context — in a browser with drag-and-drop upload and side-by-side comparison.

---

*Intellidoc — AI Document Intelligence System — Telegram Bot + Web Platform — Python 3.10+*
