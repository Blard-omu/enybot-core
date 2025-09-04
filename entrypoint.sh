#!/bin/bash
set -e

echo "🚀 AI Student Support Service - Starting..."
echo "============================================"

# Create necessary directories (for runtime data)
mkdir -p ./chroma_db ./logs

# Start the service
echo "🚀 Starting AI Student Support Service..."
exec python main.py
