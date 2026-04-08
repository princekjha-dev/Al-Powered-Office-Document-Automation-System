"""
Main bot application with reorganized structure.
Uses modular services and proper user management.
"""

import os
import sys
import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,
    filters, ConversationHandler
)

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import get_config, Config
from src.utils.helpers import setup_logging, get_logger
from src.models.user import UserManager
from src.models.storage import UserGalleryStorage, SessionStorage
from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator
from src.services.image_generator import ImageGenerator
from src.services.image_gallery import ImageGalleryService
from src.services.ai_generation import AIGenerationService

# Setup logging
setup_logging(log_level=Config.LOG_LEVEL)
logger = get_logger(__name__)

# Conversation states
GENERATE_TOPIC, GENERATE_FORMAT = range(2)
IMAGE_PROMPT, IMAGE_STYLE = range(2, 4)

# Global service instances
class BotServices:
    """Container for bot services."""
    user_manager: UserManager = None
    storage: UserGalleryStorage = None
    sessions: SessionStorage = None
    ai_service: AIGenerationService = None
    image_service: ImageGenerator = None
    gallery_service: ImageGalleryService = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    # Create or get user
    db_user = BotServices.user_manager.create_or_get_user(
        user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or ""
    )
    
    await update.message.reply_text(
        f"Welcome {user.first_name}! 👋\n\n"
        "This is your AI-powered Document & Image Assistant.\n"
        "Send documents for analysis, generate new documents, or create images.\n"
        "Use /help for all available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "🤖 *AI-Powered Document & Image Assistant*\n\n"
        "*Document Features:*\n"
        "📄 Send documents (PDF, DOCX, XLSX) for:\n"
        "   • AI analysis & summary\n"
        "   • Key points & insights\n\n"
        "✏️ `/generate` - Create AI-powered documents\n"
        "   • Choose format (Word/PDF)\n\n"
        "*Image Generation:*\n"
        "🎨 `/image` - Generate images from prompts\n"
        "📸 `/gallery` - View your generated images\n"
        "📊 `/gallery_stats` - Gallery statistics\n\n"
        "*Settings:*\n"
        "/cancel - Cancel current operation"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded documents."""
    user_id = update.effective_user.id
    document = update.message.document
    
    if not document:
        await update.message.reply_text("Please send a document file.")
        return

    file_name = document.file_name
    
    # Check supported file type
    if not DocumentReader.is_supported_file(file_name):
        await update.message.reply_text("❌ Unsupported file type (PDF, DOCX, XLSX only)")
        return

    # Download file
    file = await context.bot.get_file(document.file_id)
    file_path = os.path.join(Config.TEMP_DIR, file_name)
    await file.download_to_drive(file_path)

    try:
        # Check file size
        if not DocumentReader.check_file_size(file_path):
            await update.message.reply_text(f"❌ File too large (max: {Config.MAX_FILE_SIZE_MB}MB)")
            return

        await update.message.reply_text("🔄 Analyzing your document...")
        
        # Extract text
        text = DocumentReader.extract_text(file_path)
        if not text.strip():
            await update.message.reply_text("❌ Could not extract text from document")
            return

        # Analyze with AI
        analysis = BotServices.ai_service.analyze_document(text)
        await update.message.reply_text(analysis)

        # Store for image generation
        context.user_data['last_document_text'] = text

        # Update user statistics
        BotServices.user_manager.update_user_statistics(user_id, documents_processed=1)

        # Offer image generation
        if Config.IMAGE_GENERATION_ENABLED:
            keyboard = [['🎨 Generate Images', '❌ Skip']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                "Would you like to generate images from this document?",
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def generate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start document generation."""
    await update.message.reply_text(
        "📝 *Document Generator*\n\n"
        "What would you like to generate a document about?\n"
        "Example: 'Python best practices', 'Marketing strategy 2024'"
    )
    return GENERATE_TOPIC


async def generate_topic_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive document topic."""
    topic = update.message.text
    context.user_data['topic'] = topic
    
    keyboard = [['Word (.docx)', 'PDF']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Great! Topic: *{topic}*\n\nChoose format:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return GENERATE_FORMAT


async def generate_format_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate and send document."""
    user_id = update.effective_user.id
    format_choice = update.message.text
    topic = context.user_data.get('topic', 'Document')
    
    await update.message.reply_text("⏳ Generating document...", reply_markup=ReplyKeyboardRemove())
    
    try:
        # Generate content
        content = BotServices.ai_service.generate_document(topic)
        
        # Create document
        if 'Word' in format_choice:
            file_path = DocumentGenerator.generate_docx(topic, content, output_dir=Config.TEMP_DIR)
        else:
            file_path = DocumentGenerator.generate_pdf(topic, content, output_dir=Config.TEMP_DIR)
        
        # Send document
        with open(file_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                caption=f"✅ Document created!\n*Topic:* {topic}\n*Format:* {format_choice}",
                parse_mode='Markdown'
            )
        
        # Update statistics
        BotServices.user_manager.update_user_statistics(user_id, documents_generated=1)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await update.message.reply_text("Use /generate to create another document")
        
    except Exception as e:
        logger.error(f"Error generating document: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    return ConversationHandler.END


async def image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start image generation."""
    await update.message.reply_text(
        "🎨 *Image Generator*\n\n"
        "Describe the image you want:\n"
        "Example: 'A futuristic city with neon lights'"
    )
    return IMAGE_PROMPT


async def image_prompt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive image prompt."""
    prompt = update.message.text
    context.user_data['image_prompt'] = prompt
    
    keyboard = [['Realistic', 'Abstract'], ['Artistic', 'Skip']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Image: *{prompt}*\n\nChoose style:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return IMAGE_STYLE


async def image_style_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate image."""
    user_id = update.effective_user.id
    style = update.message.text.lower().split()[0]
    prompt = context.user_data.get('image_prompt', 'artwork')
    
    style_map = {'realistic': 'realistic', 'abstract': 'abstract', 'artistic': 'artistic', 'skip': None}
    style = style_map.get(style, 'realistic')
    
    if style is None:
        await update.message.reply_text("Skipped. Use /image anytime.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    await update.message.reply_text("🔄 Generating image...", reply_markup=ReplyKeyboardRemove())
    
    try:
        # Generate image
        image_path = BotServices.image_service.generate_from_prompt(
            prompt, style, output_dir=Config.TEMP_DIR
        )
        
        # Add to gallery
        entry = BotServices.gallery_service.add_image(
            user_id, image_path, prompt,
            tags=['user-generated', style], style=style
        )
        
        # Send image
        with open(image_path, 'rb') as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"✅ Generated!\n*ID:* {entry['id']}\n*Style:* {style}"
            )
        
        # Update statistics
        BotServices.user_manager.update_user_statistics(user_id, images_generated=1)
        
        if os.path.exists(image_path):
            os.remove(image_path)
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    await update.message.reply_text("Use /image to generate more")
    return ConversationHandler.END


async def gallery_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user's gallery."""
    user_id = update.effective_user.id
    images = BotServices.gallery_service.get_gallery_summary(user_id, limit=5)
    
    if not images:
        await update.message.reply_text("📸 Your gallery is empty. Use /image to generate images.")
        return
    
    message = "📸 *Your Images*\n\n"
    for img in images:
        message += f"*ID:* {img['id']}\n*Prompt:* {img['prompt'][:40]}...\n*Style:* {img['style']}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def gallery_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display gallery statistics."""
    user_id = update.effective_user.id
    stats = BotServices.gallery_service.get_gallery_stats(user_id)
    
    message = (
        "📊 *Your Statistics*\n\n"
        f"Total Images: {stats['total_images']}\n"
        f"Total Downloads: {stats['total_downloads']}\n"
        f"Gallery Size: {stats['gallery_size'] / 1024 / 1024:.2f} MB\n"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel operation."""
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    """Main bot function."""
    
    try:
        Config.validate()
        Config.create_directories()
    except EnvironmentError as e:
        logger.error(f"Configuration error: {e}")
        return

    logger.info("Starting bot...")
    
    # Initialize services
    BotServices.user_manager = UserManager(Config.USERS_DIR)
    BotServices.storage = UserGalleryStorage(Config.GALLERIES_DIR)
    BotServices.sessions = SessionStorage(Config.SESSIONS_DIR)
    BotServices.ai_service = AIGenerationService()
    
    if Config.IMAGE_GENERATION_ENABLED:
        BotServices.image_service = ImageGenerator(Config.HUGGINGFACE_API_KEY)
        BotServices.gallery_service = ImageGalleryService(BotServices.storage)
        logger.info("Image generation enabled")
    
    # Create application
    app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Document generation
    gen_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate_start)],
        states={
            GENERATE_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_topic_received)],
            GENERATE_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_format_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(gen_handler)
    
    # Image generation
    if Config.IMAGE_GENERATION_ENABLED:
        img_handler = ConversationHandler(
            entry_points=[CommandHandler("image", image_start)],
            states={
                IMAGE_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_prompt_received)],
                IMAGE_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_style_received)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        app.add_handler(img_handler)
        app.add_handler(CommandHandler("gallery", gallery_view))
        app.add_handler(CommandHandler("gallery_stats", gallery_stats))
    
    # Document handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    logger.info("Bot initialized successfully")
    app.run_polling()


if __name__ == '__main__':
    main()
