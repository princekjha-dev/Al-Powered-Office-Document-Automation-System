"""Unit tests for service layer."""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator
from src.services.image_generator import ImageGenerator
from src.services.image_gallery import ImageGalleryService
from src.services.ai_generation import AIGenerationService
from src.models.storage import UserGalleryStorage


class TestDocumentReader(unittest.TestCase):
    """Test DocumentReader service."""
    
    def test_is_supported_file(self) -> None:
        """Test file type validation."""
        self.assertTrue(DocumentReader.is_supported_file("test.pdf"))
        self.assertTrue(DocumentReader.is_supported_file("test.docx"))
        self.assertTrue(DocumentReader.is_supported_file("test.xlsx"))
        self.assertFalse(DocumentReader.is_supported_file("test.txt"))
        self.assertFalse(DocumentReader.is_supported_file("test.exe"))

    def test_check_file_size(self) -> None:
        """Test file size validation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * 1000)
            tmp_path = tmp.name
        
        try:
            self.assertTrue(DocumentReader.check_file_size(tmp_path))
        finally:
            os.remove(tmp_path)


class TestDocumentGenerator(unittest.TestCase):
    """Test DocumentGenerator service."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_docx(self) -> None:
        """Test Word document generation."""
        title = "Test Document"
        content = "## Section 1\nTest content\n## Section 2\nMore content"
        
        file_path = DocumentGenerator.generate_docx(
            title, content, filename="test", output_dir=self.temp_dir
        )
        
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith(".docx"))
    
    def test_generate_pdf(self) -> None:
        """Test PDF document generation."""
        title = "Test PDF"
        content = "## Section 1\nTest content"
        
        file_path = DocumentGenerator.generate_pdf(
            title, content, filename="test_pdf", output_dir=self.temp_dir
        )
        
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith(".pdf"))


class TestImageGenerator(unittest.TestCase):
    """Test ImageGenerator service."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.image_gen = ImageGenerator(api_key=None)
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_placeholder_image(self) -> None:
        """Test placeholder image creation."""
        image_path = self.image_gen._create_placeholder_image(
            "Test prompt", output_dir=self.temp_dir
        )
        
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(image_path.endswith(".png"))


class TestUserGalleryStorage(unittest.TestCase):
    """Test UserGalleryStorage."""
    
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
    
    def test_gallery_directory_creation(self) -> None:
        """Test gallery directory creation."""
        gallery_dir = self.storage.get_user_gallery_dir(self.user_id)
        self.assertTrue(os.path.exists(gallery_dir))
    
    def test_metadata_operations(self) -> None:
        """Test metadata save/load."""
        test_metadata = {
            "images": [
                {"id": 0, "filename": "test.png", "prompt": "test", "style": "realistic"}
            ],
            "total_stored": 1
        }
        
        self.storage.save_gallery_metadata(self.user_id, test_metadata)
        loaded = self.storage.load_gallery_metadata(self.user_id)
        
        self.assertEqual(loaded["total_stored"], 1)
        self.assertEqual(len(loaded["images"]), 1)


class TestAIGenerationService(unittest.TestCase):
    """Test AIGenerationService."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.ai_service = AIGenerationService(api_key="test_key")
    
    @patch('requests.post')
    def test_analyze_document(self, mock_post: Mock) -> None:
        """Test document analysis."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test analysis"}}]
        }
        mock_post.return_value = mock_response
        
        result = self.ai_service.analyze_document("Test document text")
        self.assertIsNotNone(result)
    
    @patch('requests.post')
    def test_generate_document(self, mock_post: Mock) -> None:
        """Test document generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "## Section\nGenerated content"}}]
        }
        mock_post.return_value = mock_response
        
        result = self.ai_service.generate_document("Test topic")
        self.assertIsNotNone(result)


class TestImageGalleryService(unittest.TestCase):
    """Test ImageGalleryService."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = UserGalleryStorage(base_dir=self.temp_dir)
        self.gallery_service = ImageGalleryService(self.storage)
        self.user_id = 12345
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_gallery_summary(self) -> None:
        """Test getting gallery summary."""
        summary = self.gallery_service.get_gallery_summary(self.user_id)
        self.assertIsInstance(summary, list)


if __name__ == '__main__':
    unittest.main()
