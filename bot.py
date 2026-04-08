#!/usr/bin/env python3
"""
Simplified AI-Powered Document Automation Bot - Hackathon Edition.

Core features:
- Document analysis (PDF, DOCX, XLSX)
- AI-powered insights and summarization
- Image generation from documents
- Image gallery management
"""

import os
import sys
import logging
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,
    filters, ConversationHandler
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import Config
from src.utils.helpers import setup_logging, get_logger, format_file_size
from src.models.user import UserManager
from src.models.storage import UserGalleryStorage
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

# Services container
class Services:
    user_manager: Optional[UserManager] = None
    storage: Optional[UserGalleryStorage] = None
    ai_service: Optional[AIGenerationService] = None
    image_service: Optional[ImageGenerator] = None
    gallery_service: Optional[ImageGalleryService] = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler."""
    user = update.effective_user
    Services.user_manager.create_or_get_user(
        user.id,
        username=user.username or "",
        first_name=user.first_name or ""
    )
    
    await update.message.reply_text(
        f"👋 Welcome, {user.first_name}!\n\n"
        "🤖 *AI Document Automation*\n\n"
        "📄 Send documents for instant analysis\n"
        "✏️ Generate professional documents\n"
        "🎨 Create AI images from prompts\n"
        "📸 Manage your image gallery\n\n"
        "Use /help for commands 👇",
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler."""
    help_text = (
        "📚 *Commands*\n\n"
        "*Documents:*\n"
        "📄 Send any file (PDF/DOCX/XLSX) → get AI analysis\n"
        "/generate - Create a document\n\n"
        "*Images:*\n"
        "/image - Generate an image\n"
        "/gallery - View images\n"
        "/stats - Your statistics\n\n"
        "/cancel - Stop current operation"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document uploads and analyze."""
    user_id = update.effective_user.id
    document = update.message.document
    
    if not DocumentReader.is_supported_file(document.file_name):
        await update.message.reply_text("❌ Unsupported file (PDF, DOCX, XLSX only)")
        return

    await update.message.reply_text("⏳ Analyzing document...")
    
    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(Config.TEMP_DIR, document.file_name)
        await file.download_to_drive(file_path)

        try:
            # Extract and analyze
            text = DocumentReader.extract_text(file_path)
            if not text.strip():
                await update.message.reply_text("❌ Could not extract text from file")
                return
            
            analysis = Services.ai_service.analyze_document(text)
            await update.message.reply_text(f"✅ *Analysis:*\n\n{analysis}", parse_mode='Markdown')
            
            # Ask about image generation
            keyboard = [['🎨 Generate Images', '❌ Skip']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                "Generate images from this document?",
                reply_markup=reply_markup
            )
            
            # Store document text
            context.user_data['last_doc_text'] = text
            Services.user_manager.update_user_statistics(user_id, documents_processed=1)
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"Document error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_generate_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate images from document text."""
    if update.message.text == '❌ Skip':
        await update.message.reply_text("Skipped", reply_markup=ReplyKeyboardRemove())
        return
    
    user_id = update.effective_user.id
    text = context.user_data.get('last_doc_text', '')
    
    if not text:
        await update.message.reply_text("No document in memory", reply_markup=ReplyKeyboardRemove())
        return

    await update.message.reply_text("🔄 Generating images...", reply_markup=ReplyKeyboardRemove())
    
    try:
        # Generate image prompts from document
        prompts = Services.ai_service.generate_image_prompts(text, count=2)
        
        for i, prompt in enumerate(prompts, 1):
            await update.message.reply_text(f"📸 Image {i}/2...")
            image_path = Services.image_service.generate_from_prompt(prompt, "realistic")
            
            # Add to gallery
            Services.gallery_service.add_image(
                user_id, image_path, prompt,
                tags=['document', 'auto'], style='realistic'
            )
            
            # Send image
            with open(image_path, 'rb') as f:
                await update.message.reply_photo(
                    photo=f,
                    caption=f"_{prompt}_",
                    parse_mode='Markdown'
                )
            
            if os.path.exists(image_path):
                os.remove(image_path)
        
        Services.user_manager.update_user_statistics(user_id, images_generated=2)
        await update.message.reply_text("✅ Images saved to gallery!")
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def generate_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start document generation."""
    await update.message.reply_text(
        "📝 What document would you like?\n"
        "(Example: 'Python Best Practices')"
    )
    return GENERATE_TOPIC


async def generate_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get document topic."""
    topic = update.message.text
    context.user_data['topic'] = topic
    
    keyboard = [['Word (.docx)', 'PDF']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Topic: *{topic}*\n\nFormat?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return GENERATE_FORMAT


async def generate_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generate document."""
    user_id = update.effective_user.id
    format_choice = update.message.text
    topic = context.user_data.get('topic', 'Document')
    
    await update.message.reply_text("⏳ Generating...", reply_markup=ReplyKeyboardRemove())
    
    try:
        content = Services.ai_service.generate_document(topic)
        
        if 'Word' in format_choice:
            filepath = DocumentGenerator.generate_docx(topic, content, output_dir=Config.TEMP_DIR)
        else:
            filepath = DocumentGenerator.generate_pdf(topic, content, output_dir=Config.TEMP_DIR)
        
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f,
                caption=f"✅ {topic}"
            )
        
        Services.user_manager.update_user_statistics(user_id, documents_generated=1)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    return ConversationHandler.END


async def image_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start image generation."""
    await update.message.reply_text(
        "🎨 Describe an image:\n"
        "(Example: 'A sunset over the ocean')"
    )
    return IMAGE_PROMPT


async def image_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get image prompt."""
    prompt = update.message.text
    context.user_data['image_prompt'] = prompt
    
    keyboard = [['Realistic', 'Abstract'], ['Artistic']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Prompt: *{prompt}*\n\nStyle?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return IMAGE_STYLE


async def image_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generate image."""
    user_id = update.effective_user.id
    style = update.message.text.lower().split()[0]
    prompt = context.user_data.get('image_prompt', 'artwork')
    
    style_map = {'realistic': 'realistic', 'abstract': 'abstract', 'artistic': 'artistic'}
    style = style_map.get(style, 'realistic')
    
    await update.message.reply_text("🔄 Generating...", reply_markup=ReplyKeyboardRemove())
    
    try:
        image_path = Services.image_service.generate_from_prompt(prompt, style, output_dir=Config.TEMP_DIR)
        
        Services.gallery_service.add_image(
            user_id, image_path, prompt,
            tags=['user', style], style=style
        )
        
        with open(image_path, 'rb') as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"✅ Style: *{style}*",
                parse_mode='Markdown'
            )
        
        Services.user_manager.update_user_statistics(user_id, images_generated=1)
        
        if os.path.exists(image_path):
            os.remove(image_path)
        
    except Exception as e:
        logger.error(f"Image error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    return ConversationHandler.END


async def gallery_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View user's gallery."""
    user_id = update.effective_user.id
    images = Services.gallery_service.get_gallery_summary(user_id, limit=5)
    
    if not images:
        await update.message.reply_text("📸 Gallery is empty. Use /image to create!")
        return
    
    message = f"📸 *Your Gallery ({len(images)} images)*\n\n"
    for img in images:
        message += f"• {img['style']}: {img['prompt'][:40]}...\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def stats_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View user statistics."""
    user_id = update.effective_user.id
    
    stats = Services.user_manager.get_user_statistics(user_id)
    images_count = Services.storage.get_user_images_count(user_id)
    storage_used = Services.storage.get_user_gallery_size(user_id)
    
    stats_text = (
        "📊 *Your Stats*\n\n"
        f"📄 Analyzed: {stats.get('documents_processed', 0)}\n"
        f"✏️ Generated: {stats.get('documents_generated', 0)}\n"
        f"🎨 Images: {stats.get('images_generated', 0)}\n\n"
        f"📸 Gallery: {images_count} images\n"
        f"💾 Storage: {format_file_size(storage_used)}"
    )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation."""
    await update.message.reply_text("❌ Cancelled", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Error handler."""
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ An error occurred. Please try again.")


async def main() -> None:
    """Start the bot."""
    try:
        Config.validate()
        Config.create_directories()
        
        # Initialize services
        Services.user_manager = UserManager(data_dir=Config.USERS_DIR)
        Services.storage = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
        Services.ai_service = AIGenerationService()
        Services.image_service = ImageGenerator()
        Services.gallery_service = ImageGalleryService(Services.storage)
        
        logger.info("✅ Services ready")
        
        # Create application
        application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("gallery", gallery_view))
        application.add_handler(CommandHandler("stats", stats_view))
        
        # Document generation
        doc_conv = ConversationHandler(
            entry_points=[CommandHandler("generate", generate_start)],
            states={
                GENERATE_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_topic)],
                GENERATE_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_format)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(doc_conv)
        
        # Image generation
        img_conv = ConversationHandler(
            entry_points=[CommandHandler("image", image_start)],
            states={
                IMAGE_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_prompt)],
                IMAGE_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_style)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(img_conv)
        
        # Document upload
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        
        # Image generation prompt
        application.add_handler(MessageHandler(
            filters.TEXT & (filters.Regex("🎨|Skip")),
            handle_generate_images
        ))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Bot running...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        raise


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    
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


