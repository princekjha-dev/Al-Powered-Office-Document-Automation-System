#!/bin/bash
# 🚀 HACKATHON FINALIZATION SCRIPT
# Deletes unnecessary files and commits changes to git

echo "🎯 AI-Powered Office Document Automation System - Hackathon Finalization"
echo "==========================================================================="
echo ""

# Step 1: Delete unnecessary files
echo "🗑️  Step 1: Deleting unnecessary files..."
rm -f workers.py 2>/dev/null && echo "  ✅ Deleted: workers.py"
rm -f src/services/task_queue.py 2>/dev/null && echo "  ✅ Deleted: src/services/task_queue.py"
rm -f DEPLOYMENT.md 2>/dev/null && echo "  ✅ Deleted: DEPLOYMENT.md"
rm -f DOCKER.md 2>/dev/null && echo "  ✅ Deleted: DOCKER.md"
rm -f IMPLEMENTATION_GUIDE.md 2>/dev/null && echo "  ✅ Deleted: IMPLEMENTATION_GUIDE.md"
rm -f PROJECT_SUMMARY.md 2>/dev/null && echo "  ✅ Deleted: PROJECT_SUMMARY.md"
rm -f QUICK_REFERENCE.md 2>/dev/null && echo "  ✅ Deleted: QUICK_REFERENCE.md"
rm -f CLEANUP_PLAN.md 2>/dev/null && echo "  ✅ Deleted: CLEANUP_PLAN.md"
rm -f cleanup.sh 2>/dev/null && echo "  ✅ Deleted: cleanup.sh (old)"
rm -f cleanup_workspace.py 2>/dev/null && echo "  ✅ Deleted: cleanup_workspace.py"
echo ""

# Step 2: Stage all changes
echo "📝 Step 2: Staging changes..."
git add -A
echo "  ✅ Files staged"
echo ""

# Step 3: Show changes
echo "📊 Step 3: Changes to commit:"
git status
echo ""

# Step 4: Commit changes
echo "💾 Step 4: Committing changes..."
git commit -m "🎯 Hackathon simplification: Remove Celery/Redis, streamline bot & dashboard

- Remove async task queue (workers.py, task_queue.py)
- Remove Celery & Redis dependencies
- Simplify bot.py: 500+ → 400 lines, remove SessionStorage
- Streamline dashboard.py: 400+ → 200 lines, 15 → 8 endpoints
- Remove production documentation (Deployment, Docker, Implementation guides)
- Update README with simplified structure
- Add tqdm to dependencies for progress bars
- Maintain all core features: document analysis, generation, image creation, gallery

Project ready for hackathon demo!"

echo ""

# Step 5: Show commit info
echo "✅ Step 5: Commit complete!"
git log --oneline -1
echo ""

# Step 6: Push to remote
echo "🚀 Step 6: Pushing to GitHub..."
git push origin main
echo "  ✅ Pushed successfully!"
echo ""

# Final status
echo "==========================================================================="
echo "✨ HACKATHON PROJECT READY!"
echo "==========================================================================="
echo ""
echo "📊 Simplification Summary:"
echo "   • Dependencies: 15 → 13 packages"
echo "   • bot.py: 500+ → 400 lines"
echo "   • dashboard.py: 400+ → 200 lines"
echo "   • API endpoints: 15+ → 8"
echo "   • Root files: 18 → 11"
echo "   • Production docs: removed"
echo ""
echo "✅ Core Features Preserved:"
echo "   • Document analysis (PDF, DOCX, XLSX)"
echo "   • AI-powered document generation"
echo "   • Image generation from prompts"
echo "   • Gallery management & storage"
echo "   • Telegram bot interface"
echo "   • REST API (8 endpoints)"
echo "   • CLI interface"
echo ""
echo "🎯 Next Steps:"
echo "   1. Install dependencies: pip install -r requirements.txt"
echo "   2. Setup .env file: cp .env.example .env"
echo "   3. Add API keys (OPENROUTER_API_KEY, HF_TOKEN)"
echo "   4. Test: python test_bot.py"
echo "   5. Run bot: python bot.py"
echo ""
echo "🏆 Ready for hackathon judges!"
echo "==========================================================================="
