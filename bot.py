#!/usr/bin/env python3
"""
Simplified Al-Powered Office Document Automation System Bot - Hackathon Edition.

Core features:
- Document analysis (PDF, DOCX, XLSX)
- Al-powered insights and summarization
- Image generation from documents
- Image gallery management
- Advanced: Document chat (RAG), Comparison, Auto-categorization, Language detection, Quality scoring
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
from src.services.document_chat import DocumentChat
from src.services.document_comparison import DocumentComparison
from src.services.document_categorization import DocumentCategorization
from src.services.language_detection import LanguageDetection
from src.services.document_quality import DocumentQuality

# Setup logging
setup_logging(log_level=Config.LOG_LEVEL)
logger = get_logger(__name__)

# Conversation states
GENERATE_TOPIC, GENERATE_FORMAT = range(2)
IMAGE_PROMPT, IMAGE_STYLE = range(2, 4)
CHAT_SESSION, CHAT_QUESTION = range(4, 6)
COMPARE_DOC1, COMPARE_DOC2 = range(6, 8)

# Services container
class Services:
    user_manager: Optional[UserManager] = None
    storage: Optional[UserGalleryStorage] = None
    ai_service: Optional[AIGenerationService] = None
    image_service: Optional[ImageGenerator] = None
    gallery_service: Optional[ImageGalleryService] = None
    doc_chat: Optional[DocumentChat] = None
    doc_comparison: Optional[DocumentComparison] = None
    doc_category: Optional[DocumentCategorization] = None
    language_detection: Optional[LanguageDetection] = None
    doc_quality: Optional[DocumentQuality] = None


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
        "/generate - Create a document\n"
        "/compare - Compare two documents\n"
        "/category - Categorize document\n"
        "/quality - Check document quality\n\n"
        "*Chat & Q&A:*\n"
        "/ask - Ask questions about documents\n\n"
        "*Images:*\n"
        "/image - Generate an image\n"
        "/gallery - View images\n\n"
        "*Other:*\n"
        "/stats - Your statistics\n"
        "/language - Detect & translate\n"
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
            # Extract text
            text = DocumentReader.extract_text(file_path)
            if not text.strip():
                await update.message.reply_text("❌ Could not extract text from file")
                return
            
            # Detect language
            lang_info = Services.language_detection.get_language_info(text)
            await update.message.reply_text(lang_info, parse_mode='Markdown')
            
            # Categorize document
            category_report = Services.doc_category.get_categorization_report(text, Services.ai_service)
            await update.message.reply_text(category_report, parse_mode='Markdown')
            
            # Check quality
            quality_report = Services.doc_quality.get_quality_report(text)
            await update.message.reply_text(quality_report, parse_mode='Markdown')
            
            # AI analysis
            analysis = Services.ai_service.analyze_document(text)
            await update.message.reply_text(f"✅ *Analysis:*\n\n{analysis}", parse_mode='Markdown')
            
            # Store document for chat
            session_id = Services.doc_chat.create_session(text, user_id)
            context.user_data['current_doc_session'] = session_id
            context.user_data['last_doc_text'] = text
            
            # Ask about next action
            keyboard = [['🎨 Images', '💬 Ask', '🔍 Compare'], ['❌ Done']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                "What would you like to do?",
                reply_markup=reply_markup
            )
            
            Services.user_manager.update_user_statistics(user_id, documents_processed=1)
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"Document error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_response_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user choice after document analysis."""
    choice = update.message.text
    reply_markup = ReplyKeyboardRemove()
    
    if choice == '🎨 Images':
        await update.message.reply_text("🔄 Generating images...", reply_markup=reply_markup)
        await handle_generate_images_v2(update, context)
    elif choice == '💬 Ask':
        await update.message.reply_text(
            "💬 Ask a question about the document:",
            reply_markup=reply_markup
        )
        context.user_data['in_chat_mode'] = True
    elif choice == '🔍 Compare':
        await update.message.reply_text(
            "📄 Send the document to compare with:",
            reply_markup=reply_markup
        )
        context.user_data['comparing'] = True
    else:
        await update.message.reply_text("✅ Done!", reply_markup=reply_markup)


async def handle_document_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document chat questions."""
    if context.user_data.get('in_chat_mode'):
        question = update.message.text
        session_id = context.user_data.get('current_doc_session')
        
        if not session_id:
            await update.message.reply_text("❌ No active document session. Please send a document first.")
            context.user_data['in_chat_mode'] = False
            return
        
        await update.message.reply_text("💭 Thinking...")
        
        try:
            answer = Services.doc_chat.answer_question(session_id, question, Services.ai_service)
            await update.message.reply_text(f"🤖 *Answer:*\n\n{answer}", parse_mode='Markdown')
            
            await update.message.reply_text(
                "Ask another question? (or /cancel)",
                reply_markup=ReplyKeyboardMarkup([['❌ Done']], one_time_keyboard=True)
            )
        except Exception as e:
            logger.error(f"Chat error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    elif context.user_data.get('comparing'):
        # Store second document for comparison
        context.user_data['doc2_text'] = update.message.text
        doc1_text = context.user_data.get('last_doc_text', '')
        doc2_text = context.user_data.get('doc2_text', '')
        
        if doc1_text and doc2_text:
            await update.message.reply_text("🔍 Comparing documents...")
            
            try:
                report = Services.doc_comparison.generate_comparison_report(
                    doc1_text, doc2_text, Services.ai_service
                )
                
                summary = report.get('summary', '')
                changes = report.get('key_changes', '')
                
                await update.message.reply_text(summary, parse_mode='Markdown')
                await update.message.reply_text(changes, parse_mode='Markdown')
                
                if 'semantic_analysis' in report:
                    await update.message.reply_text(
                        f"🧠 *Semantic Analysis:*\n\n{report['semantic_analysis']}",
                        parse_mode='Markdown'
                    )
                
                context.user_data['comparing'] = False
            except Exception as e:
                logger.error(f"Comparison error: {e}")
                await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_generate_images_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate images from document (new version)."""
    user_id = update.effective_user.id
    text = context.user_data.get('last_doc_text', '')
    
    if not text:
        await update.message.reply_text("No document in memory")
        return

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
        Services.doc_chat = DocumentChat(data_dir=os.path.join(Config.DATA_DIR, 'chat_sessions'))
        Services.doc_comparison = DocumentComparison()
        Services.doc_category = DocumentCategorization()
        Services.language_detection = LanguageDetection()
        Services.doc_quality = DocumentQuality()
        
        logger.info("✅ All services initialized")
        
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
        
        # Document chat/Q&A handler
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_document_questions
        ))
        
        # Response action buttons
        application.add_handler(MessageHandler(
            filters.TEXT & (filters.Regex(r"🎨|💬|🔍|Done")),
            handle_response_action
        ))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Bot running with advanced features...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        raise


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
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
