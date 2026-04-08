# Al-Powered Office Document Automation System

A comprehensive Telegram bot that combines document analysis, generation, and AI-powered image creation for a complete office automation solution.

## ✨ What Makes This Different?

Unlike typical document automation tools, this system includes **5 advanced AI-powered differentiators**:

| Feature | Level | Benefit |
|---------|-------|---------|
| **RAG-Based Document Q&A** | 🆕 Advanced | Ask questions, get context-grounded answers |
| **Intelligent Document Comparison** | 🆕 Advanced | Detect structural + semantic changes |
| **Auto-Categorization** | 🆕 Advanced | Instantly classify documents with confidence |
| **Multi-Language Support** | 🆕 Advanced | 10+ languages with auto-detection |
| **Quality Scoring** | 🆕 Advanced | Assess 5 quality dimensions |
| **Anti-Hallucination Guards** | Core | Source-grounded analysis results |
| **Document-to-Image** | Core | Visually represent document concepts |
| **User Management** | Core | Track stats and usage patterns |

👉 **Perfect for**: Hackathons, document management systems, knowledge workers, students, research teams

## 🌟 Features

### 📄 Core Document Analysis
- Accept PDF, Word (.docx), Excel (.xlsx) files
- Auto-detect file type and process accordingly
- Extract text from documents
- AI-powered analysis using OpenRouter, OpenAI, Groq, or Gemini APIs
- Anti-hallucination guardrails for source-grounded results
- Returns: Summary, 5 Key Points, 1 Smart Insight, Action Items

### 🆕 Advanced Document Intelligence

#### 💬 Document Chat & Q&A (RAG)
- Ask natural language questions about uploaded documents
- Context-grounded answers using Retrieval Augmented Generation (RAG)
- Intelligent document chunking with embedding-based retrieval
- Fallback keyword matching for offline operation
- Full chat history persistence per document session
- *Command: `/ask`*

#### 🔍 Document Comparison
- Compare two documents line-by-line
- Identify additions, deletions, and structural changes
- Similarity ratio calculation
- AI-powered semantic change analysis
- Comparison reports with highlighted differences
- *Command: `/compare`*

#### 📂 Auto-Categorization & Tagging
- Automatic document type detection (10 categories)
- Smart tag generation from document content
- Confidence scoring for classification
- Document statistics and metadata extraction
- Supports: Contracts, Reports, Proposals, Invoices, Memos, Resumes, Manuals, Specifications, Newsletters, Emails
- *Command: `/category`*

#### 🌍 Multi-Language Support
- Auto-detect document language (10+ languages)
- Language-aware processing
- Confidence scoring for detection
- AI-powered translation capability
- Supports: English, Spanish, French, German, Chinese, Japanese, Portuguese, Russian, Italian, Korean
- *Command: `/language`*

#### 📊 Document Quality Scoring
- Multi-dimensional quality assessment
- Scores: Clarity, Completeness, Coherence, Grammar, Professionalism
- Overall quality rating (0-10)
- Automated improvement suggestions
- Text preview generation
- *Command: `/quality`*

### ✏️ Document Generation
- Generate professional documents from AI prompts
- Choose between Word (.docx) or PDF format
- Auto-formatted with sections, headers, and proper structure
- Customizable document templates and styles

### 🎨 Image Generation
- Generate images from text prompts using AI
- Multiple style options: Realistic, Abstract, Artistic
- **Document-to-Image**: Automatically generate images based on document content
- Extract key concepts and create relevant visual representations
- Perfect for assignments, presentations, and reports

### 📸 Image Gallery & Management
- Persistent image gallery with metadata
- Gallery statistics and analytics
- Search images by tags or keywords
- Track popular generated images
- Export gallery data (JSON, CSV)
- Advanced filtering and organization

### 🎯 Enterprise Features
- RESTful API for programmatic access
- Command-line interface (CLI) for batch operations
- Web dashboard for management
- Async task queue (Celery) for background jobs
- Comprehensive user management and statistics
- Production-ready logging and error handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- AI API Key (OpenRouter recommended)
- Optional: Redis for async tasks

### Dependencies

**Core:**
- python-telegram-bot (Telegram integration)
- requests (HTTP client)
- python-dotenv (Configuration management)
- flask (Web server)

