#!/usr/bin/env python3
"""
Web App Backend — AI-Powered Office Document Automation System.

Flask server that provides API endpoints for all features
and serves the web frontend.
"""

import os
import sys
import uuid
import tempfile
import re
import base64
from datetime import datetime

from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add project root to path so we can import from src/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from src.config.settings import Config
from src.utils.helpers import get_logger, format_file_size
from src.models.user import UserManager
from src.models.storage import UserGalleryStorage
from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator
from src.services.ai_generation import AIGenerationService
from src.services.image_generator import ImageGenerator
from src.services.image_gallery import ImageGalleryService
from src.services.document_chat import DocumentChat
from src.services.document_comparison import DocumentComparison
from src.services.document_categorization import DocumentCategorization
from src.services.language_detection import LanguageDetection
from src.services.document_quality import DocumentQuality
from src.services.chat_image_generator import ChatImageGenerator
from src.handlers.image_routes import init_image_routes

# ─── Setup ──────────────────────────────────────────────────
Config.create_directories()

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE
CORS(app)

logger = get_logger(__name__)

# ─── Initialize Services ────────────────────────────────────
user_manager = UserManager(data_dir=Config.USERS_DIR)
storage = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
ai_service = AIGenerationService()
image_gen = ImageGenerator()
gallery_service = ImageGalleryService(storage)
doc_chat = DocumentChat(data_dir=os.path.join(Config.DATA_DIR, 'chat_sessions'))
doc_comparison = DocumentComparison()
doc_category = DocumentCategorization()
lang_detection = LanguageDetection()
doc_quality = DocumentQuality()
chat_image_gen = ChatImageGenerator(data_dir=Config.DATA_DIR)

# In-memory session store for document Q&A
doc_sessions = {}  # session_id -> { text, chat_session_id }

logger.info("All services initialized for web app")


def clean_markdown_text(text: str) -> str:
    """Clean markdown artifacts for web display."""
    if not text:
        return ""
    cleaned = text.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("`", "")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


# ─── Serve Frontend ─────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/hero', methods=['GET'])
def hero_page():
    """Serve hero component page."""
    return render_template('hero-demo.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# ─── API: Health ─────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "services": {
            "ai": bool(ai_service),
            "image_gen": bool(image_gen),
            "doc_chat": bool(doc_chat),
            "lang_detection": bool(lang_detection),
        }
    })