async def gallery_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display user's gallery."""
    user_id = update.effective_user.id
    images = BotServices.gallery_service.get_gallery_summary(user_id, limit=5)
    
    if not images:
        await update.message.reply_text("📸 Your gallery is empty. Use /image to generate images.")
        return
    
    message = "📸 *Your Images*\n\n"
    for img in images:
        message += f"• {img['filename']} - {img['style']}\n"
    
    await update.message.reply_text(message)


async def gallery_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show gallery statistics."""
    user_id = update.effective_user.id
    
    try:
        images_count = BotServices.storage.get_user_images_count(user_id)
        storage_size = BotServices.storage.get_user_gallery_size(user_id)
        
        from src.utils.helpers import format_file_size
        
        stats_text = (
            f"📊 *Gallery Statistics*\n\n"
            f"Total Images: {images_count}\n"
            f"Storage Used: {format_file_size(storage_size)}\n"
            f"Last Updated: Just now"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error getting gallery stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel current operation."""
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again or contact support."
        )


async def main() -> None:
    """Start the bot."""
    try:
        Config.validate()
        Config.create_directories()
        
        # Initialize services
        BotServices.user_manager = UserManager(data_dir=Config.USERS_DIR)
        BotServices.storage = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
        BotServices.sessions = SessionStorage(data_dir=Config.SESSIONS_DIR)
        BotServices.ai_service = AIGenerationService()
        BotServices.image_service = ImageGenerator()
        BotServices.gallery_service = ImageGalleryService(BotServices.storage)
        
        logger.info("All services initialized")
        
        # Create application
        application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("gallery", gallery_view))
        application.add_handler(CommandHandler("gallery_stats", gallery_stats))
        
        # Document conversation
        document_conv = ConversationHandler(
            entry_points=[CommandHandler("generate", generate_start)],
            states={
                GENERATE_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_topic_received)],
                GENERATE_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_format_received)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(document_conv)
        
        # Image conversation
        image_conv = ConversationHandler(
            entry_points=[CommandHandler("image", image_start)],
            states={
                IMAGE_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_prompt_received)],
                IMAGE_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_style_received)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(image_conv)
        
        # Document upload handler
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start polling
        logger.info("Bot started polling...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
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
