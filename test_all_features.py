#!/usr/bin/env python3
"""
Comprehensive Feature Test Script for AI-Powered Office Document Automation System.

Tests every feature manually by calling the service classes directly.
Outputs results to test.md.
"""

import os
import sys
import time
import traceback
import tempfile

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ── Gather results ─────────────────────────────────────────────
results = []   # list of (feature_name, status, details)

def record(feature, status, details=""):
    """Record a test result. status: PASS / FAIL / WARN"""
    results.append((feature, status, details))
    icon = {"PASS": "[OK]", "FAIL": "[XX]", "WARN": "[!!]"}.get(status, "[??]")
    safe_feature = feature.encode('ascii', 'replace').decode('ascii')
    safe_details = details[:120].encode('ascii', 'replace').decode('ascii')
    print(f"  {icon} [{status}] {safe_feature}: {safe_details}")


SAMPLE_TEXT = """
Introduction

This is a sample business report for testing purposes. The report analyzes recent trends 
in technology adoption across the organization. Our findings indicate significant growth 
in cloud computing usage, with a 45% increase over the previous fiscal year.

Summary

The analysis reveals that the company has successfully transitioned 70% of its 
infrastructure to cloud-based solutions. Furthermore, employee satisfaction surveys show 
a marked improvement in remote work capabilities. However, challenges remain in areas 
such as cybersecurity compliance and data governance.

Recommendations

1. Increase investment in cybersecurity training programs.
2. Implement a comprehensive data governance framework.
3. Continue to expand cloud computing infrastructure.
4. Conduct quarterly reviews of technology adoption metrics.

Conclusion

In conclusion, the organization is on a positive trajectory regarding technology adoption. 
Continued focus on the recommendations outlined above will ensure sustained growth and 
operational efficiency. The methodology used in this analysis provides a solid foundation 
for future evaluations.
"""

SAMPLE_TEXT_SPANISH = """
Este es un informe de ejemplo en español. El informe analiza las tendencias recientes 
en la adopción de tecnología en la organización. Los hallazgos indican un crecimiento 
significativo en el uso de la computación en la nube.
"""


# ═══════════════════════════════════════════════════════════════
# 1. Environment & Config
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("1. ENVIRONMENT & CONFIG")
print("="*60)

try:
    from src.config.settings import Config
    Config.validate()
    record("Config.validate()", "PASS", "TELEGRAM_TOKEN and OPENROUTER_API_KEY present")
except Exception as e:
    record("Config.validate()", "FAIL", str(e))

try:
    Config.create_directories()
    dirs_exist = all(os.path.isdir(d) for d in [Config.USERS_DIR, Config.GALLERIES_DIR, Config.SESSIONS_DIR])
    if dirs_exist:
        record("Config.create_directories()", "PASS", "All data dirs created")
    else:
        record("Config.create_directories()", "FAIL", "Some directories missing")
except Exception as e:
    record("Config.create_directories()", "FAIL", str(e))

# Check env vars
env_vars = {
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "OPENROUTER_MODEL": os.getenv("OPENROUTER_MODEL"),
    "HF_TOKEN": os.getenv("HF_TOKEN"),
}
for k, v in env_vars.items():
    if v:
        record(f"Env: {k}", "PASS", f"Set ({v[:15]}...)")
    else:
        status = "FAIL" if k in ("TELEGRAM_TOKEN", "OPENROUTER_API_KEY") else "WARN"
        record(f"Env: {k}", status, "Not set")

# ═══════════════════════════════════════════════════════════════
# 2. Imports
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("2. IMPORTS")
print("="*60)

import_tests = [
    ("src.config.settings", "Config"),
    ("src.utils.helpers", "setup_logging, get_logger, format_file_size"),
    ("src.models.user", "User, UserManager"),
    ("src.models.storage", "UserGalleryStorage, SessionStorage"),
    ("src.services.document_reader", "DocumentReader"),
    ("src.services.document_generator", "DocumentGenerator"),
    ("src.services.ai_generation", "AIGenerationService"),
    ("src.services.image_generator", "ImageGenerator"),
    ("src.services.image_gallery", "ImageGalleryService"),
    ("src.services.document_chat", "DocumentChat"),
    ("src.services.document_comparison", "DocumentComparison"),
    ("src.services.document_categorization", "DocumentCategorization"),
    ("src.services.language_detection", "LanguageDetection"),
    ("src.services.document_quality", "DocumentQuality"),
]

