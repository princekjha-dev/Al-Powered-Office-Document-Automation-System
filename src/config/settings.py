"""
Configuration management system.
Centralized settings for the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # AI Services
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'gpt-4o-mini')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GEMII_API_KEY = os.getenv('GEMII_API_KEY')
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openrouter').lower()
    
    # Image Generation
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    IMAGE_GENERATION_ENABLED = os.getenv('IMAGE_GENERATION_ENABLED', 'true').lower() == 'true'
    DEFAULT_IMAGE_STYLE = os.getenv('DEFAULT_IMAGE_STYLE', 'realistic')
    MAX_IMAGES_PER_DOCUMENT = int(os.getenv('MAX_IMAGES_PER_DOCUMENT', '3'))
    ENABLE_IMAGE_GALLERY = os.getenv('ENABLE_IMAGE_GALLERY', 'true').lower() == 'true'
    
    # Storage
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    USERS_DIR = os.path.join(DATA_DIR, 'users')
    GALLERIES_DIR = os.path.join(DATA_DIR, 'galleries')
    SESSIONS_DIR = os.path.join(DATA_DIR, 'sessions')
    TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')
    
    # File Limits
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '20'))
    MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Application
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Cleanup settings
    AUTO_CLEANUP_ENABLED = os.getenv('AUTO_CLEANUP_ENABLED', 'true').lower() == 'true'
    CLEANUP_INTERVAL_HOURS = int(os.getenv('CLEANUP_INTERVAL_HOURS', '24'))
    SESSION_TIMEOUT_HOURS = int(os.getenv('SESSION_TIMEOUT_HOURS', '24'))

    @staticmethod
    def validate():
        """Validate critical configuration."""
        if not Config.TELEGRAM_TOKEN:
            raise EnvironmentError('TELEGRAM_TOKEN is required')
        if not Config.OPENROUTER_API_KEY:
            raise EnvironmentError('OPENROUTER_API_KEY is required')

    @staticmethod
    def create_directories():
        """Create necessary directories."""
        for directory in [Config.USERS_DIR, Config.GALLERIES_DIR, Config.SESSIONS_DIR]:
            os.makedirs(directory, exist_ok=True)


def get_config():
    """Get configuration instance."""
    return Config
