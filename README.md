# AI-Powered Office Document & Image Automation System

A comprehensive Telegram bot that combines document analysis, generation, and AI-powered image creation for a complete office automation solution.

## 🌟 Features

### 📄 Document Analysis
- Accept PDF, Word (.docx), Excel (.xlsx) files
- Auto-detect file type and process accordingly
- Extract text from documents
- AI-powered analysis using OpenRouter, OpenAI, Groq, or Gemini APIs
- Returns: Summary, 5 Key Points, 1 Smart Insight, Action Items

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
- `/generate` - Generate new documents
- Get AI analysis, key points, and insights

### Image Commands
- `/image` - Generate images from prompts
- `/gallery` - View your generated images
- `/gallery_stats` - Gallery statistics

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
├── bot.py                 # Telegram bot
├── dashboard.py           # Web dashboard
├── cli.py                 # Command-line interface
│
├── src/
│   ├── config/           # Configuration
│   ├── models/           # Data models (User, Storage)
│   ├── services/         # Business logic
│   │   ├── ai_generation.py
│   │   ├── document_reader.py
│   │   ├── document_generator.py
│   │   ├── image_generator.py
│   │   └── image_gallery.py
│   └── utils/           # Helpers
│
├── tests/               # Unit & Integration tests
└── requirements.txt     # Dependencies
```

## 🔌 Core Services

### AIGenerationService
- Document analysis
- Content generation
- Image prompt generation

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

# Optional
HUGGINGFACE_API_KEY=your_hf_key
IMAGE_GENERATION_ENABLED=true
LOG_LEVEL=INFO
DEBUG=false
```

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

### 1. Analyze and Generate Images from Document
```
User → Uploads document
Bot → Extracts text & analyzes
Bot → Generates 3 images from document
User → Saves images to personal gallery
```

### 2. Generate Report Documents
```
User → Requests document on topic
Bot → Generates content using AI
Bot → Formats as DOCX or PDF
User → Downloads formatted report
```

### 3. Batch Image Generation
```
User → Provides list of prompts via CLI
System → Queues background tasks
System → Generates images asynchronously
User → Downloads batch results
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

## 📚 Learning Resources

- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Complete implementation guide
- [QUICKSTART.md](QUICKSTART.md) - Get started in 3 minutes
- [HACKATHON_README.md](HACKATHON_README.md) - Hackathon-specific features

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

- `/generate` - Generate a new AI-powered document
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