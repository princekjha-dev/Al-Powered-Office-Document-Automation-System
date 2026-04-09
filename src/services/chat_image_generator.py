"""
Chat Image Generation Service - Generate and manage images within chat sessions.

Integrates image generation with chat, storing images in user galleries
and sessions. Supports multiple free AI APIs (Hugging Face, Replicate, Stability AI).
"""

import os
import json
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ChatImageGenerator:
    """
    Generate images during chat sessions and store them in galleries.
    Supports multiple free APIs with fallback mechanism.
    """

    # Free APIs configuration
    APIS = {
        "huggingface": {
            "enabled": bool(os.getenv('HF_TOKEN')),
            "priority": 1,
            "models": [
                "black-forest-labs/FLUX.1-Krea-dev",
                "stabilityai/stable-diffusion-3-medium",
                "runwayml/stable-diffusion-v1-5"
            ]
        },
        "replicate": {
            "enabled": bool(os.getenv('REPLICATE_API_TOKEN')),
            "priority": 2,
            "models": [
                "black-forest-labs/flux-pro",
                "stability-ai/sdxl",
                "openjourney/openjourney"
            ]
        },
        "stability": {
            "enabled": bool(os.getenv('STABILITY_API_KEY')),
            "priority": 3,
            "models": ["sd3-large", "sd3-large-turbo"]
        }
    }

    def __init__(self, data_dir: str = "data"):
        """
        Initialize chat image generator.
        
        Args:
            data_dir: Base data directory
        """
        self.data_dir = data_dir
        self.galleries_dir = os.path.join(data_dir, "galleries")
        self.sessions_dir = os.path.join(data_dir, "chat_sessions")
        
        os.makedirs(self.galleries_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        self.image_generator = self._init_image_generator()
        logger.info("ChatImageGenerator initialized")

    def _init_image_generator(self):
        """Initialize the primary image generator."""
        try:
            from src.services.image_generator import ImageGenerator
            return ImageGenerator()
        except ImportError:
            logger.error("ImageGenerator not available")
            return None

    def generate_image_for_chat(
        self,
        user_id: int,
        session_id: str,
        prompt: str,
        style: str = "realistic",
        api_provider: Optional[str] = None
    ) -> Dict:
        """
        Generate image during chat and store in gallery.
        
        Args:
            user_id: User ID
            session_id: Chat session ID
            prompt: Image generation prompt
            style: Image style (realistic, abstract, artistic)
            api_provider: Specific API to use (optional)
        
        Returns:
            Image metadata dictionary
        """
        try:
            # Determine which API to use
            if not api_provider:
                api_provider = self._select_best_api()
            
            logger.info(f"Generating image using {api_provider}: {prompt[:50]}...")
            
            # Generate image based on provider
            image_result = self._generate_with_provider(
                prompt, style, api_provider, user_id
            )
            
            if not image_result:
                return self._create_placeholder_response(prompt)
            
            # Save to gallery
            image_metadata = self._save_to_gallery(
                user_id, image_result, prompt, style
            )
            
            # Link to chat session
            self._link_to_session(user_id, session_id, image_metadata)
            
            logger.info(f"Image generated successfully: {image_metadata['id']}")
            return image_metadata
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return self._create_placeholder_response(prompt)

    def _select_best_api(self) -> str:
        """Select best available API based on priority."""
        enabled_apis = [
            (name, config['priority'])
            for name, config in self.APIS.items()
            if config.get('enabled')
        ]
        
        if not enabled_apis:
            logger.warning("No image generation APIs configured")
            return "placeholder"
        
        # Sort by priority (lower is better)
        enabled_apis.sort(key=lambda x: x[1])
        return enabled_apis[0][0]

    def _generate_with_provider(
        self,
        prompt: str,
        style: str,
        provider: str,
        user_id: int
    ) -> Optional[str]:
        """
        Generate image with specific provider.
        
        Args:
            prompt: Image prompt
            style: Image style
            provider: API provider name
            user_id: User ID for organizing
        
        Returns:
            Path to generated image or None
        """
        output_dir = os.path.join(self.galleries_dir, str(user_id))
        os.makedirs(output_dir, exist_ok=True)
        
        if provider == "huggingface":
            return self._generate_huggingface(prompt, style, output_dir)
        elif provider == "replicate":
            return self._generate_replicate(prompt, style, output_dir)
        elif provider == "stability":
            return self._generate_stability(prompt, style, output_dir)
        else:
            return None

    def _generate_huggingface(
        self,
        prompt: str,
        style: str,
        output_dir: str
    ) -> Optional[str]:
        """Generate using Hugging Face API."""
        if not self.image_generator:
            return None
        
        try:
            style_prompt = self._enhance_prompt(prompt, style)
            image_path = self.image_generator.generate_from_prompt(
                style_prompt,
                style=style,
                output_dir=output_dir
            )
            return image_path if os.path.exists(image_path) else None
        except Exception as e:
            logger.error(f"Hugging Face generation failed: {e}")
            return None

    def _generate_replicate(
        self,
        prompt: str,
        style: str,
        output_dir: str
    ) -> Optional[str]:
        """Generate using Replicate API (free tier)."""
        try:
            import replicate
            
            api_token = os.getenv('REPLICATE_API_TOKEN')
            if not api_token:
                logger.warning("REPLICATE_API_TOKEN not configured")
                return None
            
            # Use Replicate's stable diffusion
            style_prompt = self._enhance_prompt(prompt, style)
            
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a60c3b23c3f280fe0e3ccf97cdfb0ef1",
                input={"prompt": style_prompt}
            )
            
            if output:
                # Download and save image
                import requests
                image_url = output[0] if isinstance(output, list) else output
                response = requests.get(image_url)
                
                filename = f"replicate_{datetime.now().timestamp()}.png"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath
        except ImportError:
            logger.warning("replicate library not installed")
        except Exception as e:
            logger.error(f"Replicate generation failed: {e}")
        
        return None

    def _generate_stability(
        self,
        prompt: str,
        style: str,
        output_dir: str
    ) -> Optional[str]:
        """Generate using Stability AI free tier."""
        try:
            import requests
            
            api_key = os.getenv('STABILITY_API_KEY')
            if not api_key:
                logger.warning("STABILITY_API_KEY not configured")
                return None
            
            style_prompt = self._enhance_prompt(prompt, style)
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/sd3-large-turbo/text-to-image",
                headers={
                    "authorization": f"Bearer {api_key}",
                    "accept": "image/*"
                },
                json={
                    "prompt": style_prompt,
                    "output_format": "png"
                }
            )
            
            if response.status_code == 200:
                filename = f"stability_{datetime.now().timestamp()}.png"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath
        except Exception as e:
            logger.error(f"Stability AI generation failed: {e}")
        
        return None

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """
        Enhance prompt with style modifiers.
        
        Args:
            prompt: Base prompt
            style: Style to apply
        
        Returns:
            Enhanced prompt
        """
        style_modifiers = {
            "realistic": "photorealistic, ultra detailed, high resolution, 8k, professional photography",
            "abstract": "abstract art, geometric shapes, vibrant colors, modern art, contemporary",
            "artistic": "digital art, concept art, illustration, trending on artstation, masterpiece",
            "anime": "anime style, cel shading, vibrant colors, manga illustration, professional",
            "watercolor": "watercolor painting, artistic, soft colors, elegant, beautiful",
            "sketch": "pencil sketch, line art, detailed drawing, black and white, professional"
        }
        
        modifier = style_modifiers.get(style, "")
        return f"{prompt}, {modifier}" if modifier else prompt

    def _save_to_gallery(
        self,
        user_id: int,
        image_path: str,
        prompt: str,
        style: str
    ) -> Dict:
        """
        Save image metadata to gallery.
        
        Args:
            user_id: User ID
            image_path: Path to image
            prompt: Generation prompt
            style: Style used
        
        Returns:
            Image metadata
        """
        gallery_dir = os.path.join(self.galleries_dir, str(user_id))
        os.makedirs(gallery_dir, exist_ok=True)
        
        # Create metadata
        image_id = int(datetime.now().timestamp() * 1000)
        metadata = {
            "id": image_id,
            "filename": os.path.basename(image_path),
            "filepath": image_path,
            "prompt": prompt,
            "style": style,
            "created_at": datetime.now().isoformat(),
            "url": f"/api/gallery/image/{user_id}/{image_id}"
        }
        
        # Save metadata file
        metadata_path = os.path.join(gallery_dir, f"{image_id}_meta.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata

    def _link_to_session(
        self,
        user_id: int,
        session_id: str,
        image_metadata: Dict
    ) -> None:
        """
        Link image to chat session.
        
        Args:
            user_id: User ID
            session_id: Chat session ID
            image_metadata: Image metadata
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session = json.load(f)
            else:
                session = {"id": session_id, "user_id": user_id, "messages": []}
            
            # Add image reference to session
            if "generated_images" not in session:
                session["generated_images"] = []
            
            session["generated_images"].append(image_metadata)
            
            # Save updated session
            with open(session_file, 'w') as f:
                json.dump(session, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to link image to session: {e}")

    def _create_placeholder_response(self, prompt: str) -> Dict:
        """
        Create placeholder response when generation fails.
        
        Args:
            prompt: Original prompt
        
        Returns:
            Placeholder metadata
        """
        return {
            "id": int(datetime.now().timestamp() * 1000),
            "prompt": prompt,
            "style": "placeholder",
            "created_at": datetime.now().isoformat(),
            "error": "Image generation unavailable. Please configure API keys.",
            "url": "/static/images/placeholder.png"
        }

    def get_session_images(
        self,
        session_id: str
    ) -> List[Dict]:
        """
        Get all images generated in a chat session.
        
        Args:
            session_id: Chat session ID
        
        Returns:
            List of image metadata
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session = json.load(f)
                    return session.get("generated_images", [])
        except Exception as e:
            logger.error(f"Failed to retrieve session images: {e}")
        
        return []

    def get_user_gallery(self, user_id: int) -> List[Dict]:
        """
        Get all images in user's gallery.
        
        Args:
            user_id: User ID
        
        Returns:
            List of image metadata
        """
        gallery_dir = os.path.join(self.galleries_dir, str(user_id))
        images = []
        
        try:
            if os.path.exists(gallery_dir):
                for filename in os.listdir(gallery_dir):
                    if filename.endswith('_meta.json'):
                        with open(os.path.join(gallery_dir, filename), 'r') as f:
                            images.append(json.load(f))
        except Exception as e:
            logger.error(f"Failed to retrieve gallery: {e}")
        
        return sorted(images, key=lambda x: x.get('created_at', ''), reverse=True)

    @staticmethod
    def get_available_apis() -> Dict[str, bool]:
        """Get status of available APIs."""
        return {
            name: config.get('enabled', False)
            for name, config in ChatImageGenerator.APIS.items()
        }

    @staticmethod
    def get_available_styles() -> List[str]:
        """Get list of available image styles."""
        return [
            "realistic",
            "abstract",
            "artistic",
            "anime",
            "watercolor",
            "sketch"
        ]
