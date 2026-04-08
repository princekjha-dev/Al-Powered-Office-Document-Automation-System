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

### 🎯 Hackathon Features
- Batch image generation for multiple prompts
- Document-based image suggestions
- Pattern recognition for visual content
- Automatic tag generation
- Download tracking for popular images
- Responsive error handling and user feedback

## 🎮 Commands

### Core Commands
- `/start` - Welcome message
- `/help` - Show all available commands
- `/cancel` - Cancel current operation

### Document Commands
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