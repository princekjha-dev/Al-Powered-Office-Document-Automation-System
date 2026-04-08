"""Integration tests for the system."""

import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.user import UserManager, User
from src.models.storage import UserGalleryStorage
from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator
from src.config.settings import Config


class TestUserManagementWorkflow(unittest.TestCase):
    """Test complete user management workflow."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.user_manager = UserManager(data_dir=self.temp_dir)
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_user_creation_and_retrieval(self) -> None:
        """Test creating and retrieving users."""
        user_id = 123456
        user = self.user_manager.create_or_get_user(
            user_id, username="testuser", first_name="Test"
        )
        
        self.assertEqual(user.user_id, user_id)
        self.assertEqual(user.username, "testuser")
        
        # Retrieve user
        retrieved_user = self.user_manager.get_user(user_id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, user_id)
    
    def test_user_statistics_update(self) -> None:
        """Test updating user statistics."""
        user_id = 123456
        self.user_manager.create_or_get_user(user_id)
        
        self.user_manager.update_user_statistics(
            user_id, documents_processed=1, images_generated=2
        )
        
        stats = self.user_manager.get_user_statistics(user_id)
        self.assertEqual(stats["documents_processed"], 1)
        self.assertEqual(stats["images_generated"], 2)


class TestDocumentGenerationWorkflow(unittest.TestCase):
    """Test document generation workflow."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_document_generation_pipeline(self) -> None:
        """Test complete document generation."""
        title = "Python Best Practices"
        content = """## Introduction
        This is a test document about Python best practices.
        
        ## Key Points
        - Use type hints
        - Follow PEP 8
        - Write tests
        
        ## Conclusion
        Follow best practices for better code quality."""
        
        # Generate DOCX
        docx_path = DocumentGenerator.generate_docx(
            title, content, output_dir=self.temp_dir
        )
        self.assertTrue(os.path.exists(docx_path))
        
        # Generate PDF
        pdf_path = DocumentGenerator.generate_pdf(
            title, content, output_dir=self.temp_dir
        )
        self.assertTrue(os.path.exists(pdf_path))


class TestGalleryWorkflow(unittest.TestCase):
    """Test image gallery workflow."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = UserGalleryStorage(base_dir=self.temp_dir)
        self.user_id = 12345
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_gallery_metadata_workflow(self) -> None:
        """Test complete gallery workflow."""
        # Create metadata
        metadata = {
            "images": [
                {
                    "id": 0, "filename": "test1.png",
                    "prompt": "a beautiful landscape",
                    "style": "realistic", "tags": ["nature"],
                    "created_at": "2024-01-01T00:00:00"
                }
            ],
            "total_stored": 1
        }
        
        # Save metadata
        self.storage.save_gallery_metadata(self.user_id, metadata)
        
        # Load and verify
        loaded = self.storage.load_gallery_metadata(self.user_id)
        self.assertEqual(loaded["total_stored"], 1)
        self.assertEqual(loaded["images"][0]["prompt"], "a beautiful landscape")


if __name__ == '__main__':
    unittest.main()