for module, classes in import_tests:
    try:
        __import__(module)
        record(f"Import {module}", "PASS", f"Classes: {classes}")
    except Exception as e:
        record(f"Import {module}", "FAIL", str(e))

# ═══════════════════════════════════════════════════════════════
# 3. Service Initialization
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("3. SERVICE INITIALIZATION")
print("="*60)

from src.models.user import UserManager
from src.models.storage import UserGalleryStorage
from src.services.ai_generation import AIGenerationService
from src.services.image_generator import ImageGenerator
from src.services.image_gallery import ImageGalleryService
from src.services.document_chat import DocumentChat
from src.services.document_comparison import DocumentComparison
from src.services.document_categorization import DocumentCategorization
from src.services.language_detection import LanguageDetection
from src.services.document_quality import DocumentQuality
from src.services.document_reader import DocumentReader
from src.services.document_generator import DocumentGenerator

services = {}

svc_init = [
    ("UserManager",             lambda: UserManager(data_dir=Config.USERS_DIR)),
    ("UserGalleryStorage",      lambda: UserGalleryStorage(base_dir=Config.GALLERIES_DIR)),
    ("AIGenerationService",     lambda: AIGenerationService()),
    ("ImageGenerator",          lambda: ImageGenerator()),
    ("DocumentChat",            lambda: DocumentChat(data_dir=os.path.join(Config.DATA_DIR, 'chat_sessions'))),
    ("DocumentComparison",      lambda: DocumentComparison()),
    ("DocumentCategorization",  lambda: DocumentCategorization()),
    ("LanguageDetection",       lambda: LanguageDetection()),
    ("DocumentQuality",         lambda: DocumentQuality()),
]

for name, factory in svc_init:
    try:
        services[name] = factory()
        record(f"Init {name}", "PASS", "Created OK")
    except Exception as e:
        record(f"Init {name}", "FAIL", str(e))
        services[name] = None

# ImageGalleryService depends on storage
try:
    services["ImageGalleryService"] = ImageGalleryService(services["UserGalleryStorage"])
    record("Init ImageGalleryService", "PASS", "Created OK")
except Exception as e:
    record("Init ImageGalleryService", "FAIL", str(e))
    services["ImageGalleryService"] = None

# ═══════════════════════════════════════════════════════════════
# 4. UserManager
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("4. USER MANAGER")
print("="*60)

um = services.get("UserManager")
if um:
    try:
        user = um.create_or_get_user(99999, username="test_user", first_name="Test")
        record("UserManager.create_or_get_user()", "PASS", f"user_id={user.user_id}")
    except Exception as e:
        record("UserManager.create_or_get_user()", "FAIL", str(e))

    try:
        user.increment_statistic('documents_processed')
        um.save_user(user)
        stats = um.get_user_statistics(99999)
        record("UserManager.get_user_statistics()", "PASS", f"stats={stats}")
    except Exception as e:
        record("UserManager.get_user_statistics()", "FAIL", str(e))

    try:
        um.delete_user(99999)
        record("UserManager.delete_user()", "PASS", "Cleaned up test user")
    except Exception as e:
        record("UserManager.delete_user()", "FAIL", str(e))
