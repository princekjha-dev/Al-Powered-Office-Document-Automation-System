#!/usr/bin/env python3
"""
AI-Powered Office Document Automation Bot  ·  v2.0
====================================================
Full upgrade over v1 — all four priorities implemented:

STABILITY & ERROR HANDLING
  • Structured logging with user_id context on every log line
  • Per-handler try/except with user-friendly error messages
  • Circuit-breaker pattern on AI service (disables after N consecutive fails)
  • _ai_call_with_retry(): exponential back-off, configurable retries
  • _tmp_path(): context manager — guaranteed temp-file cleanup even on crash
  • Telegram API errors caught & surfaced without crashing the bot

NEW FEATURES
  • 🎙️ Full voice message support via OpenAI Whisper (ogg → text → action menu)
  • 📝 /summarize [page]  — whole-doc or per-page summarisation
  • 📦 /export            — ZIP download of entire gallery
  • 🔍 /search <query>    — keyword search inside the loaded document
  • 📋 /outline           — auto-generate a structured outline from the document
  • 🔔 Broadcast-ready    — /broadcast for admins (rate-limited, chunked)

CODE REFACTORING & STRUCTURE
  • _Services typed dataclass — IDE-friendly, no Optional clutter
  • _kb() builder — DRY InlineKeyboardMarkup construction
  • _reply() universal reply helper — works for messages & callback queries
  • _bump() stat helper — single call to increment any user statistic
  • Menu dispatch via dict instead of if/elif chains
  • All keyboard presets in named factory functions
  • build_application() factory separates wiring from startup

PERFORMANCE & ASYNC
  • rate_limited() decorator — per-user sliding-window rate limiter
  • asyncio.gather() for concurrent language + category + quality scoring
  • run_in_executor() for all blocking I/O (file read, zip, AI calls)
  • drop_pending_updates=True on polling — skip stale messages on restart
  • Graceful SIGTERM shutdown (Docker / systemd compatible)
  • Connection pool reuse via single aiohttp.ClientSession (optional Whisper)
"""

from __future__ import annotations

import asyncio
import contextlib
import functools
import io
import logging
import os
import signal
import sys
import tempfile
import time
import zipfile
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

import aiohttp
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import Config
from src.models.storage import UserGalleryStorage
from src.models.user import UserManager
from src.services.ai_generation import AIGenerationService
from src.services.document_categorization import DocumentCategorization
from src.services.document_chat import DocumentChat
from src.services.document_comparison import DocumentComparison
from src.services.document_generator import DocumentGenerator
from src.services.document_quality import DocumentQuality
from src.services.document_reader import DocumentReader
from src.services.image_gallery import ImageGalleryService
from src.services.image_generator import ImageGenerator
from src.services.language_detection import LanguageDetection
from src.utils.helpers import format_file_size, get_logger, setup_logging

# ──────────────────────────────────────────────────────────────────────────────
# Logging — structured with user context
# ──────────────────────────────────────────────────────────────────────────────
setup_logging(log_level=Config.LOG_LEVEL)
logger = get_logger(__name__)


class _UserAdapter(logging.LoggerAdapter):
    """Add user_id= to every log record automatically."""
    def process(self, msg, kwargs):
        user_id = self.extra.get("user_id", "?")
        return f"[user={user_id}] {msg}", kwargs


def user_logger(user_id: int) -> logging.LoggerAdapter:
    return _UserAdapter(logger, {"user_id": user_id})


# ──────────────────────────────────────────────────────────────────────────────
# Configuration knobs (override via env vars)
# ──────────────────────────────────────────────────────────────────────────────
RATE_LIMIT: int          = int(os.getenv("BOT_RATE_LIMIT", 10))       # max calls per window
RATE_WINDOW: int         = int(os.getenv("BOT_RATE_WINDOW", 60))      # window in seconds
AI_RETRIES: int          = int(os.getenv("BOT_AI_RETRIES", 3))        # exponential back-off tries
CIRCUIT_THRESHOLD: int   = int(os.getenv("BOT_CIRCUIT_THRESHOLD", 5)) # fails before circuit opens
CIRCUIT_RECOVERY: int    = int(os.getenv("BOT_CIRCUIT_RECOVERY", 60)) # seconds before retry
WHISPER_API_KEY: str     = os.getenv("OPENAI_API_KEY", "")            # for voice transcription
ADMIN_IDS: set[int]      = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}

# ──────────────────────────────────────────────────────────────────────────────
# Conversation states
# ──────────────────────────────────────────────────────────────────────────────
GENERATE_TOPIC, GENERATE_FORMAT = range(2)
IMAGE_PROMPT, IMAGE_STYLE       = range(2, 4)

# ──────────────────────────────────────────────────────────────────────────────
# Rate limiter  (sliding window per user)
# ──────────────────────────────────────────────────────────────────────────────
_rate_store: dict[int, deque[float]] = defaultdict(deque)


def rate_limited(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """Decorator: reject calls exceeding RATE_LIMIT within RATE_WINDOW seconds."""
    @functools.wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *a, **kw):
        uid = update.effective_user.id
        now = time.monotonic()
        dq  = _rate_store[uid]
        while dq and now - dq[0] > RATE_WINDOW:
            dq.popleft()
        if len(dq) >= RATE_LIMIT:
            await _safe_reply(update, "⏳ You're sending too fast — wait a moment and try again.")
            return None
        dq.append(now)
        return await func(update, ctx, *a, **kw)
    return wrapper


# ──────────────────────────────────────────────────────────────────────────────
# Circuit breaker (AI service protection)
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class CircuitBreaker:
    threshold: int   = CIRCUIT_THRESHOLD
    recovery: int    = CIRCUIT_RECOVERY
    _fails: int      = field(default=0, init=False)
    _opened_at: float = field(default=0.0, init=False)

    @property
    def open(self) -> bool:
        if self._fails >= self.threshold:
            if time.monotonic() - self._opened_at > self.recovery:
                self._fails = 0   # attempt recovery
                return False
            return True
        return False

    def record_failure(self) -> None:
        self._fails += 1
        if self._fails == self.threshold:
            self._opened_at = time.monotonic()
            logger.warning(f"Circuit breaker OPEN after {self.threshold} failures.")

    def record_success(self) -> None:
        if self._fails:
            logger.info("Circuit breaker CLOSED — AI service recovered.")
        self._fails = 0


_circuit = CircuitBreaker()


