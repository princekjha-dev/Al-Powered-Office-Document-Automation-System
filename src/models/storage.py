"""
Unified storage system for managing user galleries and data.
Handles multi-user image storage with proper organization.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class UserGalleryStorage:
    """Manages per-user image galleries with organized storage."""

    def __init__(self, base_dir: str = "data/galleries"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def get_user_gallery_dir(self, user_id: int) -> str:
        """Get directory for user's gallery."""
        user_dir = os.path.join(self.base_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def get_user_images_dir(self, user_id: int) -> str:
        """Get directory for user's images."""
        images_dir = os.path.join(self.get_user_gallery_dir(user_id), "images")
        os.makedirs(images_dir, exist_ok=True)
        return images_dir

    def get_metadata_file(self, user_id: int) -> str:
        """Get gallery metadata file path for user."""
        return os.path.join(self.get_user_gallery_dir(user_id), "metadata.json")

    def save_image(self, user_id: int, image_path: str, image_name: str) -> str:
        """Save image to user's gallery directory."""
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")

        user_images_dir = self.get_user_images_dir(user_id)
        destination_path = os.path.join(user_images_dir, image_name)
        
        try:
            shutil.copy2(image_path, destination_path)
            return destination_path
        except Exception as e:
            raise Exception(f"Failed to save image: {e}")

    def get_image_path(self, user_id: int, image_name: str) -> str:
        """Get full path to user's image."""
        return os.path.join(self.get_user_images_dir(user_id), image_name)

    def load_gallery_metadata(self, user_id: int) -> Dict:
        """Load gallery metadata for user."""
        metadata_file = self.get_metadata_file(user_id)
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata for user {user_id}: {e}")
        
        return {"images": [], "total_stored": 0}

    def save_gallery_metadata(self, user_id: int, metadata: Dict) -> bool:
        """Save gallery metadata for user."""
        metadata_file = self.get_metadata_file(user_id)
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving metadata for user {user_id}: {e}")
            return False

    def get_user_gallery_size(self, user_id: int) -> int:
        """Get total size of user's gallery in bytes."""
        user_images_dir = self.get_user_images_dir(user_id)
        total_size = 0
        
        for filename in os.listdir(user_images_dir):
            filepath = os.path.join(user_images_dir, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        
        return total_size

    def get_user_images_count(self, user_id: int) -> int:
        """Get total number of images for user."""
        user_images_dir = self.get_user_images_dir(user_id)
        return len([f for f in os.listdir(user_images_dir) if os.path.isfile(os.path.join(user_images_dir, f))])

    def delete_user_image(self, user_id: int, image_name: str) -> bool:
        """Delete a specific image from user's gallery."""
        image_path = self.get_image_path(user_id, image_name)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                return True
        except Exception as e:
            print(f"Error deleting image {image_name}: {e}")
        return False

    def delete_user_gallery(self, user_id: int) -> bool:
        """Delete entire user gallery."""
        user_gallery_dir = self.get_user_gallery_dir(user_id)
        try:
            if os.path.exists(user_gallery_dir):
                shutil.rmtree(user_gallery_dir)
                return True
        except Exception as e:
            print(f"Error deleting gallery for user {user_id}: {e}")
        return False

    def get_all_users_galleries(self) -> List[int]:
        """Get list of all user IDs with galleries."""
        users = []
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                if item.isdigit():
                    users.append(int(item))
        return users

    def get_total_storage_used(self) -> int:
        """Get total storage used by all galleries."""
        total = 0
        for user_id in self.get_all_users_galleries():
            total += self.get_user_gallery_size(user_id)
        return total

    def export_user_gallery(self, user_id: int, export_format: str = "json") -> str:
        """Export user gallery metadata."""
        metadata = self.load_gallery_metadata(user_id)
        
        if export_format == "json":
            return json.dumps(metadata, indent=2)
        elif export_format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Filename", "Prompt", "Style", "Created", "Downloads"])
            
            for img in metadata.get("images", []):
                writer.writerow([
                    img.get("id"),
                    img.get("filename"),
                    img.get("prompt", ""),
                    img.get("style", ""),
                    img.get("created_at", ""),
                    img.get("downloads", 0),
                ])
            
            return output.getvalue()
        
        return ""


class SessionStorage:
    """Manages temporary session data for users."""

    def __init__(self, data_dir: str = "data/sessions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def save_session(self, user_id: int, session_data: Dict) -> bool:
        """Save user session data temporarily."""
        session_file = os.path.join(self.data_dir, f"session_{user_id}.json")
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session for user {user_id}: {e}")
            return False

    def load_session(self, user_id: int) -> Optional[Dict]:
        """Load user session data."""
        session_file = os.path.join(self.data_dir, f"session_{user_id}.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading session for user {user_id}: {e}")
        return None

    def delete_session(self, user_id: int) -> bool:
        """Delete user session."""
        session_file = os.path.join(self.data_dir, f"session_{user_id}.json")
        try:
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
        except Exception as e:
            print(f"Error deleting session for user {user_id}: {e}")
        return False

    def clear_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clear sessions older than specified hours."""
        from datetime import timedelta
        import time
        
        deleted_count = 0
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception:
                    pass
        
        return deleted_count