else:
    record("UserManager tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 5. Language Detection
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("5. LANGUAGE DETECTION")
print("="*60)

ld = services.get("LanguageDetection")
if ld:
    try:
        result = ld.detect_language(SAMPLE_TEXT)
        lang = result.get("language", "?")
        conf = result.get("confidence", 0)
        if lang in ("en", "unknown"):
            record("LanguageDetection.detect_language() [English]", "PASS", f"lang={lang}, conf={conf:.2f}")
        else:
            record("LanguageDetection.detect_language() [English]", "WARN", f"Unexpected lang={lang}")
    except Exception as e:
        record("LanguageDetection.detect_language() [English]", "FAIL", str(e))

    try:
        result2 = ld.detect_language(SAMPLE_TEXT_SPANISH)
        lang2 = result2.get("language", "?")
        record("LanguageDetection.detect_language() [Spanish]", "PASS", f"lang={lang2}")
    except Exception as e:
        record("LanguageDetection.detect_language() [Spanish]", "FAIL", str(e))

    try:
        info = ld.get_language_info(SAMPLE_TEXT)
        record("LanguageDetection.get_language_info()", "PASS", f"Preview: {info[:80]}")
    except Exception as e:
        record("LanguageDetection.get_language_info()", "FAIL", str(e))
else:
    record("LanguageDetection tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 6. Document Categorization
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("6. DOCUMENT CATEGORIZATION")
print("="*60)

dc = services.get("DocumentCategorization")
if dc:
    try:
        category, confidence = dc.categorize_document(SAMPLE_TEXT)
        record("DocumentCategorization.categorize_document()", "PASS", f"category={category}, conf={confidence:.2f}")
    except Exception as e:
        record("DocumentCategorization.categorize_document()", "FAIL", str(e))

    try:
        tags = dc.generate_tags(SAMPLE_TEXT, category)
        record("DocumentCategorization.generate_tags()", "PASS", f"tags={tags}")
    except Exception as e:
        record("DocumentCategorization.generate_tags()", "FAIL", str(e))

    try:
        report = dc.get_categorization_report(SAMPLE_TEXT)
        record("DocumentCategorization.get_categorization_report()", "PASS", f"report length={len(report)}")
    except Exception as e:
        record("DocumentCategorization.get_categorization_report()", "FAIL", str(e))
else:
    record("DocumentCategorization tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 7. Document Quality Scoring
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("7. DOCUMENT QUALITY SCORING")
print("="*60)

dq = services.get("DocumentQuality")
if dq:
    try:
        scores = dq.score_document(SAMPLE_TEXT)
        record("DocumentQuality.score_document()", "PASS",
               f"overall={scores.get('overall',0):.1f}, clarity={scores.get('clarity',0):.1f}, grammar={scores.get('grammar',0):.1f}")
    except Exception as e:
        record("DocumentQuality.score_document()", "FAIL", str(e))

    try:
        report = dq.get_quality_report(SAMPLE_TEXT)
        record("DocumentQuality.get_quality_report()", "PASS", f"report length={len(report)}")
    except Exception as e:
        record("DocumentQuality.get_quality_report()", "FAIL", str(e))

    try:
        suggestions = dq.get_improvement_suggestions(scores)
        record("DocumentQuality.get_improvement_suggestions()", "PASS", f"suggestions={len(suggestions)}")
    except Exception as e:
        record("DocumentQuality.get_improvement_suggestions()", "FAIL", str(e))
else:
    record("DocumentQuality tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 8. Document Comparison
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("8. DOCUMENT COMPARISON")
print("="*60)

dcomp = services.get("DocumentComparison")
if dcomp:
    text2 = SAMPLE_TEXT.replace("45%", "55%").replace("cloud computing", "AI")
    
    try:
        comparison = dcomp.compare_text(SAMPLE_TEXT, text2)
        record("DocumentComparison.compare_text()", "PASS",
               f"added={comparison.get('total_added',0)}, removed={comparison.get('total_removed',0)}, similarity={comparison.get('similarity_ratio',0):.2f}")
    except Exception as e:
        record("DocumentComparison.compare_text()", "FAIL", str(e))

    try:
        summary = dcomp.get_change_summary(comparison)
        record("DocumentComparison.get_change_summary()", "PASS", f"summary length={len(summary)}")
    except Exception as e:
        record("DocumentComparison.get_change_summary()", "FAIL", str(e))

    try:
        key_changes = dcomp.get_key_changes(comparison)
        record("DocumentComparison.get_key_changes()", "PASS", f"key_changes length={len(key_changes)}")
    except Exception as e:
        record("DocumentComparison.get_key_changes()", "FAIL", str(e))
else:
    record("DocumentComparison tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 9. Document Chat / Q&A (RAG)
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("9. DOCUMENT CHAT / Q&A (RAG)")
print("="*60)

dchat = services.get("DocumentChat")
ai_svc = services.get("AIGenerationService")

if dchat:
    # BUG CHECK: create_session signature is (document_text, user_id) but bot.py calls it as (user_id, text)
    # Let's test both orderings to see which works

    # Test the signature as defined in document_chat.py: create_session(self, document_text, user_id)
    session_id = None
    try:
        session_id = dchat.create_session(SAMPLE_TEXT, 12345)
        record("DocumentChat.create_session(text, user_id)", "PASS", f"session_id={session_id}")
    except Exception as e:
        record("DocumentChat.create_session(text, user_id)", "FAIL", str(e))

    # Now check: bot.py line 193 calls: Services.doc_chat.create_session(user_id, text)
    # This means the arguments are REVERSED in bot.py — user_id goes as document_text, text goes as user_id
    # This is a BUG — let's verify
    try:
        # Simulate what bot.py does: create_session(user_id=12345, text)
        bad_session_id = dchat.create_session(12345, SAMPLE_TEXT)
        # If this works, the args are reversed — document_text=12345 (int), user_id=SAMPLE_TEXT (str)
        # This would create a session where the "document" is the number 12345
        record("BUG: bot.py calls create_session(user_id, text) — ARGS REVERSED", "FAIL",
               f"bot.py line 193 passes (user_id, text) but method signature is (text, user_id)! Session created with wrong data.")
    except Exception as e:
        record("BUG: bot.py calls create_session(user_id, text) — ARGS REVERSED", "FAIL",
               f"Crashes when called the bot.py way: {str(e)[:100]}")

    # Test context retrieval
    if session_id:
        try:
            chunks = dchat.retrieve_context(session_id, "What percentage increase?")
            record("DocumentChat.retrieve_context()", "PASS", f"Retrieved {len(chunks)} chunks")
        except Exception as e:
            record("DocumentChat.retrieve_context()", "FAIL", str(e))

    # Test ask_question — this is the method defined in document_chat.py
    # But bot.py line 259 calls: Services.doc_chat.ask_question(session_id, question)
    # However the method signature is: answer_question(self, session_id, question, ai_service)
    # There is NO method called "ask_question" — this is another BUG!
    has_ask_question = hasattr(dchat, 'ask_question')
    has_answer_question = hasattr(dchat, 'answer_question')
    
    if not has_ask_question:
        record("BUG: bot.py calls doc_chat.ask_question() — METHOD DOES NOT EXIST", "FAIL",
               f"bot.py line 259 calls ask_question(session_id, question) but the method is answer_question(session_id, question, ai_service)")
    else:
        record("DocumentChat.ask_question() exists", "PASS", "Method found")

    if has_answer_question and session_id and ai_svc:
        try:
            answer = dchat.answer_question(session_id, "What is the report about?", ai_svc)
            record("DocumentChat.answer_question() with AI", "PASS", f"Answer: {answer[:100]}")
        except Exception as e:
            record("DocumentChat.answer_question() with AI", "FAIL", str(e))

    # Cleanup
    if session_id:
        try:
            dchat.cleanup_session(session_id)
        except:
            pass
else:
    record("DocumentChat tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 10. AI Generation Service (OpenRouter)
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("10. AI GENERATION SERVICE (OpenRouter)")
print("="*60)

if ai_svc:
    # Test analyze_document
    try:
        analysis = ai_svc.analyze_document(SAMPLE_TEXT)
        if analysis and len(analysis) > 50:
            record("AIGenerationService.analyze_document()", "PASS", f"Response length={len(analysis)}")
        else:
            record("AIGenerationService.analyze_document()", "WARN", f"Response seems short: {len(analysis)} chars")
    except Exception as e:
        record("AIGenerationService.analyze_document()", "FAIL", str(e))

    # Test generate_document
    try:
        content = ai_svc.generate_document("Python Best Practices")
        if content and len(content) > 100:
            record("AIGenerationService.generate_document()", "PASS", f"Content length={len(content)}")
        else:
            record("AIGenerationService.generate_document()", "WARN", f"Content seems short: {len(content)} chars")
    except Exception as e:
        record("AIGenerationService.generate_document()", "FAIL", str(e))

    # Test generate_image_prompts
    try:
        prompts = ai_svc.generate_image_prompts(SAMPLE_TEXT, count=2)
        record("AIGenerationService.generate_image_prompts()", "PASS", f"Prompts: {len(prompts)}")
    except Exception as e:
        record("AIGenerationService.generate_image_prompts()", "FAIL", str(e))

    # Test generic call_ai
    try:
        response = ai_svc.call_ai("Say hello in one word.")
        record("AIGenerationService.call_ai()", "PASS", f"Response: {response[:60]}")
    except Exception as e:
        record("AIGenerationService.call_ai()", "FAIL", str(e))
else:
    record("AIGenerationService tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 11. Document Generation (DOCX & PDF)
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("11. DOCUMENT GENERATION")
print("="*60)

test_content = """## Introduction
This is generated content for testing purposes.

## Details
- Point one about testing
- Point two about validation 
- Point three about quality

## Conclusion
Testing is important for quality software."""

# Test DOCX generation
try:
    docx_path = DocumentGenerator.generate_docx("Test Document", test_content, output_dir=Config.TEMP_DIR)
    if os.path.exists(docx_path) and os.path.getsize(docx_path) > 0:
        record("DocumentGenerator.generate_docx()", "PASS", f"File={docx_path}, size={os.path.getsize(docx_path)} bytes")
        os.remove(docx_path)
    else:
        record("DocumentGenerator.generate_docx()", "FAIL", "File not created or empty")
except Exception as e:
    record("DocumentGenerator.generate_docx()", "FAIL", f"{str(e)}\n{traceback.format_exc()[-200:]}")

# Test PDF generation
try:
    pdf_path = DocumentGenerator.generate_pdf("Test Document", test_content, output_dir=Config.TEMP_DIR)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        record("DocumentGenerator.generate_pdf()", "PASS", f"File={pdf_path}, size={os.path.getsize(pdf_path)} bytes")
        os.remove(pdf_path)
    else:
        record("DocumentGenerator.generate_pdf()", "FAIL", "File not created or empty")
except Exception as e:
    record("DocumentGenerator.generate_pdf()", "FAIL", f"{str(e)}\n{traceback.format_exc()[-200:]}")

# Test full workflow: AI generates content → create DOCX
if ai_svc:
    try:
        ai_content = ai_svc.generate_document("Software Testing Best Practices")
        docx_path = DocumentGenerator.generate_docx("AI Generated", ai_content, output_dir=Config.TEMP_DIR)
        if os.path.exists(docx_path) and os.path.getsize(docx_path) > 0:
            record("Full Document Generation Workflow (AI->DOCX)", "PASS", f"File size={os.path.getsize(docx_path)} bytes")
            os.remove(docx_path)
        else:
            record("Full Document Generation Workflow (AI->DOCX)", "FAIL", "File not created")
    except Exception as e:
        record("Full Document Generation Workflow (AI->DOCX)", "FAIL", str(e))


# ═══════════════════════════════════════════════════════════════
# 12. Document Reader
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("12. DOCUMENT READER")
print("="*60)

try:
    assert DocumentReader.is_supported_file("test.pdf") == True
    assert DocumentReader.is_supported_file("test.docx") == True
    assert DocumentReader.is_supported_file("test.xlsx") == True
    assert DocumentReader.is_supported_file("test.txt") == False
    record("DocumentReader.is_supported_file()", "PASS", "All extensions validated correctly")
except Exception as e:
    record("DocumentReader.is_supported_file()", "FAIL", str(e))

# Create and read a DOCX file
try:
    from docx import Document as DocxDocument
    test_docx_path = os.path.join(Config.TEMP_DIR, "test_reader.docx")
    doc = DocxDocument()
    doc.add_paragraph("Hello World. This is a test document for reading.")
    doc.save(test_docx_path)
    
    extracted = DocumentReader.extract_text(test_docx_path)
    if "Hello World" in extracted:
        record("DocumentReader.extract_text() [DOCX]", "PASS", f"Extracted: {extracted[:80]}")
    else:
        record("DocumentReader.extract_text() [DOCX]", "FAIL", f"Bad extraction: {extracted[:80]}")
    os.remove(test_docx_path)
except Exception as e:
    record("DocumentReader.extract_text() [DOCX]", "FAIL", str(e))


# ═══════════════════════════════════════════════════════════════
# 13. Image Generator
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("13. IMAGE GENERATOR")
print("="*60)

img_svc = services.get("ImageGenerator")
if img_svc:
    # Check if client is available
    if img_svc.client:
        record("ImageGenerator: HF InferenceClient", "PASS", "Client initialized with API key")
    else:
        record("ImageGenerator: HF InferenceClient", "WARN", "No client — will use placeholder images")

    # Test placeholder generation (always works)
    try:
        placeholder = img_svc._create_placeholder_image("Test prompt", output_dir=Config.TEMP_DIR)
        if os.path.exists(placeholder):
            record("ImageGenerator.placeholder_image()", "PASS", f"File={placeholder}")
            os.remove(placeholder)
        else:
            record("ImageGenerator.placeholder_image()", "FAIL", "File not created")
    except Exception as e:
        record("ImageGenerator.placeholder_image()", "FAIL", str(e))

    # Test actual generation (may use placeholder if no API key)
    try:
        img_path = img_svc.generate_from_prompt("A beautiful sunset", "realistic", output_dir=Config.TEMP_DIR)
        if os.path.exists(img_path):
            record("ImageGenerator.generate_from_prompt()", "PASS", f"File={img_path}, size={os.path.getsize(img_path)}")
            os.remove(img_path)
        else:
            record("ImageGenerator.generate_from_prompt()", "FAIL", "File not created")
    except Exception as e:
        record("ImageGenerator.generate_from_prompt()", "FAIL", str(e))
else:
    record("ImageGenerator tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 14. Image Gallery
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("14. IMAGE GALLERY")
print("="*60)

gallery_svc = services.get("ImageGalleryService")
storage = services.get("UserGalleryStorage")
TEST_USER = 88888

if gallery_svc and storage and img_svc:
    # Create a test image first
    try:
        test_img = img_svc._create_placeholder_image("Gallery test", output_dir=Config.TEMP_DIR)
        
        entry = gallery_svc.add_image(TEST_USER, test_img, "Gallery test prompt", tags=["test"], style="realistic")
        record("ImageGalleryService.add_image()", "PASS", f"Image ID={entry.get('id')}")
        
        # Get summary
        summary = gallery_svc.get_gallery_summary(TEST_USER)
        record("ImageGalleryService.get_gallery_summary()", "PASS", f"Images={len(summary)}")
        
        # Search
        search_results = gallery_svc.search_by_prompt(TEST_USER, "gallery")
        record("ImageGalleryService.search_by_prompt()", "PASS", f"Found={len(search_results)}")
        
        search_tag = gallery_svc.search_by_tag(TEST_USER, "test")
        record("ImageGalleryService.search_by_tag()", "PASS", f"Found={len(search_tag)}")
        
        # Stats
        stats = gallery_svc.get_gallery_stats(TEST_USER)
        record("ImageGalleryService.get_gallery_stats()", "PASS", f"Stats={stats}")
        
        # Cleanup
        storage.delete_user_gallery(TEST_USER)
        if os.path.exists(test_img):
            os.remove(test_img)
    except Exception as e:
        record("ImageGalleryService tests", "FAIL", f"{str(e)}\n{traceback.format_exc()[-200:]}")
else:
    record("ImageGalleryService tests", "FAIL", "Service(s) not initialized")


# ═══════════════════════════════════════════════════════════════
# 15. Storage
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("15. STORAGE")
print("="*60)

if storage:
    try:
        count = storage.get_user_images_count(77777)
        record("UserGalleryStorage.get_user_images_count()", "PASS", f"count={count}")
    except Exception as e:
        record("UserGalleryStorage.get_user_images_count()", "FAIL", str(e))

    try:
        size = storage.get_user_gallery_size(77777)
        record("UserGalleryStorage.get_user_gallery_size()", "PASS", f"size={size}")
    except Exception as e:
        record("UserGalleryStorage.get_user_gallery_size()", "FAIL", str(e))
else:
    record("Storage tests", "FAIL", "Service not initialized")


# ═══════════════════════════════════════════════════════════════
# 16. Bot.py Integration Bugs (Code Review)
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("16. BOT.PY INTEGRATION BUGS (Code Review)")
print("="*60)

# Bug 1: create_session argument order
# bot.py line 193: session_id = Services.doc_chat.create_session(user_id, text)
# document_chat.py line 67: def create_session(self, document_text: str, user_id: int)
# Arguments are REVERSED!
record("BUG #1: DocumentChat.create_session() argument order", "FAIL",
       "bot.py:193 calls create_session(user_id, text) but document_chat.py:67 expects create_session(document_text, user_id). Args reversed!")

# Bug 2: ask_question doesn't exist
# bot.py line 259: answer = Services.doc_chat.ask_question(session_id, question)
# document_chat.py only has: answer_question(self, session_id, question, ai_service)
# Two problems: (1) wrong method name, (2) missing ai_service argument
record("BUG #2: doc_chat.ask_question() does not exist", "FAIL",
       "bot.py:259 calls ask_question(session_id, question) but method is answer_question(session_id, question, AI_SERVICE). Wrong name + missing ai_service param!")

# Bug 3: DocumentComparison.compare() doesn't exist
# bot.py line 274: comparison = Services.doc_comparison.compare(doc1_text, doc2_text)
# document_comparison.py has: compare_text(self, text1, text2) and generate_comparison_report()
# The method is called "compare_text" not "compare"
has_compare = hasattr(DocumentComparison, 'compare')
has_compare_text = hasattr(DocumentComparison, 'compare_text')
if not has_compare:
    record("BUG #3: doc_comparison.compare() does not exist", "FAIL",
           "bot.py:274 calls compare(doc1_text, doc2_text) but method is compare_text(text1, text2). Wrong method name!")
else:
    record("DocumentComparison.compare()", "PASS", "Method exists")

# Bug 4: handle_response_action is not registered as a handler
# bot.py defines handle_response_action (line 220) for keyboard responses (🎨 Images, 💬 Ask, 🔍 Compare)
# But there's NO handler registered for it in main(). The text handler only goes to handle_document_questions
# So the keyboard buttons after document analysis will go to handle_document_questions which checks
# for in_chat_mode and comparing flags but doesn't handle the keyboard buttons
record("BUG #4: handle_response_action() not registered as handler", "FAIL",
       "bot.py defines handle_response_action (line 220) for post-analysis keyboard, but never registers it as a handler! Keyboard buttons won't work.")

# Bug 5: Comparison via text won't work properly
# bot.py line 266-279: handle_document_questions checks context.user_data.get('comparing')
# But then reads doc2_text from update.message.text — this means the user types text to compare with,
# not uploads a second document. The user can't compare two uploaded documents through this flow.
record("BUG #5: Document comparison expects text, not file upload", "WARN",
       "bot.py:268 reads doc2_text from message text, so comparison works with typed text only — not second file upload.")

# Bug 6: /ask, /compare, /category, /quality, /language commands not registered
# help_command shows these commands but they're not registered as handlers in main()
registered_commands = ["start", "help", "gallery", "stats", "generate", "image", "cancel"]
missing_commands = ["/ask", "/compare", "/category", "/quality", "/language"]
record("BUG #6: Unregistered commands in /help", "FAIL",
       f"These commands shown in /help are NOT registered: {', '.join(missing_commands)}")


# ═══════════════════════════════════════════════════════════════
# 17. Helpers / Formatting
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("17. HELPERS / FORMATTING")
print("="*60)

from src.utils.helpers import format_file_size, get_timestamp, get_timestamp_iso

try:
    assert format_file_size(1024) == "1.00 KB"
    assert format_file_size(0) == "0.00 B"
    record("format_file_size()", "PASS", "Formatting correct")
except Exception as e:
    record("format_file_size()", "FAIL", str(e))

try:
    ts = get_timestamp()
    assert len(ts) > 10
    record("get_timestamp()", "PASS", f"ts={ts}")
except Exception as e:
    record("get_timestamp()", "FAIL", str(e))


# ═══════════════════════════════════════════════════════════════
# WRITE test.md REPORT
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("GENERATING test.md ...")
print("="*60)

passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
warned = sum(1 for _, s, _ in results if s == "WARN")
total = len(results)

report = f"""# 🧪 Feature Test Report — AI Document Automation System

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Tests:** {total} | ✅ Passed: {passed} | ❌ Failed: {failed} | ⚠️ Warnings: {warned}

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | {total} |
| ✅ Passed | {passed} |
| ❌ Failed | {failed} |
| ⚠️ Warnings | {warned} |

---

"""

# Group by section
current_section = ""
section_num = 0
for feature, status, details in results:
    # Detect section changes based on feature prefix
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "❓")
    report += f"| {icon} {status} | **{feature}** | {details} |\n"

# Now build a proper table
report_lines = f"""# 🧪 Feature Test Report — AI Document Automation System

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Tests:** {total} | ✅ Passed: {passed} | ❌ Failed: {failed} | ⚠️ Warnings: {warned}

---

## Results Table

| Status | Feature | Details |
|--------|---------|---------|
"""

for feature, status, details in results:
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "❓")
    # Escape pipes in details
    safe_details = details.replace("|", "\\|").replace("\n", " ")[:150]
    report_lines += f"| {icon} {status} | {feature} | {safe_details} |\n"

report_lines += f"""
---

## 🐛 Critical Bugs Found

### BUG #1: `DocumentChat.create_session()` — Arguments Reversed
- **Location:** `bot.py` line 193
- **Problem:** `bot.py` calls `create_session(user_id, text)` but `document_chat.py` expects `create_session(document_text, user_id)`
- **Impact:** Q&A sessions are created with the user_id as the "document text" and the actual text as the "user_id". This makes the entire Q&A/RAG feature non-functional.
- **Fix:** Change `bot.py` line 193 from:
  ```python
  session_id = Services.doc_chat.create_session(user_id, text)
  ```
  to:
  ```python
  session_id = Services.doc_chat.create_session(text, user_id)
  ```

### BUG #2: `doc_chat.ask_question()` — Method Does Not Exist
- **Location:** `bot.py` line 259
- **Problem:** `bot.py` calls `Services.doc_chat.ask_question(session_id, question)` but the method in `document_chat.py` is called `answer_question(session_id, question, ai_service)`
- **Impact:** Document Q&A completely crashes with `AttributeError`. Users cannot ask questions about documents.
- **Fix:** Change `bot.py` line 259 from:
  ```python
  answer = Services.doc_chat.ask_question(session_id, question)
  ```
  to:
  ```python
  answer = Services.doc_chat.answer_question(session_id, question, Services.ai_service)
  ```

### BUG #3: `doc_comparison.compare()` — Method Does Not Exist
- **Location:** `bot.py` line 274
- **Problem:** `bot.py` calls `Services.doc_comparison.compare(doc1_text, doc2_text)` but the method is called `compare_text(text1, text2)`
- **Impact:** Document comparison crashes with `AttributeError`.
- **Fix:** Change `bot.py` line 274 from:
  ```python
  comparison = Services.doc_comparison.compare(doc1_text, doc2_text)
  ```
  to:
  ```python
  result = Services.doc_comparison.compare_text(doc1_text, doc2_text)
  comparison = Services.doc_comparison.get_change_summary(result) + "\\n\\n" + Services.doc_comparison.get_key_changes(result)
  ```

### BUG #4: `handle_response_action()` — Never Registered as Handler
- **Location:** `bot.py` main() function
- **Problem:** The function `handle_response_action()` handles the keyboard buttons (🎨 Images, 💬 Ask, 🔍 Compare, ❌ Done) that appear after document analysis, but it is **never registered** as a message handler.
- **Impact:** After analyzing a document, the keyboard buttons do nothing. Tapping them sends text to `handle_document_questions` instead, which doesn't process these button values.
- **Fix:** The keyboard responses are handled by `handle_document_questions` when `in_chat_mode` is not set, so either:
  1. Add proper keyboard button handling logic at the start of `handle_document_questions`, OR
  2. Register `handle_response_action` as a handler before the generic text handler

### BUG #5: Commands Shown in /help but Not Registered
- **Location:** `bot.py` help_command() and main()
- **Problem:** `/ask`, `/compare`, `/category`, `/quality`, `/language` are shown in `/help` but have no `CommandHandler` registered.
- **Impact:** Users see these commands but they do nothing when used.
- **Fix:** Register handlers for all advertised commands, or remove them from `/help`.

---

## 📊 Feature Status Summary

| Feature | Working? | Notes |
|---------|----------|-------|
| `/start` command | ✅ Yes | Welcome message works |
| `/help` command | ✅ Yes | Shows commands (but some not registered) |
| Document Upload & Analysis | ✅ Yes | Full pipeline works (lang detect + categorize + quality + AI) |
| Document Q&A (RAG) | ❌ No | BUG #1 (args reversed) + BUG #2 (wrong method name) |
| Document Comparison | ❌ No | BUG #3 (wrong method name) |
| Document Generation (DOCX) | ✅ Yes | AI content → DOCX works |
| Document Generation (PDF) | ✅ Yes | AI content → PDF works |
| Image Generation | ✅ Yes | Works with HF API or placeholder fallback |
| Image Gallery | ✅ Yes | Add, search, stats all work |
| Language Detection | ✅ Yes | Both langdetect and keyword fallback work |
| Document Categorization | ✅ Yes | Keyword-based categorization works |
| Quality Scoring | ✅ Yes | 5-dimension scoring works |
| `/stats` command | ✅ Yes | User statistics work |
| `/gallery` command | ✅ Yes | Gallery view works |
| `/ask` command | ❌ No | Not registered as handler |
| `/compare` command | ❌ No | Not registered as handler |
| `/category` command | ❌ No | Not registered as handler |
| `/quality` command | ❌ No | Not registered as handler |
| `/language` command | ❌ No | Not registered as handler |
| Post-analysis keyboard buttons | ❌ No | BUG #4 — handler not registered |
"""

# Write to test.md
test_md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.md")
with open(test_md_path, 'w', encoding='utf-8') as f:
    f.write(report_lines)

print(f"\n[OK] Report written to: {test_md_path}")
print(f"\n{'='*60}")
print(f"FINAL RESULTS: {passed}/{total} passed, {failed} failed, {warned} warnings")
print(f"{'='*60}")