**Document Processing:**
- PyPDF2 (PDF parsing)
- python-docx (DOCX handling)
- openpyxl (Excel handling)
- reportlab (PDF generation)
- pillow (Image processing)

**🆕 Advanced Features:**
- sentence-transformers (RAG embeddings) - For intelligent document Q&A
- langdetect (Language detection) - Auto-detect 10+ languages
- numpy (Numerical operations) - Embedding calculations

**Utilities:**
- click (CLI framework)
- tabulate (Table formatting)
- tqdm (Progress bars)

### Installation

```bash
# 1. Clone and install
git clone <repo-url>
cd Al-Powered-Office-Document-Automation-System
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 3. Verify setup
python test_bot.py

# 4. Run bot
python bot.py
```

## 📖 Full Documentation

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for:
- Complete setup instructions
- API documentation with curl examples
- CLI usage guide
- Example commands and code samples
- Testing procedures
- Advanced configuration
- Troubleshooting guide

## 🎮 Commands

### Core Commands
- `/start` - Welcome message
- `/help` - Show all available commands
- `/cancel` - Cancel current operation

### Document Commands
- Send document (PDF/DOCX/XLSX) for analysis
- `/generate` - Generate new documents from prompts
- `/compare` - Compare two documents (structural & semantic)
- `/category` - Auto-categorize document and generate tags
- `/quality` - Check document quality with detailed breakdown

### Chat & Q&A Commands
- `/ask` - Ask natural language questions about documents
- Get context-grounded answers using RAG
- Full conversation history per document session

### Language Commands
- `/language` - Detect document language
- Get language with confidence score
- Translate content to supported languages

### Image Commands
- `/image` - Generate images from prompts
- `/gallery` - View your generated images
- `/gallery_stats` - Gallery statistics and analytics

## 💻 Interfaces

### Telegram Bot
```bash
python bot.py
```

### Web Dashboard
```bash
python dashboard.py
# Access at http://localhost:5000
```

### Command-Line Interface
```bash
python cli.py --help
python cli.py document analyze file.pdf
python cli.py image generate --prompt "A beautiful sunset"
```

### REST API
```bash
curl -X POST http://localhost:5000/api/documents/analyze \
  -F "file=@document.pdf"
```

## 🏗️ Project Structure

```
├── bot.py                       # Telegram bot with all features
├── dashboard.py                 # Web dashboard
├── cli.py                       # Command-line interface
│
├── src/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── models/
│   │   ├── user.py              # User management
│   │   └── storage.py           # Gallery storage
│   ├── services/
│   │   ├── ai_generation.py     # AI text/image generation
│   │   ├── document_reader.py   # PDF/DOCX/XLSX parsing
│   │   ├── document_generator.py # Document creation
│   │   ├── image_generator.py   # Image generation
│   │   ├── image_gallery.py     # Gallery management
│   │   ├── document_chat.py     # 🆕 RAG-based Q&A
│   │   ├── document_comparison.py # 🆕 Document diff & analysis
│   │   ├── document_categorization.py # 🆕 Auto categorization
│   │   ├── language_detection.py # 🆕 Multi-language support
│   │   └── document_quality.py  # 🆕 Quality scoring
│   └── utils/
│       └── helpers.py           # Utility functions
│
├── tests/
│   ├── test_integration.py      # Integration tests
│   └── test_services.py         # Service tests
│
└── requirements.txt             # Dependencies
```

## 🔌 Core Services

### AIGenerationService
- Document analysis and summarization
- Content generation with customizable prompts
- Image prompt generation from documents
- Built-in hallucination reduction instructions
- Fact-check verification for analysis outputs
- Support for multiple AI providers (OpenRouter, OpenAI, Groq, Gemini)

### 🆕 Advanced Services

#### DocumentChat (RAG)
```python
from src.services.document_chat import DocumentChat

chat = DocumentChat()
session_id = chat.create_session(document_text, user_id)
answer = chat.answer_question(session_id, "What are key points?", ai_service)
```
- Intelligent document chunking (300 chars, 50 char overlap)
- Embedding-based retrieval using Sentence Transformers
- Fallback keyword matching when embeddings unavailable
- Stores embeddings and chat history per session

