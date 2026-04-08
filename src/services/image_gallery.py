"""
Image gallery service - Manage and organize generated images.
"""

import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ImageGalleryService:
    """
    Service to manage user image galleries with proper data organization.
    """

    def __init__(self, storage_manager):
        """
        Initialize gallery service.
        
        Args:
            storage_manager: UserGalleryStorage instance
        """
        self.storage = storage_manager

    def add_image(self, user_id, image_path, prompt, tags=None, style="realistic"):
        """
        Add image to user's gallery.
        
        Args:
            user_id: Telegram user ID
            image_path: Path to image file
            prompt: Prompt used to generate image
            tags: List of tags
            style: Generation style
        
        Returns:
            Image entry dictionary
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image not found: {image_path}")

        # Load existing metadata
        metadata = self.storage.load_gallery_metadata(user_id)
        
        # Create image entry
        image_id = len(metadata.get("images", []))
        filename = os.path.basename(image_path)
        
        image_entry = {
            "id": image_id,
            "filename": filename,
            "prompt": prompt,
            "tags": tags or [],
            "style": style,
            "created_at": datetime.now().isoformat(),
            "downloads": 0,
        }

        # Save image to storage
        try:
            saved_path = self.storage.save_image(user_id, image_path, filename)
            image_entry["stored_path"] = saved_path
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise

        # Update metadata
        metadata["images"].append(image_entry)
        metadata["total_stored"] = len(metadata["images"])
        self.storage.save_gallery_metadata(user_id, metadata)
        
        logger.info(f"Image added to user {user_id}'s gallery: {image_id}")
        return image_entry

    def get_gallery_summary(self, user_id, limit=10):
        """Get user's recent images."""
        metadata = self.storage.load_gallery_metadata(user_id)
        images = metadata.get("images", [])
        
        # Sort by creation date (newest first)
        images = sorted(images, key=lambda x: x["created_at"], reverse=True)
        return images[:limit]

    def search_by_prompt(self, user_id, query):
        """Search user's images by prompt keywords."""
        metadata = self.storage.load_gallery_metadata(user_id)
        query = query.lower()
        
        return [img for img in metadata.get("images", []) 
                if query in img["prompt"].lower()]

    def search_by_tag(self, user_id, tag):
        """Search user's images by tag."""
        metadata = self.storage.load_gallery_metadata(user_id)
        
        return [img for img in metadata.get("images", []) 
                if tag.lower() in [t.lower() for t in img.get("tags", [])]]

    def get_image_by_id(self, user_id, image_id):
        """Get specific image by ID."""
        metadata = self.storage.load_gallery_metadata(user_id)
        
        for img in metadata.get("images", []):
            if img["id"] == image_id:
                return img
        return None

    def increment_downloads(self, user_id, image_id):
        """Increment download count for an image."""
        metadata = self.storage.load_gallery_metadata(user_id)
        
        for img in metadata.get("images", []):
            if img["id"] == image_id:
                img["downloads"] = img.get("downloads", 0) + 1
                self.storage.save_gallery_metadata(user_id, metadata)
                break

    def get_gallery_stats(self, user_id):
        """Get user's gallery statistics."""
        metadata = self.storage.load_gallery_metadata(user_id)
        images = metadata.get("images", [])
        
        total_downloads = sum(img.get("downloads", 0) for img in images)
        styles = {}
        all_tags = set()
        
        for img in images:
            style = img.get("style", "unknown")
            styles[style] = styles.get(style, 0) + 1
            all_tags.update(img.get("tags", []))
        
        return {
            "total_images": len(images),
            "total_downloads": total_downloads,
            "styles": styles,
            "unique_tags": len(all_tags),
            "gallery_size": self.storage.get_user_gallery_size(user_id),
        }

    def delete_image(self, user_id, image_id):
        """Delete an image from user's gallery."""
        metadata = self.storage.load_gallery_metadata(user_id)
        images = metadata.get("images", [])
        
        for img in images:
            if img["id"] == image_id:
                filename = img.get("filename")
                images.remove(img)
                
                # Update metadata
                metadata["total_stored"] = len(images)
                self.storage.save_gallery_metadata(user_id, metadata)
                
                # Delete file
                self.storage.delete_user_image(user_id, filename)
                return True
        
        return False

    def export_gallery(self, user_id, format="json"):
        """Export user's gallery."""
        return self.storage.export_user_gallery(user_id, format)
