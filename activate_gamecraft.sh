#!/bin/bash
# Activate GameCraft Environment

echo "🎮 Activating Hunyuan-GameCraft Environment..."

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate HYGameCraft

# Load environment variables
if [ -f "gamecraft_integration/.env" ]; then
    export $(grep -v '^#' gamecraft_integration/.env | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️ Environment file not found"
fi

# Set Python path
export PYTHONPATH="${GAMECRAFT_PATH}:${PYTHONPATH}"

echo "🚀 GameCraft environment ready!"
echo "💡 Available commands:"
echo "  - python gamecraft_integration/pipeline_manager.py --help"
echo "  - python gamecraft_integration/gamecraft_runner.py"
echo "📁 Project root: $(pwd)"
echo "🎮 GameCraft path: $GAMECRAFT_PATH"

# Create alias for easy pipeline access
alias gamecraft-pipeline="python gamecraft_integration/pipeline_manager.py"
alias gamecraft-test="python -c 'from gamecraft_integration import GameCraftRunner; print(\"GameCraft integration working!\")'"

echo "🎯 Ready to create worlds! Try: gamecraft-test"
