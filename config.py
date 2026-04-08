import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'gpt-4o-mini')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GEMII_API_KEY = os.getenv('GEMII_API_KEY')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openrouter').lower()


def validate_environment():
    """Ensure required environment values are available."""
    if not TELEGRAM_TOKEN:
        raise EnvironmentError('TELEGRAM_TOKEN is required.')


def get_api_key(provider: str):
    """Return the configured API key for the selected AI provider."""
    provider = provider.lower() 
    return {
        'openrouter': OPENROUTER_API_KEY,
        'openai': OPENAI_API_KEY,
        'groq': GROQ_API_KEY,
        'gemii': GEMII_API_KEY,
    }.get(provider)
