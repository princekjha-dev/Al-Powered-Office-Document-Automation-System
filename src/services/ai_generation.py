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

    ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
    ANTI_HALLUCINATION_INSTRUCTIONS = (
        "When answering, do not invent facts. Base your response only on the supplied input. "
        "If the information is missing or uncertain, say 'I cannot verify this from the input.' "
        "Avoid speculation and clearly flag uncertainty."
    )

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
            f"{self.ANTI_HALLUCINATION_INSTRUCTIONS}\n\n"
            "Analyze the following document text and provide:\n"
            "1. A concise summary (2-3 sentences)\n"
            "2. 5 key points\n"
            "3. 1 smart insight\n"
            "4. Action items (if any)\n\n"
            f"Document text:\n{text[:10000]}"
        )

        analysis = self._make_request(
            prompt,
            system_role="You are a helpful assistant that analyzes documents.",
            max_tokens=1200,
            temperature=0.2
        )

        verification = self.verify_response(analysis, text)
        return f"{analysis}\n\n---\n*Hallucination check:*\n{verification}"

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
            max_tokens=2000,
            temperature=0.2
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

    def call_ai(self, prompt, system_role="You are a helpful assistant", 
               max_tokens=1000, temperature=0.7):
        """
        Generic AI call method for use by other services.
        
        Args:
            prompt: User prompt
            system_role: System role
            max_tokens: Maximum tokens
            temperature: Temperature
        
        Returns:
            AI response
        """
        return self._make_request(prompt, system_role, max_tokens, temperature)

    def verify_response(self, response_text, source_text):
        """
        Verify generated response against source content to catch hallucinations.
        
        Args:
            response_text: Generated AI output
            source_text: Original source or document text
        
        Returns:
            Text summary of whether any unsupported claims were detected
        """
        prompt = (
            "You are a precise verifier. Review the response below and compare it to the source content. "
            "List any statements that cannot be verified from the source. "
            "If the response is fully grounded, reply with 'Verified: no unsupported claims found.'\n\n"
            f"Source content:\n{source_text[:8000]}\n\n"
            f"Response:\n{response_text[:4000]}"
        )

        return self._make_request(
            prompt,
            system_role="You are a precise verifier that detects unsupported claims.",
            max_tokens=300,
            temperature=0.2
        )

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
            'HTTP-Referer': 'https://github.com/ai-document-bot',
            'X-Title': 'AI Document Automation',
        }

        for attempt in range(2):
            try:
                response = requests.post(self.ENDPOINT, headers=headers, json=payload, timeout=60)
                
                # Check for HTTP errors
                if response.status_code != 200:
                    error_text = response.text[:500] if response.text else "Empty response"
                    raise Exception(f"API returned HTTP {response.status_code}: {error_text}")
                
                # Check for empty response body
                if not response.text or not response.text.strip():
                    raise Exception("API returned empty response body")
                
                result = response.json()
                
                # Check for API-level errors
                if 'error' in result:
                    error_msg = result['error']
                    if isinstance(error_msg, dict):
                        error_msg = error_msg.get('message', str(error_msg))
                    raise Exception(f"API error: {error_msg}")
                
                # Extract content
                if 'choices' not in result or not result['choices']:
                    raise Exception(f"No choices in API response: {str(result)[:200]}")
                
                return result['choices'][0]['message']['content'].strip()
                
            except Exception as e:
                if attempt == 0:
                    continue  # Retry once
                raise Exception(f"API failed after retry: {e}")