#### DocumentComparison
```python
from src.services.document_comparison import DocumentComparison

comparison = DocumentComparison()
report = comparison.generate_comparison_report(doc1, doc2, ai_service)
# Returns: summary, key_changes, semantic_analysis, similarity_ratio
```
- Line-by-line diff analysis
- Similarity ratio calculation (0-1 scale)
- AI-powered semantic change detection
- JSON report export

#### DocumentCategorization
```python
from src.services.document_categorization import DocumentCategorization

categorizer = DocumentCategorization()
analysis = categorizer.analyze_document(text, ai_service)
# Returns: category, confidence, tags, statistics
```
- 10 predefined document categories
- Keyword-based primary detection + AI fallback
- Auto-generated tags from content
- Document statistics (words, lines, pages)
- Confidence scoring

#### LanguageDetection
```python
from src.services.language_detection import LanguageDetection

detector = LanguageDetection()
lang_info = detector.detect_language(text)
# Returns: language, language_name, confidence, is_confident
```
- Supports 10+ languages
- Uses langdetect library with keyword fallback
- Confidence scoring for reliability
- Translation capability via AI service
- Language-aware document processing

#### DocumentQuality
```python
from src.services.document_quality import DocumentQuality

quality = DocumentQuality()
scores = quality.score_document(text)
# Returns: clarity, completeness, coherence, grammar, professionalism, overall
```
- 5-dimensional quality assessment
- Clarity (sentence structure analysis)
- Completeness (structure/sections detection)
- Coherence (transition word analysis)
- Grammar (basic checks)
- Professionalism (tone & vocabulary)
- Automated improvement suggestions

### DocumentReader
- PDF text extraction
- DOCX parsing
- XLSX parsing

### DocumentGenerator
- DOCX creation
- PDF creation
- Formatting and styling

### ImageGenerator
- Image generation from prompts
- Batch processing
- Multiple style support

### ImageGalleryService
- Gallery management
- Search and filtering
- Analytics and statistics

## 🔐 Configuration

Edit `.env` file:

```env
# Required
TELEGRAM_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key

# Optional AI Providers
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# Image Generation
HUGGINGFACE_API_KEY=your_hf_key
IMAGE_GENERATION_ENABLED=true
DEFAULT_IMAGE_STYLE=realistic

# Advanced Features
ENABLE_IMAGE_GALLERY=true
MAX_IMAGES_PER_DOCUMENT=3

# Storage & Performance
MAX_FILE_SIZE_MB=20
CLEANUP_INTERVAL_HOURS=24
SESSION_TIMEOUT_HOURS=24
AUTO_CLEANUP_ENABLED=true

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Advanced Configuration Options

**Document Chat (RAG):**
- Automatically uses Sentence Transformers for embeddings
- Falls back to keyword matching if embeddings unavailable
- Stores sessions in `data/chat_sessions/`

**Language Detection:**
- Uses langdetect library for 10+ language detection
- Falls back to keyword matching offline
- Confidence threshold: 30% for reliable detection

**Document Quality:**
- Assesses 5 dimensions: clarity, completeness, coherence, grammar, professionalism
- Provides automated improvement suggestions
- Quality scale: 0-10 (0: needs improvement, 10: excellent)

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_services.py -v
python -m pytest tests/test_integration.py -v

# Run without Celery
python test_bot.py
```

## 📊 API Endpoints

- `GET /api/health` - Health check
- `POST /api/users` - Create user
- `GET /api/users/<id>` - Get user
- `POST /api/documents/analyze` - Analyze document
- `POST /api/documents/generate` - Generate document
- `POST /api/images/generate` - Generate image
- `GET /api/galleries/<id>` - Get gallery
- `GET /api/galleries/<id>/stats` - Gallery stats