# ─── API: Document Analysis ─────────────────────────────────

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Upload and analyze a document. Returns full report."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not DocumentReader.is_supported_file(file.filename):
        return jsonify({"error": "Unsupported format. Use PDF, DOCX, or XLSX."}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.TEMP_DIR, filename)
        file.save(filepath)

        try:
            text = DocumentReader.extract_text(filepath)
            if not text.strip():
                return jsonify({"error": "Could not extract text from file"}), 400

            # 1. Language detection
            lang_result = lang_detection.detect_language(text)

            # 2. Categorization
            category, cat_conf = doc_category.categorize_document(text)
            tags = doc_category.generate_tags(text, category)

            # 3. Quality scores
            scores = doc_quality.score_document(text)
            overall = scores.get("overall", 0)
            if overall >= 8:
                quality_label = "Excellent"
            elif overall >= 6:
                quality_label = "Good"
            elif overall >= 4:
                quality_label = "Fair"
            else:
                quality_label = "Needs Work"

            # 4. Stats
            word_count = len(text.split())
            line_count = len(text.split('\n'))
            pages_est = max(1, word_count // 250)

            # 5. AI Analysis
            ai_analysis = ""
            try:
                ai_analysis = ai_service.analyze_document(text)
            except Exception as ai_err:
                logger.error(f"AI analysis failed: {ai_err}")
                ai_analysis = f"AI analysis unavailable: {str(ai_err)[:200]}"
            ai_analysis = clean_markdown_text(ai_analysis)

            # 6. Create Q&A session for this document
            session_id = str(uuid.uuid4())
            chat_session_id = doc_chat.create_session(text, 0)
            doc_sessions[session_id] = {
                "text": text,
                "chat_session_id": chat_session_id,
                "filename": filename,
                "created": datetime.now().isoformat()
            }

            return jsonify({
                "success": True,
                "session_id": session_id,
                "filename": filename,
                "language": {
                    "code": lang_result.get("language", "?"),
                    "name": lang_result.get("language_name", "Unknown"),
                    "confidence": lang_result.get("confidence", 0),
                },
                "category": {
                    "name": category,
                    "confidence": cat_conf,
                    "tags": tags,
                },
                "quality": {
                    "overall": overall,
                    "label": quality_label,
                    "clarity": scores.get("clarity", 0),
                    "grammar": scores.get("grammar", 0),
                    "coherence": scores.get("coherence", 0),
                    "completeness": scores.get("completeness", 0),
                    "professionalism": scores.get("professionalism", 0),
                },
                "stats": {
                    "words": word_count,
                    "lines": line_count,
                    "pages": pages_est,
                },
                "ai_analysis": ai_analysis,
            })
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── API: Document Q&A ──────────────────────────────────────

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question about a previously analyzed document."""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    question = data.get('question')

    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        normalized_question = question.lower().strip()
        image_keywords = [
            "image", "poster", "thumbnail", "banner", "logo", "generate pic",
            "generate image", "create image", "make image", "photo", "illustration"
        ]
        if any(k in normalized_question for k in image_keywords):
            prompt = question.strip()
            image_path = image_gen.generate_from_prompt(prompt, style="realistic", output_dir=Config.TEMP_DIR)
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode("utf-8")
            try:
                os.remove(image_path)
            except Exception:
                pass
            return jsonify({
                "success": True,
                "mode": "image",
                "answer": "Image generated from your prompt.",
                "image_data": f"data:image/png;base64,{encoded}",
                "question": question,
            })

        if not session_id:
            return jsonify({"error": "session_id is required for document Q&A"}), 400

        session = doc_sessions.get(session_id)
        if not session:
            return jsonify({"error": "Session not found. Upload a document first."}), 404

        chat_session_id = session["chat_session_id"]
        answer = doc_chat.answer_question(chat_session_id, question, ai_service)
        answer = clean_markdown_text(answer)
        return jsonify({
            "success": True,
            "mode": "chat",
            "answer": answer,
            "question": question,
        })
    except Exception as e:
        logger.error(f"Q&A error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── API: Document Comparison ────────────────────────────────

@app.route('/api/compare', methods=['POST'])
def compare_documents():
    """Compare two documents or two text blocks."""
    text1 = ""
    text2 = ""

    if 'file1' in request.files and 'file2' in request.files:
        file1 = request.files['file1']
        file2 = request.files['file2']
        paths = []
        try:
            for f in [file1, file2]:
                fname = secure_filename(f.filename)
                fpath = os.path.join(Config.TEMP_DIR, f"cmp_{uuid.uuid4().hex[:8]}_{fname}")
                f.save(fpath)
                paths.append(fpath)
            text1 = DocumentReader.extract_text(paths[0])
            text2 = DocumentReader.extract_text(paths[1])
        finally:
            for p in paths:
                if os.path.exists(p):
                    os.remove(p)
    else:
        data = request.get_json() or {}
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        
        # If session_id is provided, use the session's document text as text1
        session_id = data.get('session_id', '')
        if session_id and session_id in doc_sessions:
            text1 = doc_sessions[session_id].get('text', '')

    if not text1 or not text2:
        return jsonify({"error": "Two documents or text blocks are required"}), 400

    try:
        result = doc_comparison.compare_text(text1, text2)
        summary = doc_comparison.get_change_summary(result)
        key_changes = doc_comparison.get_key_changes(result)

        # Try AI semantic analysis
        semantic = ""
        try:
            semantic = doc_comparison.analyze_semantic_changes(text1, text2, ai_service)
        except Exception:
            pass

        return jsonify({
            "success": True,
            "similarity": result.get("similarity_ratio", 0),
            "added": result.get("total_added", 0),
            "removed": result.get("total_removed", 0),
            "unchanged": result.get("total_unchanged", 0),
            "added_lines": result.get("added_lines", [])[:10],
            "removed_lines": result.get("removed_lines", [])[:10],
            "summary": summary,
            "key_changes": key_changes,
            "semantic_analysis": semantic,
        })
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── API: Document Generation ────────────────────────────────

@app.route('/api/generate', methods=['POST'])
def generate_document():
    """Generate a document from a topic."""
    data = request.get_json()
    topic = data.get('topic')
    fmt = data.get('format', 'docx')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        content = ai_service.generate_document(topic)

        if fmt == 'pdf':
            filepath = DocumentGenerator.generate_pdf(topic, content, output_dir=Config.TEMP_DIR)
            mimetype = 'application/pdf'
        else:
            filepath = DocumentGenerator.generate_docx(topic, content, output_dir=Config.TEMP_DIR)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath),
            mimetype=mimetype,
        )
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── API: Image Generation ───────────────────────────────────

@app.route('/api/image', methods=['POST'])
def generate_image():
    """Generate an image from a prompt."""
    data = request.get_json()
    prompt = data.get('prompt')
    style = data.get('style', 'realistic')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        image_path = image_gen.generate_from_prompt(prompt, style, output_dir=Config.TEMP_DIR)

        return send_file(
            image_path,
            mimetype='image/png',
        )
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── API: Quick Tools ────────────────────────────────────────

@app.route('/api/categorize', methods=['POST'])
def categorize_text():
    """Categorize text."""
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Text is required"}), 400

    category, confidence = doc_category.categorize_document(text)
    tags = doc_category.generate_tags(text, category)
    return jsonify({
        "success": True,
        "category": category,
        "confidence": confidence,
        "tags": tags,
    })


@app.route('/api/quality', methods=['POST'])
def quality_score():
    """Score document quality."""
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Text is required"}), 400

    scores = doc_quality.score_document(text)
    suggestions = doc_quality.get_improvement_suggestions(scores)
    return jsonify({
        "success": True,
        "scores": scores,
        "suggestions": suggestions,
    })


@app.route('/api/language', methods=['POST'])
def detect_language():
    """Detect language."""
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = lang_detection.detect_language(text)
    return jsonify({
        "success": True,
        "language": result.get("language"),
        "language_name": result.get("language_name"),
        "confidence": result.get("confidence"),
    })


# ─── API: Chat Image Generation ──────────────────────────────

@app.route('/api/chat-generate-image', methods=['POST'])
def chat_generate_image():
    """
    Generate image within chat session.
    
    Request JSON:
    {
        "user_id": 123456,
        "session_id": "session_123",
        "prompt": "a beautiful landscape",
        "style": "realistic"
    }
    """
    try:
        data = request.get_json()
        required = ['user_id', 'session_id', 'prompt']
        
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields: user_id, session_id, prompt'}), 400
        
        result = chat_image_gen.generate_image_for_chat(
            user_id=data['user_id'],
            session_id=data['session_id'],
            prompt=data['prompt'],
            style=data.get('style', 'realistic'),
            api_provider=data.get('api_provider')
        )
        
        return jsonify({'success': True, 'image': result}), 200
    except Exception as e:
        logger.error(f"Chat image generation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat-gallery/<int:user_id>', methods=['GET'])
def chat_get_gallery(user_id):
    """Get all images in user's gallery."""
    try:
        images = chat_image_gen.get_user_gallery(user_id)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'images': images,
            'count': len(images)
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving gallery: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat-session-images/<session_id>', methods=['GET'])
def chat_get_session_images(session_id):
    """Get all images generated in a chat session."""
    try:
        images = chat_image_gen.get_session_images(session_id)
        return jsonify({
            'success': True,
            'session_id': session_id,
            'images': images,
            'count': len(images)
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving session images: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/image-status', methods=['GET'])
def image_status():
    """Get image generation status and available APIs."""
    try:
        return jsonify({
            'success': True,
            'available_apis': chat_image_gen.get_available_apis(),
            'available_styles': chat_image_gen.get_available_styles(),
            'status': 'ready'
        }), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


# Initialize image generation routes
init_image_routes(app, chat_image_gen)

# ─── Error Handlers ──────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": f"File too large. Max size: {Config.MAX_FILE_SIZE_MB}MB"}), 413

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ─── Run ─────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 50)
    print("  AI Document Automation — Web App")
    print("=" * 50)
    print(f"  Open: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
