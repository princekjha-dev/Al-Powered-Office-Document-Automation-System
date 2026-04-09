"""
API routes for chat image generation.
Endpoints to generate images within chat sessions and manage galleries.
"""

from flask import Blueprint, request, jsonify, send_file
import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Create blueprint for image generation routes
image_bp = Blueprint('images', __name__, url_prefix='/api/images')


def init_image_routes(app, image_generator_service):
    """
    Initialize image generation routes.
    
    Args:
        app: Flask app
        image_generator_service: ChatImageGenerator instance
    """
    
    @image_bp.route('/generate', methods=['POST'])
    def generate_image():
        """
        Generate image in a chat session.
        
        Request JSON:
        {
            "user_id": 123456,
            "session_id": "session_123",
            "prompt": "a beautiful landscape",
            "style": "realistic",
            "api_provider": "huggingface" (optional)
        }
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            required = ['user_id', 'session_id', 'prompt']
            if not all(field in data for field in required):
                return jsonify({'error': 'Missing required fields'}), 400
            
            user_id = data['user_id']
            session_id = data['session_id']
            prompt = data['prompt']
            style = data.get('style', 'realistic')
            api_provider = data.get('api_provider')
            
            # Generate image
            logger.info(f"Generating image for user {user_id}, session {session_id}")
            result = image_generator_service.generate_image_for_chat(
                user_id=user_id,
                session_id=session_id,
                prompt=prompt,
                style=style,
                api_provider=api_provider
            )
            
            return jsonify({
                'success': True,
                'image': result
            }), 200
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return jsonify({'error': str(e)}), 500

    @image_bp.route('/session/<session_id>', methods=['GET'])
    def get_session_images(session_id):
        """
        Get all images generated in a chat session.
        
        Args:
            session_id: Chat session ID
        """
        try:
            images = image_generator_service.get_session_images(session_id)
            return jsonify({
                'success': True,
                'session_id': session_id,
                'images': images,
                'count': len(images)
            }), 200
        except Exception as e:
            logger.error(f"Error retrieving session images: {e}")
            return jsonify({'error': str(e)}), 500

    @image_bp.route('/gallery/<int:user_id>', methods=['GET'])
    def get_user_gallery(user_id):
        """
        Get all images in user's gallery.
        
        Args:
            user_id: User ID
        """
        try:
            images = image_generator_service.get_user_gallery(user_id)
            return jsonify({
                'success': True,
                'user_id': user_id,
                'images': images,
                'count': len(images)
            }), 200
        except Exception as e:
            logger.error(f"Error retrieving gallery: {e}")
            return jsonify({'error': str(e)}), 500

    @image_bp.route('/gallery/image/<int:user_id>/<int:image_id>', methods=['GET'])
    def get_image_file(user_id, image_id):
        """
        Download image file.
        
        Args:
            user_id: User ID
            image_id: Image ID
        """
        try:
            gallery_dir = os.path.join('data/galleries', str(user_id))
            metadata_file = os.path.join(gallery_dir, f"{image_id}_meta.json")
            
            if not os.path.exists(metadata_file):
                return jsonify({'error': 'Image not found'}), 404
            
            # Load metadata to get filepath
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            image_path = metadata.get('filepath')
            if not os.path.exists(image_path):
                return jsonify({'error': 'Image file not found'}), 404
            
            return send_file(image_path, mimetype='image/png'), 200
            
        except Exception as e:
            logger.error(f"Error retrieving image: {e}")
            return jsonify({'error': str(e)}), 500

    @image_bp.route('/status', methods=['GET'])
    def get_status():
        """
        Get image generation status and available APIs.
        """
        try:
            return jsonify({
                'success': True,
                'available_apis': image_generator_service.get_available_apis(),
                'available_styles': image_generator_service.get_available_styles(),
                'status': 'ready'
            }), 200
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({'error': str(e)}), 500

    @image_bp.route('/clear-gallery/<int:user_id>', methods=['DELETE'])
    def clear_gallery(user_id):
        """
        Clear user's image gallery (optional endpoint).
        
        Args:
            user_id: User ID
        """
        try:
            import shutil
            gallery_dir = os.path.join('data/galleries', str(user_id))
            
            if os.path.exists(gallery_dir):
                shutil.rmtree(gallery_dir)
                logger.info(f"Cleared gallery for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': f'Gallery cleared for user {user_id}'
            }), 200
            
        except Exception as e:
            logger.error(f"Error clearing gallery: {e}")
            return jsonify({'error': str(e)}), 500

    # Register blueprint
    app.register_blueprint(image_bp)
    logger.info("Image generation routes initialized")