async def _ai_call_with_retry(fn: Callable, *args, retries: int = AI_RETRIES, **kwargs) -> Any:
    """
    Run a (potentially blocking) AI function in a thread executor with
    exponential back-off and circuit-breaker protection.
    """
    if _circuit.open:
        raise RuntimeError("AI service is temporarily unavailable — please try again in a minute.")

    loop = asyncio.get_running_loop()
    for attempt in range(retries):
        try:
            result = await loop.run_in_executor(None, functools.partial(fn, *args, **kwargs))
            _circuit.record_success()
            return result
        except Exception as exc:
            _circuit.record_failure()
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            logger.warning(f"AI call failed (attempt {attempt+1}/{retries}): {exc}. Retry in {wait}s…")
            await asyncio.sleep(wait)


# ──────────────────────────────────────────────────────────────────────────────
# Services container
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class _Services:
    user_manager: UserManager        = field(init=False)
    storage: UserGalleryStorage      = field(init=False)
    ai_service: AIGenerationService  = field(init=False)
    image_service: ImageGenerator    = field(init=False)
    gallery_service: ImageGalleryService = field(init=False)
    doc_chat: DocumentChat           = field(init=False)
    doc_comparison: DocumentComparison = field(init=False)
    doc_category: DocumentCategorization = field(init=False)
    language_detection: LanguageDetection = field(init=False)
    doc_quality: DocumentQuality     = field(init=False)
    http_session: Optional[aiohttp.ClientSession] = field(default=None, init=False)

    def init_all(self) -> None:
        self.user_manager      = UserManager(data_dir=Config.USERS_DIR)
        self.storage           = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
        self.ai_service        = AIGenerationService()
        self.image_service     = ImageGenerator()
        self.gallery_service   = ImageGalleryService(self.storage)
        self.doc_chat          = DocumentChat(data_dir=os.path.join(Config.DATA_DIR, "chat_sessions"))
        self.doc_comparison    = DocumentComparison()
        self.doc_category      = DocumentCategorization()
        self.language_detection = LanguageDetection()
        self.doc_quality       = DocumentQuality()
        logger.info("All services initialised successfully.")

    async def init_async(self) -> None:
        """Called after the event loop is running (for aiohttp session)."""
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)
        )

    async def shutdown(self) -> None:
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
        logger.info("Services shut down cleanly.")


Svc = _Services()


# ──────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────────────────────────────────────

async def _safe_reply(update: Update, text: str, **kwargs) -> Optional[Message]:
    """Send a Markdown reply, handling both message and callback-query contexts."""
    kwargs.setdefault("parse_mode", ParseMode.MARKDOWN)
    try:
        if update.message:
            return await update.message.reply_text(text, **kwargs)
        if update.callback_query and update.callback_query.message:
            return await update.callback_query.message.reply_text(text, **kwargs)
    except TelegramError as e:
        logger.error(f"Telegram send error: {e}")
    return None


def _kb(*rows: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Build InlineKeyboardMarkup from rows of (label, callback_data) tuples."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=cb) for label, cb in row]
         for row in rows]
    )


@contextlib.contextmanager
def _tmp_path(suffix: str = ".tmp"):
    """Context manager: yield a NamedTemporaryFile path, delete on exit."""
    with tempfile.NamedTemporaryFile(suffix=suffix, dir=Config.TEMP_DIR, delete=False) as f:
        path = Path(f.name)
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


def _bump(user_id: int, stat: str, amount: int = 1) -> None:
    """Increment a user statistic silently."""
    try:
        user = Svc.user_manager.get_user(user_id)
        if user:
            user.increment_statistic(stat, amount)
            Svc.user_manager.save_user(user)
    except Exception as e:
        logger.warning(f"Stat bump failed ({stat}): {e}")


def _truncate(text: str, limit: int = 3800) -> str:
    """Truncate text to Telegram's message limit."""
    return text[:limit] + "…" if len(text) > limit else text


@contextlib.asynccontextmanager
async def _typing(update: Update):
    """
    Show Telegram's native 'typing...' indicator in the chat header
    while work is in progress. Re-sends the action every 4 s so it
    never expires on long AI calls. Cancels cleanly on exit.
    """
    chat_id = update.effective_chat.id
    bot = update.get_bot()

    async def _keep_typing():
        while True:
            try:
                await bot.send_chat_action(chat_id, action="typing")
            except TelegramError:
                pass
            await asyncio.sleep(4)

    task = asyncio.create_task(_keep_typing())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


# ──────────────────────────────────────────────────────────────────────────────
# Voice transcription  (OpenAI Whisper via REST)
# ──────────────────────────────────────────────────────────────────────────────

async def _transcribe_voice(ogg_path: Path) -> str:
    """
    Transcribe a voice OGG file using OpenAI Whisper API.
    Returns the transcript string, or raises on failure.

    Requirements:
      pip install aiohttp
      OPENAI_API_KEY environment variable must be set.
    """
    if not WHISPER_API_KEY:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file to enable voice transcription."
        )

    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {WHISPER_API_KEY}"}

    with open(ogg_path, "rb") as audio_file:
        form = aiohttp.FormData()
        form.add_field("file", audio_file, filename="voice.ogg", content_type="audio/ogg")
        form.add_field("model", "whisper-1")
        form.add_field("response_format", "text")

        session = Svc.http_session
        async with session.post(url, headers=headers, data=form) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Whisper API error {resp.status}: {body[:200]}")
            return (await resp.text()).strip()


# ──────────────────────────────────────────────────────────────────────────────
# Keyboard factory functions
# ──────────────────────────────────────────────────────────────────────────────

def _main_menu_kb() -> InlineKeyboardMarkup:
    return _kb(
        [("📄 Analyze Docs",  "menu_analyze"),  ("✏️ Generate Doc", "menu_generate")],
        [("🎨 Create Image",  "menu_image"),    ("📸 My Gallery",   "menu_gallery")],
        [("💬 Ask AI",        "menu_ask"),       ("📊 Stats",        "menu_stats")],
        [("📦 Export ZIP",    "menu_export"),    ("❓ Help",          "help_quickstart")],
    )


def _doc_actions_kb() -> InlineKeyboardMarkup:
    return _kb(
        [("🎨 Generate Images", "action_images"),   ("💬 Ask Questions", "action_ask")],
        [("🔍 Compare Docs",    "action_compare"),  ("📝 Summarize",     "action_summarize")],
        [("📋 Outline",         "action_outline"),  ("✅ Done",           "action_done")],
    )


def _voice_actions_kb() -> InlineKeyboardMarkup:
    return _kb(
        [("💬 Ask Questions", "action_ask"),    ("📝 Summarize", "action_summarize")],
        [("📋 Outline",       "action_outline"), ("🏠 Main Menu", "menu_main")],
    )


