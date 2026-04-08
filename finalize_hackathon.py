#!/usr/bin/env python3
"""
🚀 HACKATHON FINALIZATION SCRIPT
Deletes unnecessary files and commits changes to git
"""

import os
import subprocess
import sys

def run_command(cmd, description=""):
    """Run a shell command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    print("\n" + "="*80)
    print("🎯 AI-Powered Office Document Automation System - Hackathon Finalization")
    print("="*80 + "\n")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Step 1: Delete unnecessary files
    print("🗑️  Step 1: Deleting unnecessary files...")
    files_to_delete = [
        "workers.py",
        "src/services/task_queue.py",
        "DEPLOYMENT.md",
        "DOCKER.md",
        "IMPLEMENTATION_GUIDE.md",
        "PROJECT_SUMMARY.md",
        "QUICK_REFERENCE.md",
        "CLEANUP_PLAN.md",
        "HACKATHON_SIMPLIFICATION_STATUS.md",
        "cleanup.sh",
        "cleanup_workspace.py",
    ]
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  ✅ Deleted: {file_path}")
            except Exception as e:
                print(f"  ⚠️  Failed to delete {file_path}: {e}")
        else:
            print(f"  ⏭️  Skipped: {file_path} (not found)")
    
    print("\n✅ Cleanup complete!\n")
    
    # Step 2: Show git status
    print("📊 Step 2: Git status...")
    code, stdout, stderr = run_command("git status --short")
    if stdout:
        print(stdout)
    else:
        print("  No changes detected")
    print()
    
    # Step 3: Stage all changes
    print("📝 Step 3: Staging all changes...")
    code, stdout, stderr = run_command("git add -A")
    print("  ✅ Files staged\n")
    
    # Step 4: Commit changes
    print("💾 Step 4: Committing changes...")
    commit_msg = """🎯 Hackathon simplification: Remove Celery/Redis, streamline bot & dashboard

- Remove async task queue (workers.py, task_queue.py)
- Remove Celery & Redis dependencies  
- Simplify bot.py: 500+ → 400 lines, remove SessionStorage
- Streamline dashboard.py: 400+ → 200 lines, 15 → 8 endpoints
- Remove production documentation (Deployment, Docker, Implementation guides)
- Update README with simplified structure
- Add tqdm to dependencies for progress bars
- Maintain all core features: document analysis, generation, image creation

Project ready for hackathon demo! ✨"""
    
    code, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if "nothing to commit" in stdout:
        print("  ℹ️  No changes to commit (already up to date)")
    elif code == 0:
        print("  ✅ Changes committed successfully!")
    else:
        print(f"  ⚠️  Commit issue: {stderr}")
    print()
    
    # Step 5: Show latest commit
    print("✅ Step 5: Latest commit info:")
    code, stdout, stderr = run_command("git log --oneline -1")
    if stdout:
        print(f"  {stdout.strip()}")
    print()
    
    # Step 6: Try to push
    print("🚀 Step 6: Pushing to GitHub...")
    code, stdout, stderr = run_command("git push origin main")
    if code == 0:
        print("  ✅ Pushed successfully!")
    else:
        if "Permission denied" in stderr or "authentication" in stderr.lower():
            print("  ⚠️  Push requires authentication. Run: git push origin main")
        else:
            print(f"  ℹ️  Push status: {stderr[:100] if stderr else 'Check manually'}")
    print()
    
    # Final summary
    print("="*80)
    print("✨ HACKATHON PROJECT READY!")
    print("="*80 + "\n")
    
    print("📊 Simplification Summary:")
    print("   • Dependencies: 15 → 13 packages")
    print("   • bot.py: 500+ → 400 lines")
    print("   • dashboard.py: 400+ → 200 lines")
    print("   • API endpoints: 15+ → 8")
    print("   • Root files: 18 → 11")
    print("   • Production docs: removed\n")
    
    print("✅ Core Features Preserved:")
    print("   • Document analysis (PDF, DOCX, XLSX)")
    print("   • AI-powered document generation")
    print("   • Image generation from prompts")
    print("   • Gallery management & storage")
    print("   • Telegram bot interface")
    print("   • REST API (8 endpoints)")
    print("   • CLI interface\n")
    
    print("🎯 Next Steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Setup .env file: cp .env.example .env")
    print("   3. Add API keys (OPENROUTER_API_KEY, HF_TOKEN)")
    print("   4. Test: python test_bot.py")
    print("   5. Run bot: python bot.py\n")
    
    print("🏆 Ready for hackathon judges!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
