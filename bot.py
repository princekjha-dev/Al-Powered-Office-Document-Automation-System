import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from document_reader import DocumentReader
from claude_handler import ClaudeHandler

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Claude handler
claude = ClaudeHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    """
    await update.message.reply_text(
        "Welcome to the Office Document Analyzer Bot!\n\n"
        "Send me a PDF, Word (.docx), or Excel (.xlsx) file and I'll analyze it using AI.\n"
        "Use /help for more information."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command.
    """
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n\n"
        "Send a document file (PDF, DOCX, XLSX) to get:\n"
        "• Summary\n"
        "• 5 Key Points\n"
        "• 1 Smart Insight\n"
        "• Action Items\n\n"
        "File size limit: 20MB"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle document messages.
    """
    document = update.message.document
    if not document:
        await update.message.reply_text("Please send a document file.")
        return

    file_name = document.file_name
    file_id = document.file_id

    # Check if supported file type
    if not DocumentReader.is_supported_file(file_name):
        await update.message.reply_text("Unsupported file type. Please send PDF, DOCX, or XLSX files.")
        return

    # Download file
    file = await context.bot.get_file(file_id)
    file_path = f"/tmp/{file_name}"
    await file.download_to_drive(file_path)

    try:
        # Check file size
        if not DocumentReader.check_file_size(file_path):
            await update.message.reply_text("File is too large. Maximum size is 20MB.")
            return

        # Extract text
        await update.message.reply_text("Processing your document...")
        text = DocumentReader.extract_text(file_path)

        if not text.strip():
            await update.message.reply_text("Could not extract text from the document.")
            return

        # Analyze with Claude
        analysis = claude.analyze_text(text)

        # Send response
        await update.message.reply_text(analysis)

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        await update.message.reply_text("An error occurred while processing your document. Please try again.")
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    """
    Main function to run the bot.
    """
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("TELEGRAM_TOKEN not found in environment variables.")
        return

    application = ApplicationBuilder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()