"""
Image generation service - Generate images using AI APIs.

Uses Hugging Face InferenceClient with fal-ai provider and FLUX.1-Krea-dev model
for high-quality image generation. Falls back to placeholder generation when
API key is not configured.
"""

import os
import tempfile
from datetime import datetime
from typing import List, Tuple, Optional
import logging

from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Service for generating images using Hugging Face InferenceClient.
    
    Uses fal-ai provider with FLUX.1-Krea-dev model for high-quality generation.
    Supports multiple style presets. Falls back to placeholder images when API
    key is unavailable.
    """

    # Style prompt modifiers for different aesthetics
    STYLE_MODIFIERS = {
        "realistic": "photorealistic, ultra detailed, high resolution, 8k",
        "abstract": "abstract art, geometric shapes, vibrant colors, modern art",
        "artistic": "digital art, concept art, illustration, trending on artstation",
    }

    DEFAULT_MODEL = "black-forest-labs/FLUX.1-Krea-dev"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        """
        Initialize image generator with Hugging Face InferenceClient.
        
        Args:
            api_key: Hugging Face API token (optional, falls back to HF_TOKEN env var)
            model: Model ID to use (optional, defaults to FLUX.1-Krea-dev)
        """
        self.api_key = api_key or os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_API_KEY')
        self.model = model or os.getenv('HF_IMAGE_MODEL', self.DEFAULT_MODEL)
        self.client = None

        if self.api_key:
            try:
                self.client = InferenceClient(
                    provider="fal-ai",
                    api_key=self.api_key,
                )
                logger.info(f"InferenceClient initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize InferenceClient: {e}")
                self.client = None
        else:
            logger.warning("HF_TOKEN not configured. Image generation will use placeholders.")

    def generate_from_prompt(self, prompt: str, style: str = "realistic", 
                            filename: Optional[str] = None, output_dir: str = "") -> str:
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
        if not output_dir:
            output_dir = tempfile.gettempdir()
        os.makedirs(output_dir, exist_ok=True)

        if not self.client:
            logger.warning("InferenceClient not available. Using placeholder image.")
            return self._create_placeholder_image(prompt, filename, output_dir)

        try:
            return self._generate_with_client(prompt, style, filename, output_dir)
        except Exception as e:
            logger.error(f"Image generation failed: {e}. Using placeholder.")
            return self._create_placeholder_image(prompt, filename, output_dir)

    def _generate_with_client(self, prompt: str, style: str = "realistic",
                              filename: Optional[str] = None, output_dir: str = "") -> str:
        """
        Generate image using Hugging Face InferenceClient.
        
        Args:
            prompt: Text prompt
            style: Image style
            filename: Optional filename
            output_dir: Output directory
        
        Returns:
            Path to saved image
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}"

        filepath = os.path.join(output_dir, f"{filename}.png")

        # Enhance prompt with style modifiers
        style_modifier = self.STYLE_MODIFIERS.get(style, self.STYLE_MODIFIERS["realistic"])
        enhanced_prompt = f"{prompt}, {style_modifier}"

        logger.info(f"Generating image with prompt: {enhanced_prompt[:100]}...")

        # Generate image using InferenceClient (returns PIL.Image)
        image = self.client.text_to_image(
            enhanced_prompt,
            model=self.model,
        )

        # Save PIL Image to file
        image.save(filepath)
        logger.info(f"Image generated and saved: {filepath}")
        return filepath

    def generate_from_document(self, text: str, style: str = "realistic", 
                              max_prompts: int = 3, output_dir: str = "") -> List[Tuple[str, str]]:
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

    def _create_placeholder_image(self, prompt: str, filename: Optional[str] = None, 
                                 output_dir: str = "") -> str:
        """Create placeholder image when API unavailable."""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            raise Exception("PIL not available. Install pillow: pip install pillow")

        if not output_dir:
            output_dir = tempfile.gettempdir()

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
                      output_dir: str = "") -> List[str]:
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
