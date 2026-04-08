#!/usr/bin/env python3
"""
Simplified REST API Dashboard - Hackathon Edition.

Provides 8 core API endpoints for document automation.
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import Config
from src.models.user import UserManager
from src.models.storage import UserGalleryStorage
from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator
from src.services.ai_generation import AIGenerationService
from src.services.image_generator import ImageGenerator
from src.services.image_gallery import ImageGalleryService
from src.utils.helpers import get_logger, format_file_size

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE
CORS(app)

logger = get_logger(__name__)

# Services
user_manager = UserManager()
storage = UserGalleryStorage()
gallery_service = ImageGalleryService(storage)
ai_service = AIGenerationService()
image_gen = ImageGenerator()


@app.route('/api/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({"status": "✅ healthy", "version": "1.0"})


@app.route('/api/documents/analyze', methods=['POST'])
def analyze_document():
    """Analyze uploaded document."""
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    if not DocumentReader.is_supported_file(file.filename):
        return jsonify({"error": "Unsupported format (PDF, DOCX, XLSX)"}), 400
    
    try:
        filepath = os.path.join(Config.TEMP_DIR, secure_filename(file.filename))
        file.save(filepath)
        
        text = DocumentReader.extract_text(filepath)
        if not text.strip():
            return jsonify({"error": "No text extracted"}), 400
        
        analysis = ai_service.analyze_document(text)
        prompts = ai_service.generate_image_prompts(text, count=2)
        
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "image_prompts": prompts,
            "text_length": len(text)
        })
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/generate', methods=['POST'])
def generate_document():
    """Generate a document."""
    data = request.get_json()
    topic = data.get('topic')
    format_type = data.get('format', 'docx')
    
    if not topic:
        return jsonify({"error": "No topic"}), 400
    
    try:
        content = ai_service.generate_document(topic)
        
        if format_type == 'pdf':
            filepath = DocumentGenerator.generate_pdf(topic, content, output_dir=Config.TEMP_DIR)
        else:
            filepath = DocumentGenerator.generate_docx(topic, content, output_dir=Config.TEMP_DIR)
        
        return jsonify({
            "success": True,
            "message": "Document created",
            "file": os.path.basename(filepath),
            "format": format_type
        })
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/images/generate', methods=['POST'])
def generate_image():
    """Generate an image."""
    data = request.get_json()
    prompt = data.get('prompt')
    style = data.get('style', 'realistic')
    user_id = data.get('user_id')
    
    if not prompt:
        return jsonify({"error": "No prompt"}), 400
    
    try:
        image_path = image_gen.generate_from_prompt(prompt, style, output_dir=Config.TEMP_DIR)
        
        if user_id:
            gallery_service.add_image(user_id, image_path, prompt, tags=['generated', style], style=style)
        
        return jsonify({
            "success": True,
            "message": "Image created",
            "image": os.path.basename(image_path),
            "prompt": prompt,
            "style": style
        })
    except Exception as e:
        logger.error(f"Image error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/galleries/<int:user_id>', methods=['GET'])
def get_gallery(user_id):
    """Get user's gallery."""
    try:
        limit = request.args.get('limit', 10, type=int)
        images = gallery_service.get_gallery_summary(user_id, limit=limit)
        
        return jsonify({
            "success": True,
            "images": images,
            "count": len(images),
            "total": storage.get_user_images_count(user_id),
            "storage": format_file_size(storage.get_user_gallery_size(user_id))
        })
    except Exception as e:
        logger.error(f"Gallery error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/galleries/<int:user_id>/stats', methods=['GET'])
def gallery_stats(user_id):
    """Get gallery statistics."""
    try:
        return jsonify({
            "success": True,
            "total_images": storage.get_user_images_count(user_id),
            "storage_used": format_file_size(storage.get_user_gallery_size(user_id)),
            "storage_bytes": storage.get_user_gallery_size(user_id)
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a user."""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "No user_id"}), 400
    
    try:
        user = user_manager.create_or_get_user(
            user_id,
            username=data.get('username', ''),
            first_name=data.get('first_name', '')
        )
        return jsonify({"success": True, "user": user.to_dict()}), 201
    except Exception as e:
        logger.error(f"User error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information."""
    try:
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "gallery": storage.get_user_images_count(user_id),
            "storage": format_file_size(storage.get_user_gallery_size(user_id))
        })
    except Exception as e:
        logger.error(f"User error: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Server error"}), 500


