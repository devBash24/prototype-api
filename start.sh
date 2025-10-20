#!/bin/bash

# Plant Care API Startup Script for Production

echo "🌱 Starting Plant Care API..."

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "🚀 Starting application..."
python main.py