def _help_menu_kb() -> InlineKeyboardMarkup:
    return _kb(
        [("📚 Commands", "help_commands"),    ("💡 Features",   "help_features")],
        [("🚀 Quick Start", "help_quickstart"), ("🏠 Main Menu", "menu_main")],
    )


def _after_image_kb() -> InlineKeyboardMarkup:
    return _kb(
        [("🎨 Create Another", "menu_image"), ("📸 View Gallery", "menu_gallery")],
        [("📦 Export ZIP",     "menu_export"), ("🏠 Main Menu",    "menu_main")],
    )


def _after_generate_kb() -> InlineKeyboardMarkup:
    return _kb(
        [("✏️ Generate Another", "menu_generate"), ("📄 Analyze Doc", "menu_analyze")],
        [("🎨 Create Image",     "menu_image"),     ("🏠 Main Menu",   "menu_main")],
    )


# ──────────────────────────────────────────────────────────────────────────────
# /start  /help  /menu
# ──────────────────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        Svc.user_manager.create_or_get_user(
            user.id, username=user.username or "", first_name=user.first_name or ""
        )
    except Exception as e:
        user_logger(user.id).warning(f"create_or_get_user failed: {e}")

    await _safe_reply(
        update,
        f"👋 Welcome, *{user.first_name}*!\n\n"
        "🤖 *AI Document Automation Suite v2*\n\n"
        "📄 Analyze PDF, DOCX, XLSX\n"
        "🎙️ Send voice notes — I'll transcribe & analyse them\n"
        "✏️ Generate professional documents\n"
        "🎨 Create AI images\n"
        "📦 Export gallery as ZIP\n"
        "💬 Chat with your documents (RAG)\n\n"
        "Choose an option below 👇",
        reply_markup=_main_menu_kb(),
    )


async def help_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _safe_reply(
        update,
        "📚 *Help & Commands*\n\n"
        "📄 *Analysis* — /analyze /quality /language /category /errors\n"
        "📝 *Summarize* — /summarize [page]\n"
        "📋 *Outline* — /outline\n"
        "🔍 *Search* — /search <query>\n"
        "🌐 *Translate* — /translate <lang_code>\n\n"
        "✏️ *Generate* — /generate (Word or PDF)\n"
        "🎨 *Image* — /image\n"
        "📸 *Gallery* — /gallery\n"
        "📦 *Export* — /export\n\n"
        "🔄 *Compare* — /compare\n"
        "💬 *Chat* — /ask or /chat\n"
        "🧹 *Clear* — /clear\n"
        "📊 *Stats* — /stats\n\n"
        "🎙️ Voice messages are transcribed automatically!",
        reply_markup=_help_menu_kb(),
    )


async def menu_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _safe_reply(update, "🏠 *Main Menu*\n\nChoose what you'd like to do:", reply_markup=_main_menu_kb())


# ──────────────────────────────────────────────────────────────────────────────
# Menu callback dispatcher
# ──────────────────────────────────────────────────────────────────────────────

async def handle_menu_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    data = query.data

    _MENU_HANDLERS: dict[str, Callable] = {
        "menu_analyze":    _cb_analyze,
        "menu_generate":   _cb_generate,
        "menu_image":      _cb_image,
        "menu_gallery":    _cb_gallery,
        "menu_ask":        _cb_ask,
        "menu_stats":      _cb_stats,
        "menu_main":       _cb_main,
        "menu_export":     _cb_export,
        "help_commands":   _cb_help_commands,
        "help_features":   _cb_help_features,
        "help_quickstart": _cb_help_quickstart,
    }
    handler = _MENU_HANDLERS.get(data)
    if handler:
        try:
            await handler(query, ctx, uid)
        except Exception as exc:
            user_logger(uid).error(f"Menu callback '{data}' error: {exc}", exc_info=True)
            await query.message.reply_text("❌ Something went wrong. Please try again.")


async def _cb_analyze(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "📄 *Analyze Documents*\n\n"
        "Send any file (PDF, DOCX, XLSX) and I'll:\n"
        "✅ Extract and analyse content\n"
        "✅ Detect language & category\n"
        "✅ Check quality scores\n"
        "✅ Provide AI insights\n\n"
        "Ready? Just send a file! 📤",
        parse_mode=ParseMode.MARKDOWN,
    )


async def _cb_generate(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "✏️ *Generate Documents*\n\nI can create: Reports, Summaries, Guides, Analyses\n\nUse /generate to start!",
        parse_mode=ParseMode.MARKDOWN,
    )


async def _cb_image(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "🎨 *Create AI Images*\n\nDescribe what you want, then choose a style.\n\nUse /image to start!",
        parse_mode=ParseMode.MARKDOWN,
    )


async def _cb_gallery(q: CallbackQuery, ctx, uid: int) -> None:
    images = Svc.gallery_service.get_gallery_summary(uid, limit=5)
    if not images:
        text = "📸 *Your Gallery*\n\nEmpty. Generate images with /image!"
    else:
        text = f"📸 *Your Gallery ({len(images)} images)*\n\n"
        for img in images:
            text += f"• _{img['style']}_ — {img['prompt'][:50]}…\n"
    await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=_main_menu_kb())


