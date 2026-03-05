#!/bin/bash
# HireMate AI - Render Deployment Script

echo "🚀 Deploying HireMate AI to Render..."
echo ""

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found."
    echo "Please install from: https://docs.render.com/cli"
    echo "Or deploy manually through the Render dashboard"
    exit 1
fi

# This would require Render CLI setup
echo "📋 To deploy on Render:"
echo "1. Go to https://render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repo: https://github.com/Vivitha269/Hiremate_AI"
echo "4. Configure build settings:"
echo "   - Runtime: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python -m uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "5. Add environment variables:"
echo "   - GEMINI_API_KEY: your_api_key_here"
echo "   - ENVIRONMENT: production"
echo ""

echo "✅ Ready for manual deployment on Render dashboard!"