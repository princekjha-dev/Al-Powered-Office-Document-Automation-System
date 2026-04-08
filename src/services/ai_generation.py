"""
AI text generation service for document analysis and generation.
"""

import requests
from src.config.settings import get_config

config = get_config()


class AIGenerationService:
    """
    Service for AI text generation using OpenRouter API.
    """

    ENDPOINT = "https://openrouter.ai/v1/chat/completions"

    def __init__(self, api_key=None, model=None):
        """
        Initialize AI generation service.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default from config)
        """
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.model = model or config.OPENROUTER_MODEL

    def analyze_document(self, text):
        """
        Analyze document text and provide comprehensive analysis.
        
        Args:
            text: Document text to analyze
        
        Returns:
            Analysis string with summary, key points, insights, and actions
        """
        prompt = (
            "Analyze the following document text and provide:\n"
            "1. A concise summary (2-3 sentences)\n"
            "2. 5 key points\n"
            "3. 1 smart insight\n"
            "4. Action items (if any)\n\n"
            f"Document text:\n{text[:10000]}"
        )

        return self._make_request(prompt, system_role="You are a helpful assistant that analyzes documents.")

    def generate_document(self, topic):
        """
        Generate comprehensive document content from a topic.
        
        Args:
            topic: Document topic
        
        Returns:
            Generated document content
        """
        prompt = (
            f"Generate a comprehensive, professional document about: {topic}\n\n"
            "Format the response with sections using ## for section headers. "
            "Include relevant information, examples, and best practices."
        )

        return self._make_request(
            prompt,
            system_role="You are a professional document generator.",
            max_tokens=2000
        )

    def generate_image_prompts(self, text, count=3):
        """
        Generate image prompts from text.
        
        Args:
            text: Input text
            count: Number of prompts to generate
        
        Returns:
            List of image prompts
        """
        prompt = (
            f"Generate {count} creative and detailed image generation prompts based on this text:\n\n{text[:500]}\n\n"
            "Return only the prompts, one per line, suitable for image generation AI."
        )

        response = self._make_request(prompt, max_tokens=500)
        return response.split('\n') if response else []

    def _make_request(self, prompt, system_role="You are a helpful assistant", 
                     max_tokens=1000, temperature=0.7):
        """
        Make API request to OpenRouter.
        
        Args:
            prompt: User prompt
            system_role: System role
            max_tokens: Maximum tokens
            temperature: Temperature
        
        Returns:
            Response text
        """
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_role},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        try:
            response = requests.post(self.ENDPOINT, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            # Retry once
            try:
                response = requests.post(self.ENDPOINT, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            except Exception as second_error:
                raise Exception(f'API failed after retry: {second_error}')