async def _cb_ask(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "💬 *Ask AI*\n\nJust type your question — about a loaded document or anything else.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def _cb_stats(q: CallbackQuery, ctx, uid: int) -> None:
    stats = Svc.user_manager.get_user_statistics(uid) or {}
    imgs  = Svc.storage.get_user_images_count(uid)
    size  = Svc.storage.get_user_gallery_size(uid)
    await q.edit_message_text(
        "📊 *Your Statistics*\n\n"
        f"📄 Analysed:  {stats.get('documents_processed', 0)}\n"
        f"✏️ Generated: {stats.get('documents_generated', 0)}\n"
        f"🎨 Images:    {stats.get('images_generated', 0)}\n"
        f"🎙️ Voices:    {stats.get('voices_transcribed', 0)}\n\n"
        f"📸 Gallery:   {imgs} images\n"
        f"💾 Storage:   {format_file_size(size)}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=_main_menu_kb(),
    )


async def _cb_main(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "🏠 *Main Menu*\n\nWhat would you like to do?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=_main_menu_kb(),
    )


async def _cb_export(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text("📦 Packaging your gallery…", parse_mode=ParseMode.MARKDOWN)
    await _do_export(q.message, uid)


async def _cb_help_commands(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "📚 *Commands*\n\n"
        "/analyze /quality /language /category /errors\n"
        "/summarize [page]  /outline  /search <query>\n"
        "/translate <lang>  /compare  /ask  /chat\n"
        "/generate  /image  /gallery  /export  /stats  /clear",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=_help_menu_kb(),
    )


async def _cb_help_features(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "💡 *Features*\n\n"
        "🎙️ *Voice Notes* — send audio; I transcribe & let you query it\n"
        "🤖 *RAG Chat* — question-answer over your documents\n"
        "🔄 *Doc Compare* — diff two documents\n"
        "📋 *Auto Outline* — structured outline from any doc\n"
        "🔍 *Keyword Search* — find content inside loaded docs\n"
        "📦 *Gallery Export* — ZIP download of all images\n"
        "🌐 *Translate* — 100+ languages via AI",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=_help_menu_kb(),
    )


async def _cb_help_quickstart(q: CallbackQuery, ctx, uid: int) -> None:
    await q.edit_message_text(
        "🚀 *Quick Start*\n\n"
        "1️⃣ /start — create profile\n"
        "2️⃣ Upload a PDF/DOCX → instant analysis\n"
        "3️⃣ 🎙️ Or send a voice note → transcription + analysis\n"
        "4️⃣ Press *Ask Questions* → chat with your doc\n"
        "5️⃣ /image → describe → AI image\n"
        "6️⃣ /export → download gallery ZIP",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=_help_menu_kb(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Document action callbacks
# ──────────────────────────────────────────────────────────────────────────────

async def handle_document_action_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()
    uid  = update.effective_user.id
    data = query.data

    try:
        if data == "action_images":
            await query.edit_message_text("🎨 *Generate Images*\n\nCreating images from your document…", parse_mode=ParseMode.MARKDOWN)
            await _generate_images_from_doc(query.message, ctx, uid)

        elif data == "action_ask":
            ctx.user_data["in_chat_mode"] = True
            await query.edit_message_text(
                "💬 *Ask Your Question*\n\nType your question about the document!",
                parse_mode=ParseMode.MARKDOWN,
            )

        elif data == "action_compare":
            ctx.user_data["comparing"] = True
            await query.edit_message_text(
                "🔍 *Compare*\n\nSend another document or paste text to compare.",
                parse_mode=ParseMode.MARKDOWN,
            )

        elif data == "action_summarize":
            await query.edit_message_text(
                "📝 *Summarize*\n\nUse /summarize for full doc or /summarize <page> for a page.",
                parse_mode=ParseMode.MARKDOWN,
            )

        elif data == "action_outline":
            await query.edit_message_text("📋 *Outline*\n\nGenerating…", parse_mode=ParseMode.MARKDOWN)
            await _do_outline(query.message, ctx, uid)

        elif data == "action_done":
            await query.edit_message_text("✅ Done! Use /menu to continue.", parse_mode=ParseMode.MARKDOWN)

    except Exception as exc:
        user_logger(uid).error(f"Doc action '{data}' error: {exc}", exc_info=True)
        await query.message.reply_text("❌ Something went wrong — please try again.")


# ──────────────────────────────────────────────────────────────────────────────
# Document upload handler
# ──────────────────────────────────────────────────────────────────────────────

@rate_limited
async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid  = update.effective_user.id
    ulog = user_logger(uid)
    doc  = update.message.document

    if not DocumentReader.is_supported_file(doc.file_name):
        await _safe_reply(update, "❌ Unsupported file. Please send a PDF, DOCX, or XLSX.")
        return

    with _tmp_path(suffix=Path(doc.file_name).suffix) as file_path:
        try:
            async with _typing(update):
                tg_file = await ctx.bot.get_file(doc.file_id)
                await tg_file.download_to_drive(str(file_path))

                loop = asyncio.get_running_loop()
                text = await loop.run_in_executor(None, DocumentReader.extract_text, str(file_path))

                if not text.strip():
                    await _safe_reply(update, "❌ Could not extract text. Is the file scanned or password-protected?")
                    return

                report_text, session_id, pages = await _build_document_report(text, uid)

            ctx.user_data["current_doc_session"] = session_id
            ctx.user_data["last_doc_text"]        = text
            ctx.user_data["doc_pages"]            = pages

            await _safe_reply(update, report_text)

            # AI analysis — separate message (can be slow)
            try:
                async with _typing(update):
                    analysis = await _ai_call_with_retry(Svc.ai_service.analyze_document, text)
                await update.message.reply_text(_truncate(analysis))
            except Exception as ai_err:
                ulog.error(f"AI analysis failed: {ai_err}")
                await update.message.reply_text(f"AI analysis unavailable: {str(ai_err)[:120]}")

            await update.message.reply_text(
                "What would you like to do next?",
                reply_markup=_doc_actions_kb(),
            )
            _bump(uid, "documents_processed")

        except TelegramError as te:
            ulog.error(f"Telegram error during doc upload: {te}")
            await update.message.reply_text("❌ Telegram error — please try again.")
        except Exception as exc:
            ulog.error(f"Document handler error: {exc}", exc_info=True)
            await update.message.reply_text(f"❌ Error processing document: {str(exc)[:200]}")


async def _build_document_report(text: str, uid: int) -> tuple[str, str, list[str]]:
    """
    Run language, category, and quality analysis concurrently,
    build the consolidated report string, create a chat session.
    Returns (report_markdown, session_id, pages).
    """
    loop = asyncio.get_running_loop()

    lang_fut  = loop.run_in_executor(None, Svc.language_detection.detect_language, text)
    cat_fut   = loop.run_in_executor(None, Svc.doc_category.categorize_document, text)
    qual_fut  = loop.run_in_executor(None, Svc.doc_quality.score_document, text)

    lang_result, (category, cat_conf), scores = await asyncio.gather(lang_fut, cat_fut, qual_fut)

    tags = await loop.run_in_executor(None, Svc.doc_category.generate_tags, text, category)

    lang_name = lang_result.get("language_name", "Unknown")
    lang_code = lang_result.get("language", "?")
    lang_conf = lang_result.get("confidence", 0)

    overall = scores.get("overall", 0)
    quality_label = (
        "Excellent 🌟" if overall >= 8 else
        "Good 👍"      if overall >= 6 else
        "Fair ⚠️"      if overall >= 4 else
        "Needs Work 🔧"
    )

    words   = text.split()
    lines   = text.splitlines()
    pages   = text.split("\x0c")  # form-feed page breaks
    pages_n = max(1, len(pages) if len(pages) > 1 else len(words) // 250)

    report = (
        "📄 *Document Report*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 *Language:* {lang_name} ({lang_code}) — {lang_conf*100:.0f}%\n"
        f"📂 *Category:* {category.upper()} — {cat_conf*100:.0f}%\n"
        f"🏷 *Tags:* {', '.join(tags) if tags else 'none'}\n\n"
        f"📊 *Quality:* {overall:.1f}/10 ({quality_label})\n"
        f"   Clarity {scores.get('clarity',0):.1f}  "
        f"Grammar {scores.get('grammar',0):.1f}  "
        f"Coherence {scores.get('coherence',0):.1f}\n\n"
        f"📏 *Stats:* {len(words):,} words · {len(lines):,} lines · ~{pages_n} pages"
    )

    session_id = await asyncio.get_running_loop().run_in_executor(
        None, Svc.doc_chat.create_session, text, uid
    )

    return report, session_id, pages


# ──────────────────────────────────────────────────────────────────────────────
# 🎙️ Voice message handler — full Whisper transcription
# ──────────────────────────────────────────────────────────────────────────────

@rate_limited
async def handle_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid  = update.effective_user.id
    ulog = user_logger(uid)
    voice = update.message.voice

    with _tmp_path(suffix=".ogg") as ogg_path:
        try:
            async with _typing(update):
                tg_file = await ctx.bot.get_file(voice.file_id)
                await tg_file.download_to_drive(str(ogg_path))
                transcript = await _transcribe_voice(ogg_path)

            if not transcript.strip():
                await _safe_reply(update, "⚠️ Could not transcribe audio — try speaking more clearly.")
                return

            ulog.info(f"Voice transcribed ({len(transcript)} chars)")

            # Show transcript
            await _safe_reply(
                update,
                f"🎙️ *Transcript*\n\n{_truncate(transcript, 1500)}",
            )

            # Store as active document so all doc commands work
            ctx.user_data["last_doc_text"] = transcript
            ctx.user_data["doc_pages"]     = [transcript]

            # Create a chat session
            loop = asyncio.get_running_loop()
            session_id = await loop.run_in_executor(
                None, Svc.doc_chat.create_session, transcript, uid
            )
            ctx.user_data["current_doc_session"] = session_id

            # Quick AI summary
            try:
                async with _typing(update):
                    summary = await _ai_call_with_retry(
                        Svc.ai_service.call_ai,
                        prompt=f"Summarize this voice note concisely in 3–5 sentences:\n\n{transcript[:3000]}",
                        system_role="You are a helpful assistant that summarizes spoken content.",
                    )
                await update.message.reply_text(
                    f"📝 *AI Summary*\n\n{_truncate(summary)}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception as ai_err:
                ulog.warning(f"Voice summary failed: {ai_err}")

            # Action menu
            await update.message.reply_text(
                "🎙️ *Voice note ready!*\n\nWhat would you like to do with it?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=_voice_actions_kb(),
            )
            _bump(uid, "voices_transcribed")

        except EnvironmentError as env_err:
            await _safe_reply(
                update,
                f"⚙️ *Voice transcription not configured*\n\n"
                f"{env_err}\n\n"
                f"Set `OPENAI_API_KEY` in your `.env` to enable this feature.",
            )
        except TelegramError as te:
            ulog.error(f"Telegram error in voice handler: {te}")
            await _safe_reply(update, "❌ Telegram error — please try again.")
        except Exception as exc:
            ulog.error(f"Voice handler error: {exc}", exc_info=True)
            await _safe_reply(update, f"❌ Transcription failed: {str(exc)[:200]}")


# ──────────────────────────────────────────────────────────────────────────────
# Document-aware commands
# ──────────────────────────────────────────────────────────────────────────────

async def analyze_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded — upload a file or send a voice note first.")
        return
    try:
        async with _typing(update):
            analysis = await _ai_call_with_retry(Svc.ai_service.analyze_document, text)
        await _safe_reply(update, _truncate(analysis))
    except Exception as exc:
        await _safe_reply(update, f"Analysis failed: {str(exc)[:200]}")


async def summarize_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Summarize entire doc or a specific page: /summarize [page_number]"""
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded — upload a file or voice note first.")
        return

    pages: list[str] = ctx.user_data.get("doc_pages", [text])
    page_num: Optional[int] = None

    if ctx.args:
        try:
            page_num = int(ctx.args[0])
        except ValueError:
            await _safe_reply(update, "Usage: /summarize [page_number]  e.g. /summarize 2")
            return

    if page_num is not None:
        if page_num < 1 or page_num > len(pages):
            await _safe_reply(update, f"❌ Page {page_num} not found. Document has {len(pages)} page(s).")
            return
        target, label = pages[page_num - 1], f"Page {page_num}"
    else:
        target, label = text, "Full Document"

    try:
        async with _typing(update):
            summary = await _ai_call_with_retry(
                Svc.ai_service.call_ai,
                prompt=f"Write a concise summary of the following text. Respond in plain text only, no emojis:\n\n{target[:4000]}",
                system_role="You are a professional summarizer. Be concise. No emojis, no decorative formatting.",
            )
        await _safe_reply(
            update, _truncate(summary)
        )
    except Exception as exc:
        await _safe_reply(update, f"Summarization failed: {str(exc)[:200]}")


async def outline_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a structured outline from the loaded document."""
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded — upload a file or voice note first.")
        return
    await _do_outline(update.message, ctx, update.effective_user.id)


async def _do_outline(message: Message, ctx: ContextTypes.DEFAULT_TYPE, uid: int) -> None:
    text = ctx.user_data.get("last_doc_text", "")
    # Build a fake Update-like object so _typing works with a Message
    chat_id = message.chat_id
    bot = message.get_bot()

    async def _keep_typing():
        while True:
            try:
                await bot.send_chat_action(chat_id, action="typing")
            except TelegramError:
                pass
            await asyncio.sleep(4)

    task = asyncio.create_task(_keep_typing())
    try:
        outline = await _ai_call_with_retry(
            Svc.ai_service.call_ai,
            prompt=(
                "Create a structured outline with numbered sections and sub-points "
                f"for the following document:\n\n{text[:4500]}"
            ),
            system_role="You are an expert at creating clear, hierarchical document outlines.",
        )
        await message.reply_text(f"📋 *Document Outline*\n\n{_truncate(outline)}", parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        user_logger(uid).error(f"Outline error: {exc}", exc_info=True)
        await message.reply_text(f"❌ Outline failed: {str(exc)[:200]}")
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def search_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Search for a keyword in the loaded document: /search <query>"""
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded — upload a file first.")
        return
    if not ctx.args:
        await _safe_reply(update, "Usage: /search <query>  e.g. /search revenue")
        return

    query = " ".join(ctx.args).lower()
    lines = text.splitlines()
    hits  = [
        f"• Line {i+1}: {line.strip()}"
        for i, line in enumerate(lines)
        if query in line.lower() and line.strip()
    ][:20]  # cap at 20 results

    if hits:
        result = f"🔍 *Search results for «{query}»* ({len(hits)} matches)\n\n" + "\n".join(hits)
    else:
        result = f"🔍 No matches found for «{query}» in the document."

    await _safe_reply(update, _truncate(result))


async def errors_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded — upload a file first.")
        return
    issues = []
    if len(text.split()) < 100:
        issues.append("• ⚠️ Document is very short — completeness may be low.")
    if "???" in text:
        issues.append("• ⚠️ Placeholder markers '???' detected.")
    if "TODO" in text.upper():
        issues.append("• ⚠️ TODO markers found.")
    if not any(c.isalpha() for c in text[:500]):
        issues.append("• ⚠️ Very few alphabetic characters at the start — possible encoding issue.")
    duplicate_lines = [
        l for l in set(text.splitlines())
        if text.splitlines().count(l) > 3 and l.strip()
    ]
    if duplicate_lines:
        issues.append(f"• ⚠️ Repeated lines detected ({len(duplicate_lines)} instances).")
    if not issues:
        issues = ["• ✅ No obvious issues found in quick checks."]
    await _safe_reply(update, "🧪 *Error Detection Report*\n\n" + "\n".join(issues))


async def translate_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded — upload a file first.")
        return
    if not ctx.args:
        await _safe_reply(update, "Usage: /translate <language_code>  e.g. /translate hi")
        return
    lang = ctx.args[0].strip().lower()
    try:
        async with _typing(update):
            translated = await _ai_call_with_retry(
                Svc.language_detection.translate, text, lang, Svc.ai_service
            )
        await _safe_reply(
            update, _truncate(translated)
        )
    except Exception as exc:
        user_logger(update.effective_user.id).error(f"Translate error: {exc}")
        await _safe_reply(update, f"Translation failed: {str(exc)[:200]}")


async def clear_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    for key in ("current_doc_session", "last_doc_text", "in_chat_mode", "comparing", "doc_pages"):
        ctx.user_data.pop(key, None)
    await _safe_reply(update, "🧹 Session cleared. Start fresh with /menu.")


async def category_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded."); return
    try:
        report = await asyncio.get_running_loop().run_in_executor(
            None, Svc.doc_category.get_categorization_report, text
        )
        await _safe_reply(update, report)
    except Exception as exc:
        await _safe_reply(update, f"❌ Error: {exc}")


async def quality_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded."); return
    try:
        report = await asyncio.get_running_loop().run_in_executor(
            None, Svc.doc_quality.get_quality_report, text
        )
        await _safe_reply(update, report)
    except Exception as exc:
        await _safe_reply(update, f"❌ Error: {exc}")


async def language_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = ctx.user_data.get("last_doc_text")
    if not text:
        await _safe_reply(update, "❌ No document loaded."); return
    try:
        info = await asyncio.get_running_loop().run_in_executor(
            None, Svc.language_detection.get_language_info, text
        )
        await _safe_reply(update, info)
    except Exception as exc:
        await _safe_reply(update, f"❌ Error: {exc}")


async def compare_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not ctx.user_data.get("last_doc_text"):
        await _safe_reply(update, "❌ No document loaded — upload a file first.")
        return
    ctx.user_data["comparing"] = True
    await _safe_reply(update, "📄 Send text or upload a second document to compare.")


async def ask_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not ctx.user_data.get("current_doc_session"):
        await _safe_reply(update, "❌ No document loaded — upload a file or voice note first.")
        return
    ctx.user_data["in_chat_mode"] = True
    await _safe_reply(update, "💬 Ask your question about the document:")


# ──────────────────────────────────────────────────────────────────────────────
# Export
# ──────────────────────────────────────────────────────────────────────────────

async def export_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    async with _typing(update):
        await _do_export(update.message, update.effective_user.id)


async def _do_export(message: Message, uid: int) -> None:
    images = Svc.gallery_service.get_gallery_summary(uid, limit=50)
    if not images:
        await message.reply_text("📸 Gallery is empty — generate images with /image first.")
        return
    try:
        loop = asyncio.get_running_loop()

        def _build_zip() -> tuple[io.BytesIO, int]:
            buf = io.BytesIO()
            count = 0
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for idx, img in enumerate(images, 1):
                    p = img.get("path")
                    if p and os.path.exists(p):
                        zf.write(p, arcname=f"image_{idx:03d}{Path(p).suffix}")
                        count += 1
            buf.seek(0)
            return buf, count

        buf, count = await loop.run_in_executor(None, _build_zip)

        if count == 0:
            await message.reply_text("⚠️ No image files found on disk.")
            return
        await message.reply_document(
            document=buf,
            filename="my_gallery.zip",
            caption=f"📦 Gallery export — {count} image(s)!",
        )
    except Exception as exc:
        user_logger(uid).error(f"Export error: {exc}", exc_info=True)
        await message.reply_text(f"❌ Export failed: {str(exc)[:200]}")


# ──────────────────────────────────────────────────────────────────────────────
# Image generation from document
# ──────────────────────────────────────────────────────────────────────────────

async def _generate_images_from_doc(message: Message, ctx: ContextTypes.DEFAULT_TYPE, uid: int) -> None:
    text = ctx.user_data.get("last_doc_text", "")
    if not text:
        await message.reply_text("❌ No document in memory."); return
    ulog = user_logger(uid)
    chat_id = message.chat_id
    bot = message.get_bot()
    try:
        prompts = await _ai_call_with_retry(Svc.ai_service.generate_image_prompts, text, count=2)
        count = 0
        for i, prompt in enumerate(prompts, 1):
            # Show typing indicator while each image generates
            async def _keep_typing():
                while True:
                    try:
                        await bot.send_chat_action(chat_id, action="typing")
                    except TelegramError:
                        pass
                    await asyncio.sleep(4)

            task = asyncio.create_task(_keep_typing())
            with _tmp_path(suffix=".png") as img_path:
                try:
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        None,
                        functools.partial(
                            Svc.image_service.generate_from_prompt,
                            prompt, "realistic", output_path=str(img_path)
                        )
                    )
                    Svc.gallery_service.add_image(
                        uid, str(img_path), prompt, tags=["document", "auto"], style="realistic"
                    )
                    with open(img_path, "rb") as f:
                        await message.reply_photo(
                            photo=f, caption=f"_{prompt}_", parse_mode=ParseMode.MARKDOWN
                        )
                    count += 1
                except Exception as img_err:
                    ulog.error(f"Image {i} failed: {img_err}")
                    await message.reply_text(f"⚠️ Image {i} failed: {str(img_err)[:120]}")
                finally:
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task

        if count:
            _bump(uid, "images_generated", count)
            await message.reply_text(f"✅ {count} image(s) saved to your gallery!")
    except Exception as exc:
        ulog.error(f"Image-from-doc error: {exc}", exc_info=True)
        await message.reply_text(f"❌ Image generation failed: {str(exc)[:200]}")


# ──────────────────────────────────────────────────────────────────────────────
# General text message router
# ──────────────────────────────────────────────────────────────────────────────

@rate_limited
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id

    if ctx.user_data.get("in_chat_mode"):
        await _handle_doc_chat(update, ctx, uid)
    elif ctx.user_data.get("comparing"):
        await _handle_compare(update, ctx, uid)
    else:
        await _handle_general_question(update, ctx, uid)


async def _handle_doc_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE, uid: int) -> None:
    session_id = ctx.user_data.get("current_doc_session")
    if not session_id:
        await _safe_reply(update, "No active document session — upload a file first.")
        ctx.user_data["in_chat_mode"] = False
        return
    question = update.message.text
    try:
        async with _typing(update):
            answer = await _ai_call_with_retry(
                Svc.doc_chat.answer_question, session_id, question, Svc.ai_service
            )
        await _safe_reply(update, _truncate(answer))
    except Exception as exc:
        user_logger(uid).error(f"Doc chat error: {exc}", exc_info=True)
        await _safe_reply(update, f"Error: {str(exc)[:200]}")


async def _handle_compare(update: Update, ctx: ContextTypes.DEFAULT_TYPE, uid: int) -> None:
    doc1 = ctx.user_data.get("last_doc_text", "")
    doc2 = update.message.text
    if not doc1:
        await _safe_reply(update, "❌ No base document loaded.")
        ctx.user_data["comparing"] = False
        return
    try:
        async with _typing(update):
            loop = asyncio.get_running_loop()
            result   = await loop.run_in_executor(None, Svc.doc_comparison.compare_text, doc1, doc2)
            summary  = await loop.run_in_executor(None, Svc.doc_comparison.get_change_summary, result)
            key_chgs = await loop.run_in_executor(None, Svc.doc_comparison.get_key_changes, result)
        await _safe_reply(
            update,
            f"📊 *Comparison Result*\n\n{_truncate(f'{summary}\n\n{key_chgs}')}",
        )
        ctx.user_data["comparing"] = False
    except Exception as exc:
        user_logger(uid).error(f"Comparison error: {exc}", exc_info=True)
        await _safe_reply(update, f"❌ Error: {str(exc)[:200]}")


async def _handle_general_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE, uid: int) -> None:
    try:
        async with _typing(update):
            answer = await _ai_call_with_retry(
                Svc.ai_service.call_ai,
                prompt=update.message.text,
                system_role="You are a helpful AI assistant. Respond in plain text. Do not use emojis. Be clear and concise.",
            )
        await _safe_reply(update, _truncate(answer))
    except Exception as exc:
        user_logger(uid).error(f"General query error: {exc}", exc_info=True)
        await _safe_reply(update, f"Error: {str(exc)[:200]}")


# ──────────────────────────────────────────────────────────────────────────────
# Document generation conversation
# ──────────────────────────────────────────────────────────────────────────────

async def generate_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await _safe_reply(update, "📝 *What document would you like?*\n\n(e.g. 'Python Best Practices Guide')")
    return GENERATE_TOPIC


async def generate_topic(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    ctx.user_data["topic"] = topic
    await update.message.reply_text(
        f"Topic: *{topic}*\n\nChoose format:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            [["Word (.docx)", "PDF"]], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return GENERATE_FORMAT


async def generate_format(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    uid   = update.effective_user.id
    fmt   = update.message.text
    topic = ctx.user_data.get("topic", "Document")
    # Remove the reply keyboard immediately
    await update.message.reply_text("\u200b", reply_markup=ReplyKeyboardRemove())
    try:
        async with _typing(update):
            content = await _ai_call_with_retry(Svc.ai_service.generate_document, topic)
            with _tmp_path(suffix=".docx" if "Word" in fmt else ".pdf") as fpath:
                loop = asyncio.get_running_loop()
                if "Word" in fmt:
                    await loop.run_in_executor(
                        None, functools.partial(DocumentGenerator.generate_docx, topic, content, output_path=str(fpath))
                    )
                else:
                    await loop.run_in_executor(
                        None, functools.partial(DocumentGenerator.generate_pdf, topic, content, output_path=str(fpath))
                    )
                with open(fpath, "rb") as f:
                    await update.message.reply_document(
                        document=f,
                        caption=f"✅ *{topic}*\n\n_Your document is ready!_",
                        parse_mode=ParseMode.MARKDOWN,
                    )
        _bump(uid, "documents_generated")
        await update.message.reply_text(
            "🎉 *What's Next?*", parse_mode=ParseMode.MARKDOWN, reply_markup=_after_generate_kb()
        )
    except Exception as exc:
        user_logger(uid).error(f"Doc generation error: {exc}", exc_info=True)
        await _safe_reply(update, f"❌ Generation failed: {str(exc)[:200]}")
    return ConversationHandler.END


# ──────────────────────────────────────────────────────────────────────────────
# Image generation conversation
# ──────────────────────────────────────────────────────────────────────────────

async def image_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await _safe_reply(update, "🎨 *Create an AI Image*\n\nDescribe what you'd like to see:")
    return IMAGE_PROMPT


async def image_prompt_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    prompt = update.message.text
    ctx.user_data["image_prompt"] = prompt
    await update.message.reply_text(
        f"Prompt: *{prompt}*\n\nChoose a style:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            [["Realistic", "Abstract"], ["Artistic"]],
            one_time_keyboard=True, resize_keyboard=True,
        ),
    )
    return IMAGE_STYLE


async def image_style_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    uid    = update.effective_user.id
    style  = {"realistic": "realistic", "abstract": "abstract", "artistic": "artistic"}.get(
        update.message.text.lower().split()[0], "realistic"
    )
    prompt = ctx.user_data.get("image_prompt", "artwork")
    # Remove the reply keyboard immediately
    await update.message.reply_text("\u200b", reply_markup=ReplyKeyboardRemove())
    try:
        async with _typing(update):
            with _tmp_path(suffix=".png") as img_path:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None,
                    functools.partial(
                        Svc.image_service.generate_from_prompt,
                        prompt, style, output_path=str(img_path)
                    )
                )
                Svc.gallery_service.add_image(uid, str(img_path), prompt, tags=["user", style], style=style)
                with open(img_path, "rb") as f:
                    await update.message.reply_photo(
                        photo=f,
                        caption=f"✅ Style: *{style}*\n✨ _Saved to gallery!_",
                        parse_mode=ParseMode.MARKDOWN,
                    )
        _bump(uid, "images_generated")
        await update.message.reply_text(
            "🎉 *What's Next?*", parse_mode=ParseMode.MARKDOWN, reply_markup=_after_image_kb()
        )
    except Exception as exc:
        user_logger(uid).error(f"Image style error: {exc}", exc_info=True)
        await _safe_reply(update, f"❌ Image generation failed: {str(exc)[:200]}")
    return ConversationHandler.END


# ──────────────────────────────────────────────────────────────────────────────
# Gallery & stats
# ──────────────────────────────────────────────────────────────────────────────

async def gallery_view(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid    = update.effective_user.id
    images = Svc.gallery_service.get_gallery_summary(uid, limit=5)
    if not images:
        await _safe_reply(
            update,
            "📸 *Your Gallery*\n\nEmpty! Generate images with /image.",
            reply_markup=_kb([("🎨 Create Image", "menu_image"), ("🏠 Main Menu", "menu_main")]),
        )
        return
    msg = f"📸 *Your Gallery ({len(images)} images)*\n\n"
    for i, img in enumerate(images, 1):
        msg += f"{i}. _{img['style']}_ — {img['prompt'][:55]}{'…' if len(img['prompt'])>55 else ''}\n"
    await _safe_reply(
        update, msg,
        reply_markup=_kb(
            [("🎨 Create More", "menu_image"), ("📦 Export ZIP", "menu_export")],
            [("🏠 Main Menu", "menu_main")],
        ),
    )


async def stats_view(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid   = update.effective_user.id
    stats = Svc.user_manager.get_user_statistics(uid) or {}
    imgs  = Svc.storage.get_user_images_count(uid)
    size  = Svc.storage.get_user_gallery_size(uid)
    await _safe_reply(
        update,
        "📊 *Your Statistics*\n\n"
        f"📄 Analysed:   {stats.get('documents_processed', 0)}\n"
        f"✏️ Generated:  {stats.get('documents_generated', 0)}\n"
        f"🎨 Images:     {stats.get('images_generated', 0)}\n"
        f"🎙️ Voices:     {stats.get('voices_transcribed', 0)}\n\n"
        f"📸 Gallery:    {imgs} images\n"
        f"💾 Storage:    {format_file_size(size)}",
        reply_markup=_main_menu_kb(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Admin broadcast  (/broadcast <message>)
# ──────────────────────────────────────────────────────────────────────────────

async def broadcast_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await _safe_reply(update, "❌ Not authorised.")
        return
    if not ctx.args:
        await _safe_reply(update, "Usage: /broadcast <message>")
        return
    message_text = " ".join(ctx.args)
    all_users = Svc.user_manager.get_all_users()
    sent, failed = 0, 0
    for target_id in all_users:
        try:
            await ctx.bot.send_message(target_id, message_text, parse_mode=ParseMode.MARKDOWN)
            sent += 1
            await asyncio.sleep(0.05)   # respect Telegram rate limits
        except TelegramError:
            failed += 1
    await _safe_reply(update, f"📢 Broadcast complete: {sent} sent, {failed} failed.")


# ──────────────────────────────────────────────────────────────────────────────
# Cancel & error handler
# ──────────────────────────────────────────────────────────────────────────────

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    for key in ("in_chat_mode", "comparing"):
        ctx.user_data.pop(key, None)
    await update.message.reply_text("❌ Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Unhandled exception: {ctx.error}", exc_info=ctx.error)
    if isinstance(update, Update) and update.message:
        try:
            await update.message.reply_text(
                "❌ An unexpected error occurred. Please try again or use /menu."
            )
        except TelegramError:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# Application factory
# ──────────────────────────────────────────────────────────────────────────────

def build_application():
    Config.validate()
    Config.create_directories()
    Svc.init_all()

    app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()

    # ── Commands ──────────────────────────────────────────────────────────────
    for name, fn in {
        "start":      start,
        "help":       help_command,
        "menu":       menu_command,
        "analyze":    analyze_command,
        "summary":    analyze_command,
        "summarize":  summarize_command,
        "outline":    outline_command,
        "search":     search_command,
        "errors":     errors_command,
        "translate":  translate_command,
        "gallery":    gallery_view,
        "stats":      stats_view,
        "ask":        ask_start,
        "chat":       ask_start,
        "compare":    compare_start,
        "category":   category_command,
        "quality":    quality_command,
        "language":   language_command,
        "clear":      clear_command,
        "export":     export_command,
        "broadcast":  broadcast_command,
    }.items():
        app.add_handler(CommandHandler(name, fn))

    # ── Inline callbacks ──────────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(handle_menu_callback, pattern=r"^(menu_|help_)"))
    app.add_handler(CallbackQueryHandler(handle_document_action_callback, pattern=r"^action_"))

    # ── Conversations ─────────────────────────────────────────────────────────
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("generate", generate_start)],
        states={
            GENERATE_TOPIC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_topic)],
            GENERATE_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_format)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("image", image_start)],
        states={
            IMAGE_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, image_prompt_handler)],
            IMAGE_STYLE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, image_style_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    # ── Media ─────────────────────────────────────────────────────────────────
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

    # ── General text (must be last) ───────────────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ── Error handler ─────────────────────────────────────────────────────────
    app.add_error_handler(error_handler)

    return app


# ──────────────────────────────────────────────────────────────────────────────
# Startup / shutdown lifecycle
# ──────────────────────────────────────────────────────────────────────────────

async def _on_startup(app) -> None:
    await Svc.init_async()
    logger.info("Async services ready (aiohttp session open).")


async def _on_shutdown(app) -> None:
    await Svc.shutdown()
    logger.info("Bot shut down cleanly.")


def main() -> None:
    app = build_application()
    app.post_init    = _on_startup
    app.post_shutdown = _on_shutdown

    logger.info("Bot v2 starting…")
    print("✅ Bot v2 is running! Press Ctrl+C to stop.")

    # SIGTERM for Docker / systemd
    def _sigterm(sig, frame):
        logger.info("SIGTERM received — stopping…")
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _sigterm)

    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()