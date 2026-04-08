import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeHandler:
    """
    Class to handle interactions with Claude AI API.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))

    def analyze_text(self, text):
        """
        Send text to Claude API and get analysis.
        Returns summary, key points, insight, and action items.
        """
        prompt = f"""
        Analyze the following document text and provide:
        1. A concise summary (2-3 sentences)
        2. 5 key points
        3. 1 smart insight
        4. Action items (if any)

        Document text:
        {text[:10000]}  # Limit text to avoid token limits
        """

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7,
                system="You are a helpful assistant that analyzes documents.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            # Retry once
            try:
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    temperature=0.7,
                    system="You are a helpful assistant that analyzes documents.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            except Exception as e2:
                raise Exception(f"Claude API failed after retry: {str(e2)}")