import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


class OpenRouterHandler:
    """
    Class to handle interactions with OpenRouter AI.
    """

    ENDPOINT = "https://openrouter.ai/v1/chat/completions"

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise EnvironmentError('OPENROUTER_API_KEY is required for OpenRouter access.')
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL or 'gpt-4o-mini'

    def analyze_text(self, text):
        """
        Send text to OpenRouter API and get analysis.
        Returns summary, key points, insight, and action items.
        """
        prompt = (
            "Analyze the following document text and provide:\n"
            "1. A concise summary (2-3 sentences)\n"
            "2. 5 key points\n"
            "3. 1 smart insight\n"
            "4. Action items (if any)\n\n"
            f"Document text:\n{text[:10000]}"
        )

        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that analyzes documents.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 1000,
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
            try:
                response = requests.post(self.ENDPOINT, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            except Exception as second_error:
                raise Exception(f'OpenRouter API failed after retry: {second_error}')
