"""
User model and management system.
Handles user profiles, preferences, and metadata.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List


class User:
    """Represents a user of the bot."""
    
    def __init__(self, user_id: int, username: str = "", first_name: str = "", 
                 last_name: str = "", is_premium: bool = False):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_premium = is_premium
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        self.preferences = {
            "default_image_style": "realistic",
            "max_images_per_session": 5,
            "notifications_enabled": True,
        }
        self.statistics = {
            "documents_processed": 0,
            "documents_generated": 0,
            "images_generated": 0,
            "total_api_usage": 0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_premium": self.is_premium,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "preferences": self.preferences,
            "statistics": self.statistics,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        user = User(
            user_id=data["user_id"],
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            is_premium=data.get("is_premium", False),
        )
        user.created_at = data.get("created_at", user.created_at)
        user.last_active = data.get("last_active", user.last_active)
        user.preferences = data.get("preferences", user.preferences)
        user.statistics = data.get("statistics", user.statistics)
        return user

    def update_last_active(self) -> None:
        """Update last active timestamp."""
        self.last_active = datetime.now().isoformat()

    def increment_statistic(self, stat_name: str, value: int = 1) -> None:
        """Increment a user statistic."""
        if stat_name in self.statistics:
            self.statistics[stat_name] += value

    def set_preference(self, key: str, value: Any) -> None:
        """Set user preference."""
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference."""
        return self.preferences.get(key, default)


class UserManager:
    """Manages user data storage and retrieval."""

    def __init__(self, data_dir: str = "data/users"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.users_index_file = os.path.join(data_dir, "users_index.json")
        self.users: Dict[int, User] = {}
        self._load_index()

    def _get_user_file(self, user_id: int) -> str:
        """Get file path for user data."""
        return os.path.join(self.data_dir, f"user_{user_id}.json")

    def _load_index(self) -> None:
        """Load users index."""
        if os.path.exists(self.users_index_file):
            try:
                with open(self.users_index_file, 'r') as f:
                    index = json.load(f)
                    for user_id in index:
                        self._load_user(int(user_id))
            except Exception as e:
                print(f"Error loading users index: {e}")

    def _save_index(self) -> None:
        """Save users index."""
        try:
            with open(self.users_index_file, 'w') as f:
                json.dump(list(self.users.keys()), f, indent=2)
        except Exception as e:
            print(f"Error saving users index: {e}")

    def _load_user(self, user_id: int) -> Optional[User]:
        """Load user from file."""
        user_file = self._get_user_file(user_id)
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    user_data = json.load(f)
                    user = User.from_dict(user_data)
                    self.users[user_id] = user
                    return user
            except Exception as e:
                print(f"Error loading user {user_id}: {e}")
        return None

    def _save_user(self, user: User) -> bool:
        """Save user to file."""
        user_file = self._get_user_file(user.user_id)
        try:
            with open(user_file, 'w') as f:
                json.dump(user.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user {user.user_id}: {e}")
            return False

    def create_or_get_user(self, user_id: int, username: str = "", 
                         first_name: str = "", last_name: str = "") -> User:
        """Create new user or get existing."""
        if user_id in self.users:
            return self.users[user_id]
        
        # Try loading from file
        user = self._load_user(user_id)
        if user:
            return user
        
        # Create new user
        user = User(user_id, username, first_name, last_name)
        self.users[user_id] = user
        self._save_user(user)
        self._save_index()
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        if user_id in self.users:
            return self.users[user_id]
        return self._load_user(user_id)

    def save_user(self, user: User) -> bool:
        """Save user changes."""
        self.users[user.user_id] = user
        success = self._save_user(user)
        self._save_index()
        return success

    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self.users.values())

    def get_user_count(self) -> int:
        """Get total number of users."""
        return len(self.users)

    def delete_user(self, user_id: int) -> bool:
        """Delete user data."""
        if user_id in self.users:
            del self.users[user_id]
        
        user_file = self._get_user_file(user_id)
        if os.path.exists(user_file):
            try:
                os.remove(user_file)
                self._save_index()
                return True
            except Exception as e:
                print(f"Error deleting user {user_id}: {e}")
                return False
        return True

    def get_user_statistics(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user statistics."""
        user = self.get_user(user_id)
        if user:
            return user.statistics
        return None

    def update_user_statistics(self, user_id: int, **kwargs) -> bool:
        """Update user statistics."""
        user = self.get_user(user_id)
        if user:
            for key, value in kwargs.items():
                user.increment_statistic(key, value)
            return self.save_user(user)
        return False
