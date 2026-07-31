#!/bin/bash
# Africa Rising Framework Setup (Linux/Mac)

set -e

echo "======================================"
echo "Africa Rising Framework Setup"
echo "======================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "✓ Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create directory structure
echo "✓ Creating directory structure..."
mkdir -p output/logs
mkdir -p output/cache
mkdir -p output/projects
mkdir -p cache/narration
mkdir -p cache/visuals
mkdir -p cache/captions
mkdir -p cache/assets
mkdir -p prompts

# Initialize prompt library
echo "✓ Initializing prompt library..."
python3 << 'EOF'
from core.prompt_manager import initialize_prompt_library
initialize_prompt_library()
print("Prompts initialized")
EOF

# Check FFmpeg installation
echo "✓ Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not installed. Install with:"
    echo "   macOS: brew install ffmpeg"
    echo "   Linux: apt-get install ffmpeg"
    exit 1
fi
ffmpeg -version | head -1

# Check Whisper installation
echo "✓ Checking Whisper..."
if ! command -v whisper &> /dev/null; then
    echo "⚠️  Whisper not installed. Installing..."
    pip install openai-whisper
fi
whisper --version

# Setup environment variables
echo "✓ Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Africa Rising Framework Configuration
export ANTHROPIC_API_KEY="your_key_here"
export ELEVENLABS_API_KEY="your_key_here"
export PEXELS_API_KEY="your_key_here"
export TAVILY_API_KEY="your_key_here"
export GROK_API_KEY="your_key_here"
export GOOGLE_API_KEY="your_key_here"
export RUNWAY_API_KEY="your_key_here"
EOF
    echo "⚠️  Created .env file - update with your API keys"
else
    echo "✓ .env already exists"
fi

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Test basic imports
echo "✓ Testing imports..."
python3 << 'EOF'
try:
    from agents.base_agent import BaseAgent
    from core.schemas import Shot, Asset, Timeline
    from core.prompt_manager import PromptManager
    from core.license_manager import LicenseManager
    from core.advanced_qa import AdvancedQAChecker
    from core.observability import ProductionLogger
    print("✓ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF

# Final summary
echo ""
echo "======================================"
echo "✓ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Run: python3 pipeline.py --help"
echo "3. Check config.yaml for settings"
echo ""
echo "Documentation:"
echo "- README.md - Overview"
echo "- ARCHITECTURE.md - System design"
echo "- QUICKSTART.md - Getting started"
echo ""
