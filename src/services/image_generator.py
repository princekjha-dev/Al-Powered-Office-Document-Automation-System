"""
Image generation service - Generate images using AI APIs.

Supports multiple image generation models and styles. Provides both
real API integration and fallback placeholder generation for offline use.
"""

import requests
import os
from datetime import datetime
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Service for generating images using Hugging Face APIs.
    
    Supports multiple image generation models and styles (realistic, abstract, artistic).
    Falls back to placeholder images when API is unavailable.
    """

    HF_MODELS = {
        "realistic": "stabilityai/stable-diffusion-2",
        "abstract": "runwayml/stable-diffusion-v1-5",
        "artistic": "prompthero/openjourney",
    }

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize image generator.
        
        Args:
            api_key: Hugging Face API key (optional, can be set via environment)
        """
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.hf_endpoint = "https://api-inference.huggingface.co/models/"
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def generate_from_prompt(self, prompt: str, style: str = "realistic", 
                            filename: Optional[str] = None, output_dir: str = "/tmp") -> str:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            style: Image style ('realistic', 'abstract', 'artistic')
            filename: Optional custom filename
            output_dir: Directory to save image
        
        Returns:
            Path to the generated image file
        """
        if not self.api_key:
            logger.warning("Hugging Face API key not configured. Using mock image generation.")
            return self._create_placeholder_image(prompt, filename, output_dir)

        model = self.HF_MODELS.get(style, self.HF_MODELS["realistic"])
        
        try:
            return self._query_huggingface(model, prompt, filename, output_dir)
        except Exception as e:
            logger.error(f"HF API failed: {e}. Using placeholder.")
            return self._create_placeholder_image(prompt, filename, output_dir)

    def generate_from_document(self, text: str, style: str = "realistic", 
                              max_prompts: int = 3, output_dir: str = "/tmp") -> List[Tuple[str, str]]:
        """
        Generate multiple images based on document content.
        
        Args:
            text: Document text
            style: Image style
            max_prompts: Maximum number of images
            output_dir: Output directory
        
        Returns:
            List of (image_path, prompt) tuples
        """
        prompts = self._extract_image_prompts(text, max_prompts)
        images = []
        
        for prompt in prompts:
            try:
                image_path = self.generate_from_prompt(prompt, style, output_dir=output_dir)
                images.append((image_path, prompt))
            except Exception as e:
                logger.error(f"Failed to generate image: {e}")
                continue
        
        return images

    def _extract_image_prompts(self, text: str, max_prompts: int = 3) -> List[str]:
        """Extract key concepts from document text."""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = text.lower().split()
        keywords = []
        
        for word in words:
            clean_word = word.strip('.,!?;:()[]{}""\'')
            if len(clean_word) > 4 and clean_word not in stop_words and clean_word.isalpha():
                keywords.append(clean_word)
        
        keywords = list(set(keywords))[:max_prompts]
        prompts = [f"Professional infographic about {kw}, detailed, high quality" for kw in keywords]
        
        if len(prompts) < max_prompts:
            text_preview = text[:200].replace('\n', ' ')
            prompts.append(f"Professional illustration related to: {text_preview[:100]}")
        
        return prompts[:max_prompts]

    def _query_huggingface(self, model_id: str, prompt: str, 
                          filename: Optional[str] = None, output_dir: str = "/tmp") -> str:
        """Query Hugging Face API to generate image."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}"

        filepath = os.path.join(output_dir, f"{filename}.png")

        try:
            payload = {"inputs": prompt}
            response = requests.post(
                self.hf_endpoint + model_id,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Image generated: {filepath}")
                return filepath
            else:
                raise Exception(f"API error: {response.status_code}")

        except Exception as e:
            raise Exception(f"Failed to generate image: {str(e)}")

    def _create_placeholder_image(self, prompt: str, filename: Optional[str] = None, 
                                 output_dir: str = "/tmp") -> str:
        """Create placeholder image when API unavailable."""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            raise Exception("PIL not available. Install pillow: pip install pillow")

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}"

        filepath = os.path.join(output_dir, f"{filename}.png")
        img = Image.new('RGB', (800, 600), color='#1f4e78')
        draw = ImageDraw.Draw(img)
        
        prompt_text = prompt[:80] + "..." if len(prompt) > 80 else prompt
        draw.text((50, 250), "Image Generation", fill='white')
        draw.text((50, 300), prompt_text, fill='#e0e0e0')
        
        img.save(filepath)
        return filepath

    def generate_batch(self, prompts: List[str], style: str = "realistic", 
                      output_dir: str = "/tmp") -> List[str]:
        """Generate multiple images from a list of prompts."""
        images = []
        for i, prompt in enumerate(prompts):
            try:
                filename = f"batch_image_{i}_{datetime.now().strftime('%H%M%S')}"
                image_path = self.generate_from_prompt(prompt, style, filename, output_dir)
                images.append(image_path)
            except Exception as e:
                logger.error(f"Failed to generate image {i}: {e}")
                continue
        
        return images
