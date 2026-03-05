#!/bin/bash
# HireMate AI - Railway Deployment Script

echo "🚀 Deploying HireMate AI to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Logging into Railway..."
railway login

# Link project (if not already linked)
echo "🔗 Linking project..."
railway link

# Set environment variables
echo "⚙️ Setting environment variables..."
echo "Enter your Google Gemini API Key:"
read -s GEMINI_API_KEY

railway variables set GEMINI_API_KEY=$GEMINI_API_KEY
railway variables set ENVIRONMENT=production

# Deploy
echo "🚀 Deploying..."
railway up

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your app will be available at the URL shown above"
echo ""
echo "📝 Don't forget to:"
echo "   - Set up a custom domain (optional)"
echo "   - Configure monitoring (optional)"
echo "   - Update your README with the live URL"