Full API documentation in [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md#-api-documentation)

## 🎯 Example Workflows

### 1. Complete Document Analysis Workflow
```
User → Uploads document
Bot → 🌍 Detects language
Bot → 📂 Auto-categorizes with confidence
Bot → 📊 Scores document quality (5 dimensions)
Bot → ✅ Provides AI-powered analysis
User → Saves insights
```

### 2. Smart Document Q&A
```
User → Uploads document
Bot → 💬 Creates RAG session
User → "What are the main points?"
Bot → Retrieves context, generates answer grounded in document
User → "Tell me more about X"
Bot → Answers based on document context
```

### 3. Document Comparison & Diff
```
User → Uploads first document
User → 🔍 Chooses "Compare"
Bot → Analyzes structure (additions/deletions)
Bot → 🧠 Performs semantic analysis
User → Gets side-by-side differences + insights
```

### 4. Analyze and Generate Images from Document
```
User → Uploads document (auto-detects language)
Bot → Extracts text & categorizes
Bot → 🎨 Generates 3 images from key concepts
User → Saves images to personal gallery
```

### 5. Batch Image Generation
```
User → Provides list of prompts via CLI
System → Queues background tasks
System → Generates images asynchronously
User → Downloads batch results
```

### 6. Multi-Language Document Processing
```
User → Uploads document in Spanish
Bot → 🌍 Detects Spanish with 95% confidence
Bot → Analyzes in Spanish context
User → Results available, can translate if needed
```

## ⚙️ Advanced Features

### User Management
```python
from src.models.user import UserManager

manager = UserManager()
user = manager.create_or_get_user(123456, "john_doe")
manager.update_user_statistics(123456, documents_processed=1)
```

### Custom AI Models
Change in `.env`:
```env
AI_PROVIDER=groq
GROQ_API_KEY=your_key
```

## 🐛 Troubleshooting

**Missing API Key:**
```
Error: OPENROUTER_API_KEY is required
→ Get key from openrouter.ai and add to .env
```

**Module not found:**
```
Error: ModuleNotFoundError
→ Run: pip install -r requirements.txt
```

**Redis connection failed:**
```
Error: Connection to Redis refused
→ Start Redis: redis-server
→ Or disable async tasks
```

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md#-troubleshooting) for more solutions.

## 📝 Code Quality

- ✅ Type hints on all functions
- ✅ Comprehensive docstrings
- ✅ Unit tests for services
- ✅ Integration tests for workflows
- ✅ Proper error handling and logging
- ✅ SOLID principles followed
- ✅ Clean, modular architecture

## 🏆 Hackathon Competitive Advantages

This project stands out with 5 unique advanced features not found in typical automation tools:

1. **RAG-Based Document Q&A** - Full-featured document chatting with grounded answers
2. **Semantic Document Comparison** - Understand what changed between versions intelligently
3. **Auto-Categorization** - Auto-tag and classify documents instantly
4. **Multi-Language Support** - Process documents in 10+ languages with confidence scores
5. **Quality Scoring** - Comprehensive 5-dimensional quality assessment with suggestions

**Result**: A complete, production-ready document automation system that demonstrates advanced AI/ML capabilities, clean architecture, and real-world usefulness.

## 📚 Learning Resources

- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Complete implementation guide
- [QUICKSTART.md](QUICKSTART.md) - Get started in 3 minutes
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture overview

## 🤝 Contributing

Contributions welcome! Please:
1. Test your changes
2. Add unit tests
3. Update documentation
4. Follow code style (PEP 8)

## 📄 License

This project is provided as-is for educational and development purposes.

---

**Need Help?** Check [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for detailed documentation, API examples, and troubleshooting.

**Version:** 1.0.0  
**Last Updated:** January 2024  
**Status:** Production Ready ✅

- `/generate` - Generate a new Al-powered document
  - Choose format: Word (.docx) or PDF
  - Custom styling and sections

### Image Commands
- `/image` - Generate images from text prompts
  - Choose: Realistic, Abstract, Artistic styles
  - Multiple images per session
  
- `/gallery` - View your generated images
  - See all images with metadata
  - View prompts, styles, and creation dates
  
- `/gallery_stats` - View gallery statistics
  - Total images and downloads
  - Style breakdown
  - Most popular images
  
- `/search_images <keyword>` - Search gallery by keyword
  - Search by prompt keywords
  - Filter by tags

### Document Features
- **Upload Documents** - Send PDF, DOCX, or XLSX files for:
  - AI analysis and summary
  - Key insights and recommendations
  - Automatic image generation suggestions
  - Batch processing support

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Bot Framework**: python-telegram-bot 20.7
- **API Integration**:
  - OpenRouter (text generation & analysis)
  - Hugging Face (image generation)
  - OpenAI, Groq, Gemini (optional)
  
- **Document Processing**:
  - PyPDF2 (PDF reading)
  - python-docx (Word files)
  - openpyxl (Excel files)
  - reportlab (PDF generation)
  
- **Utilities**:
  - Pillow (image processing)
  - requests (API calls)
  - python-dotenv (configuration)

## 📋 Setup

1. Clone the repository
2. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```env
   # Telegram
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   
   # Text Generation & Analysis
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=gpt-4o-mini
   OPENAI_API_KEY=your_openai_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   GEMII_API_KEY=your_gemii_api_key_here
   AI_PROVIDER=openrouter
   
   # Image Generation
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   IMAGE_GENERATION_ENABLED=true
   DEFAULT_IMAGE_STYLE=realistic
   MAX_IMAGES_PER_DOCUMENT=3
   ENABLE_IMAGE_GALLERY=true
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## ⚙️ Configuration

### Environment Variables
- `TELEGRAM_TOKEN` - (Required) Your Telegram bot token
- `OPENROUTER_API_KEY` - (Required) API key for text generation
- `HUGGINGFACE_API_KEY` - (Optional) For image generation
- `IMAGE_GENERATION_ENABLED` - (Default: true) Enable/disable image features
- `DEFAULT_IMAGE_STYLE` - (Default: realistic) Default image generation style
- `MAX_IMAGES_PER_DOCUMENT` - (Default: 3) Max images to generate from documents
- `ENABLE_IMAGE_GALLERY` - (Default: true) Enable gallery features

### Advanced Configuration
- Edit `config.py` to add or modify AI providers
- Customize image styles and generation parameters
- Adjust document formatting in `document_generator.py`
- Modify gallery storage path in `image_gallery.py`

## ⚠️ Error Handling

- **File Size** (>20MB) → Error message with size limit info
- **Unsupported File** → List of supported formats
- **API Failures** → Automatic retry with user notification
- **Image Generation Timeout** → Graceful fallback to placeholder
- **Missing API Keys** → Clear error messages indicating what's needed
- **Gallery Issues** → Automatic recovery with fresh gallery backup

## 📁 Project Structure

```
├── bot.py                    # Main bot logic, command handlers
├── document_reader.py        # Extract text from PDF, DOCX, XLSX
├── document_generator.py     # Generate Word (.docx) and PDF documents
├── image_generator.py        # AI image generation from prompts
├── image_gallery.py          # Gallery management, search, and stats
├── openrouter_handler.py     # API calls for text generation
├── config.py                 # Configuration and environment variables
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env                      # API keys (not committed)
└── .env.example              # Example environment variables
```

## 🎯 Use Cases

### For Students
- Upload assignments and get AI analysis
- Generate related images for presentations
- Create study documents from notes
- Gallery of generated educational materials

### For Professionals
- Quick document summarization
- Professional document generation
- Visual content creation for reports
- Batch processing of multiple documents

### For Content Creators
- Generate images for blog posts
- Create pattern suggestions
- Build visual content libraries
- Track popular image styles

## 🚀 Advanced Features

### Batch Processing
```python
# Generate multiple images in one command
prompts = ["nature landscape", "abstract art", "modern city"]
images = image_generator.generate_batch(prompts)
```

### Gallery Export
```python
# Export all images and metadata
json_data = image_gallery.export_gallery("json")
csv_data = image_gallery.export_gallery("csv")
```

### Search & Filter
```python
# Find images by tags or keywords
results = image_gallery.search_by_tag("document-generated")
results = image_gallery.search_by_prompt("assignment")
```

## 📊 Performance

- Fast document parsing (< 2 seconds for most files)
- Efficient image caching and storage
- Optimized gallery queries with metadata indexing
- Automatic cleanup of temporary files
- Memory-efficient batch processing

## 🔐 Privacy & Security

- All API keys stored in `.env` (never committed)
- Local gallery storage (no cloud dependency)
- User-specific image filtering
- Automatic session cleanup
- No data persistence without permission

## 🐛 Troubleshooting

### Images not generating?
1. Check `HUGGINGFACE_API_KEY` is set
2. Verify internet connection
3. Check model availability on Hugging Face
4. Use placeholder mode for testing

### Document parsing fails?
1. Ensure file is not corrupted
2. Check file size (< 20MB)
3. Verify file format (PDF/DOCX/XLSX)
4. Try re-uploading the file

### Gallery not loading?
1. Check `/tmp/image_gallery/` directory permissions
2. Verify `gallery.json` is not corrupted
3. Clear cache and restart bot
4. Check available disk space