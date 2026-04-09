"""
Utility functions for the application.
"""

import logging
import os
from datetime import datetime


def setup_logging(log_level='INFO', log_file='app.log'):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Log file path
    """
    import sys
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Stream handler with UTF-8 encoding (fixes Windows cp1252 emoji crash)
    stream_handler = logging.StreamHandler(
        stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
    )
    stream_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, stream_handler]
    )


def get_logger(name):
    """Get logger instance."""
    return logging.getLogger(name)


def format_file_size(size_bytes):
    """Format bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_timestamp():
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_timestamp_iso():
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def ensure_dir_exists(directory):
    """Ensure directory exists."""
    os.makedirs(directory, exist_ok=True)


def cleanup_old_files(directory, max_age_hours=24):
    """
    Clean up files older than specified hours.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
    
    Returns:
        Number of files deleted
    """
    import time
    
    deleted_count = 0
    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)
    
    if not os.path.exists(directory):
        return deleted_count
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception:
                    pass
    
    return deleted_count