if __name__ == '__main__':
    print("🚀 Starting API dashboard on http://localhost:5000")
    print("📚 API Endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/documents/analyze - Analyze document")
    print("  POST /api/documents/generate - Generate document")
    print("  POST /api/images/generate - Generate image")
    print("  GET  /api/galleries/<user_id> - Get gallery")
    print("  GET  /api/galleries/<user_id>/stats - Gallery stats")
    print("  POST /api/users - Create user")
    print("  GET  /api/users/<user_id> - Get user")
    app.run(host='0.0.0.0', port=5000, debug=False)
        }
    })


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int) -> Dict[str, Any]:
    """Get user details."""
    try:
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user.to_dict(),
            "gallery_count": storage.get_user_images_count(user_id),
            "storage_used": format_file_size(storage.get_user_gallery_size(user_id))
        })
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/users', methods=['POST'])
def create_user() -> Dict[str, Any]:
    """Create a new user."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
        
        user = user_manager.create_or_get_user(
            user_id,
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        return jsonify({"user": user.to_dict()}), 201
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/analyze', methods=['POST'])
def analyze_document() -> Dict[str, Any]:
    """Analyze uploaded document."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not DocumentReader.is_supported_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            text = DocumentReader.extract_text(filepath)
            if not text.strip():
                return jsonify({"error": "Could not extract text"}), 400
            
            analysis = ai_service.analyze_document(text)
            
            # Extract image prompts
            image_prompts = ai_service.generate_image_prompts(text, count=3)
            
            return jsonify({
                "analysis": analysis,
                "image_prompts": image_prompts,
                "text_length": len(text),
                "file_name": filename
            })
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/generate', methods=['POST'])
def generate_document() -> Dict[str, Any]:
    """Generate document."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        doc_format = data.get('format', 'docx')
        
        if not topic:
            return jsonify({"error": "topic required"}), 400
        
        content = ai_service.generate_document(topic)
        
        if doc_format == 'docx':
            filepath = DocumentGenerator.generate_docx(topic, content, output_dir=Config.TEMP_DIR)
        else:
            filepath = DocumentGenerator.generate_pdf(topic, content, output_dir=Config.TEMP_DIR)
        
        return jsonify({
            "status": "success",
            "file_path": filepath,
            "file_name": os.path.basename(filepath),
            "format": doc_format
        })
    except Exception as e:
        logger.error(f"Error generating document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/images/generate', methods=['POST'])
def generate_image() -> Dict[str, Any]:
    """Generate image from prompt."""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        style = data.get('style', 'realistic')
        user_id = data.get('user_id')
        
        if not prompt:
            return jsonify({"error": "prompt required"}), 400
        
        image_path = image_gen.generate_from_prompt(prompt, style, output_dir=Config.TEMP_DIR)
        
        response_data = {
            "status": "success",
            "image_path": image_path,
            "prompt": prompt,
            "style": style
        }
        
        # Add to gallery if user specified
        if user_id:
            try:
                entry = gallery_service.add_image(
                    user_id, image_path, prompt,
                    tags=['generated', style], style=style
                )
                response_data["gallery_entry"] = entry
            except Exception as e:
                logger.warning(f"Failed to add to gallery: {e}")
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/galleries/<int:user_id>', methods=['GET'])
def get_gallery(user_id: int) -> Dict[str, Any]:
    """Get user's image gallery."""
    try:
        limit = request.args.get('limit', 10, type=int)
        images = gallery_service.get_gallery_summary(user_id, limit=limit)
        
        return jsonify({
            "images": images,
            "total_count": storage.get_user_images_count(user_id),
            "storage_used": format_file_size(storage.get_user_gallery_size(user_id))
        })
    except Exception as e:
        logger.error(f"Error getting gallery: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/galleries/<int:user_id>/stats', methods=['GET'])
def get_gallery_stats(user_id: int) -> Dict[str, Any]:
    """Get gallery statistics."""
    try:
        images = gallery_service.get_gallery_summary(user_id, limit=1000)
        
        # Calculate statistics
        styles = {}
        total_downloads = 0
        for img in images:
            style = img.get('style', 'unknown')
            styles[style] = styles.get(style, 0) + 1
            total_downloads += img.get('downloads', 0)
        
        return jsonify({
            "total_images": storage.get_user_images_count(user_id),
            "storage_used": storage.get_user_gallery_size(user_id),
            "storage_used_formatted": format_file_size(storage.get_user_gallery_size(user_id)),
            "total_downloads": total_downloads,
            "styles_breakdown": styles
        })
    except Exception as e:
        logger.error(f"Error getting gallery stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/galleries/<int:user_id>/export', methods=['GET'])
def export_gallery(user_id: int) -> Dict[str, Any]:
    """Export gallery data."""
    try:
        export_format = request.args.get('format', 'json')
        data = storage.export_user_gallery(user_id, export_format=export_format)
        
        return jsonify({
            "format": export_format,
            "data": data,
            "timestamp": str(__import__('datetime').datetime.now())
        })
    except Exception as e:
        logger.error(f"Error exporting gallery: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings() -> Dict[str, Any]:
    """Get system settings."""
    return jsonify({
        "max_file_size_mb": Config.MAX_FILE_SIZE_MB,
        "image_generation_enabled": Config.IMAGE_GENERATION_ENABLED,
        "default_image_style": Config.DEFAULT_IMAGE_STYLE,
        "max_images_per_document": Config.MAX_IMAGE_GENERATION_ENABLED
    })


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error: Exception) -> Dict[str, Any]:
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error: Exception) -> Dict[str, Any]:
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


def run_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> None:
    """Run the web dashboard."""
    logger.info(f"Starting dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard(debug=True)
