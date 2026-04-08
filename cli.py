#!/usr/bin/env python3
"""Command-line interface for the Al-Powered Office Document Automation System."""

import os
import sys
import click
import json
from typing import Optional
from datetime import datetime
from pathlib import Path
from tabulate import tabulate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import get_config, Config
from src.models.user import UserManager
from src.models.storage import UserGalleryStorage
from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator
from src.services.ai_generation import AIGenerationService
from src.services.image_generator import ImageGenerator
from src.services.image_gallery import ImageGalleryService
from src.utils.helpers import format_file_size, get_logger

logger = get_logger(__name__)
config = get_config()

# Ensure directories exist
Config.create_directories()


@click.group()
def cli() -> None:
    """Al-Powered Office Document Automation System CLI."""
    pass


@cli.group()
def document() -> None:
    """Document operations."""
    pass


@document.command()
@click.argument('file_path', type=click.Path(exists=True))
def analyze(file_path: str) -> None:
    """Analyze a document."""
    try:
        if not DocumentReader.is_supported_file(file_path):
            click.secho("❌ Unsupported file type", fg='red')
            return
        
        click.secho("🔄 Reading document...", fg='yellow')
        text = DocumentReader.extract_text(file_path)
        
        click.secho("🔄 Analyzing with AI...", fg='yellow')
        ai_service = AIGenerationService()
        analysis = ai_service.analyze_document(text)
        
        click.secho("\n📊 Analysis Result:\n", fg='green')
        click.echo(analysis)
        
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@document.command()
@click.option('--topic', prompt='Document topic', help='Topic for the document')
@click.option('--format', type=click.Choice(['docx', 'pdf']), default='docx', help='Output format')
@click.option('--output', default='.', help='Output directory')
def generate(topic: str, format: str, output: str) -> None:
    """Generate a new document."""
    try:
        click.secho("🔄 Generating document content...", fg='yellow')
        ai_service = AIGenerationService()
        content = ai_service.generate_document(topic)
        
        click.secho("📝 Creating document...", fg='yellow')
        if format == 'docx':
            filepath = DocumentGenerator.generate_docx(topic, content, output_dir=output)
        else:
            filepath = DocumentGenerator.generate_pdf(topic, content, output_dir=output)
        
        click.secho(f"✅ Document saved: {filepath}", fg='green')
        
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@cli.group()
def image() -> None:
    """Image operations."""
    pass


@image.command()
@click.option('--prompt', prompt='Image description', help='What image to generate')
@click.option('--style', type=click.Choice(['realistic', 'abstract', 'artistic']), default='realistic')
@click.option('--output', default='.', help='Output directory')
def generate(prompt: str, style: str, output: str) -> None:
    """Generate an image from text prompt."""
    try:
        click.secho("🔄 Generating image...", fg='yellow')
        image_gen = ImageGenerator()
        image_path = image_gen.generate_from_prompt(prompt, style, output_dir=output)
        click.secho(f"✅ Image saved: {image_path}", fg='green')
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@cli.group()
def gallery() -> None:
    """Gallery operations."""
    pass


@gallery.command()
@click.option('--user-id', type=int, required=True, help='User ID')
def stats(user_id: int) -> None:
    """Show gallery statistics."""
    try:
        storage = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
        gallery_service = ImageGalleryService(storage)
        
        images_count = storage.get_user_images_count(user_id)
        storage_size = storage.get_user_gallery_size(user_id)
        
        click.secho("\n📊 Gallery Statistics:\n", fg='green')
        click.echo(f"Total Images: {images_count}")
        click.echo(f"Storage Used: {format_file_size(storage_size)}")
        click.echo(f"Total Storage (All Users): {format_file_size(storage.get_total_storage_used())}")
        
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@gallery.command()
@click.option('--user-id', type=int, required=True, help='User ID')
@click.option('--limit', type=int, default=10, help='Number of images to display')
def list(user_id: int, limit: int) -> None:
    """List user's images."""
    try:
        storage = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
        gallery_service = ImageGalleryService(storage)
        
        images = gallery_service.get_gallery_summary(user_id, limit=limit)
        
        if not images:
            click.secho("No images found", fg='yellow')
            return
        
        table_data = []
        for img in images:
            table_data.append([
                img['id'],
                img['filename'],
                img['prompt'][:40] + "..." if len(img['prompt']) > 40 else img['prompt'],
                img['style'],
                img.get('downloads', 0)
            ])
        
        click.secho("\n📸 User Gallery:\n", fg='green')
        click.echo(tabulate(table_data, headers=['ID', 'File', 'Prompt', 'Style', 'Downloads']))
        
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@cli.group()
def user() -> None:
    """User operations."""
    pass


@user.command()
@click.option('--user-id', type=int, required=True, help='User ID')
@click.option('--first-name', default='', help='First name')
@click.option('--last-name', default='', help='Last name')
def create(user_id: int, first_name: str, last_name: str) -> None:
    """Create a new user."""
    try:
        user_manager = UserManager(data_dir=Config.USERS_DIR)
        user = user_manager.create_or_get_user(
            user_id, first_name=first_name, last_name=last_name
        )
        click.secho(f"✅ User created: {user.user_id}", fg='green')
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@user.command()
@click.option('--user-id', type=int, required=True, help='User ID')
def stats(user_id: int) -> None:
    """Show user statistics."""
    try:
        user_manager = UserManager(data_dir=Config.USERS_DIR)
        user = user_manager.get_user(user_id)
        
        if not user:
            click.secho("User not found", fg='red')
            return
        
        click.secho(f"\n👤 User: {user.first_name} {user.last_name}\n", fg='green')
        click.echo(f"ID: {user.user_id}")
        click.echo(f"Email: {user.username}")
        click.echo(f"Created: {user.created_at}")
        click.echo(f"Last Active: {user.last_active}")
        
        click.secho("\n📊 Statistics:", fg='green')
        stats_data = [[k, v] for k, v in user.statistics.items()]
        click.echo(tabulate(stats_data, headers=['Metric', 'Value']))
        
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')


@cli.command()
def version() -> None:
    """Show version information."""
    click.echo("Al-Powered Office Document Automation System v1.0.0")


if __name__ == '__main__':
    cli()
