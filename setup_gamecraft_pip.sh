#!/bin/bash
# Setup Hunyuan-GameCraft-1.0 Environment using pip and venv
# Alternative setup for systems without conda

PROJECT_ROOT="/Volumes/Jul_23_2025/LevlStudio_Project"
GAMECRAFT_DIR="$PROJECT_ROOT/Hunyuan-GameCraft-1.0"
VENV_DIR="$PROJECT_ROOT/gamecraft_venv"

echo "🎮 Setting up Hunyuan-GameCraft-1.0 Environment (pip version)..."

cd "$PROJECT_ROOT"

# Check if GameCraft is already cloned
if [ ! -d "$GAMECRAFT_DIR" ]; then
    echo "❌ GameCraft directory not found. Please run this from LevlStudio project root."
    exit 1
fi

echo "📁 Found GameCraft directory: $GAMECRAFT_DIR"

# Create Python virtual environment
echo "🐍 Creating Python virtual environment: $VENV_DIR..."
python3 -m venv "$VENV_DIR"

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with Metal support for macOS
echo "🔥 Installing PyTorch with Metal support..."
pip install torch torchvision torchaudio

# Install GameCraft requirements
echo "📦 Installing GameCraft requirements..."
cd "$GAMECRAFT_DIR"
pip install -r requirements.txt

# Install additional dependencies for LevlStudio integration
echo "🔧 Installing additional dependencies for LevlStudio integration..."
pip install opencv-python-headless
pip install mediapipe
pip install open3d
pip install trimesh
pip install scikit-image
pip install transformers
pip install diffusers
pip install accelerate

# Install HuggingFace CLI
echo "📥 Installing HuggingFace CLI..."
pip install "huggingface_hub[cli]"

# Return to project root
cd "$PROJECT_ROOT"

# Check if weights directory exists and download models
WEIGHTS_DIR="$GAMECRAFT_DIR/weights"
if [ ! -d "$WEIGHTS_DIR" ]; then
    echo "📥 Creating weights directory..."
    mkdir -p "$WEIGHTS_DIR"
fi

# Download models if not present
MODEL_FILE="$WEIGHTS_DIR/gamecraft_models/mp_rank_00_model_states.pt"
if [ ! -f "$MODEL_FILE" ]; then
    echo "📥 Downloading GameCraft models (this may take a while)..."
    
    cd "$WEIGHTS_DIR"
    echo "🚀 Downloading from HuggingFace (10 minutes to 1 hour depending on connection)..."
    
    # Try to download the models
    if huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./; then
        echo "✅ Models downloaded successfully!"
    else
        echo "❌ Model download failed. You may need to download manually."
        echo "📝 Manual download instructions:"
        echo "   1. cd $WEIGHTS_DIR"
        echo "   2. huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./"
        echo "   3. Or download from https://huggingface.co/tencent/Hunyuan-GameCraft-1.0"
    fi
else
    echo "✅ GameCraft models already present"
fi

# Return to project root
cd "$PROJECT_ROOT"

# Create GameCraft integration environment file
echo "📝 Creating environment configuration..."
cat > gamecraft_integration/.env << EOF
# GameCraft Environment Configuration
GAMECRAFT_PATH=$GAMECRAFT_DIR
WEIGHTS_PATH=$WEIGHTS_DIR
VENV_PATH=$VENV_DIR
MODEL_BASE=$WEIGHTS_DIR/stdmodels
CHECKPOINT_PATH=$WEIGHTS_DIR/gamecraft_models/mp_rank_00_model_states.pt
CHECKPOINT_DISTILL_PATH=$WEIGHTS_DIR/gamecraft_models/mp_rank_00_model_states_distill.pt

# Output directories
OUTPUT_BASE=$PROJECT_ROOT/gamecraft_outputs
VIDEO_OUTPUT=$PROJECT_ROOT/gamecraft_outputs/videos
ANALYSIS_OUTPUT=$PROJECT_ROOT/gamecraft_outputs/analysis
UNREAL_OUTPUT=$PROJECT_ROOT/gamecraft_outputs/unreal_assets

# Processing settings
DEFAULT_VIDEO_SIZE=704,1216
DEFAULT_FPS=25
DEFAULT_CFG_SCALE=2.0
DEFAULT_INFERENCE_STEPS=50

# Device settings (Metal for macOS)
PYTORCH_ENABLE_MPS_FALLBACK=1
USE_FP8=false
USE_DISTILL=false
EOF

# Create activation script
echo "📝 Creating GameCraft activation script..."
cat > activate_gamecraft.sh << EOF
#!/bin/bash
# Activate GameCraft Environment (pip version)

echo "🎮 Activating Hunyuan-GameCraft Environment..."

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Load environment variables
if [ -f "gamecraft_integration/.env" ]; then
    export \$(grep -v '^#' gamecraft_integration/.env | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️ Environment file not found"
fi

# Set Python path
export PYTHONPATH="\${GAMECRAFT_PATH}:\${PYTHONPATH}"

# Enable Metal acceleration for PyTorch on macOS
export PYTORCH_ENABLE_MPS_FALLBACK=1

echo "🚀 GameCraft environment ready!"
echo "💡 Available commands:"
echo "  - python3 gamecraft_integration/pipeline_manager.py --help"
echo "  - python3 demo_gamecraft.py --show-presets"
echo "📁 Project root: \$(pwd)"
echo "🎮 GameCraft path: \$GAMECRAFT_PATH"

# Create alias for easy pipeline access
alias gamecraft-pipeline="python3 -m gamecraft_integration.pipeline_manager"
alias gamecraft-demo="python3 demo_gamecraft.py"
alias gamecraft-test="python3 test_gamecraft_integration.py"

echo "🎯 Ready to create worlds! Try: gamecraft-test"
EOF

chmod +x activate_gamecraft.sh

# Test installation
echo "🧪 Testing GameCraft installation..."
source "$VENV_DIR/bin/activate"

python3 << EOF
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    
    # Check Metal availability on macOS
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print("✅ Metal Performance Shaders (MPS) available")
    else:
        print("⚠️ MPS not available, will use CPU")
    
    import transformers
    print(f"✅ Transformers: {transformers.__version__}")
    
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
    
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
    
    # Test basic imports from our integration
    import sys
    sys.path.append('$PROJECT_ROOT')
    
    print("✅ GameCraft environment setup complete!")
    print("🎉 All dependencies installed successfully!")
    
except Exception as e:
    print(f"❌ Setup test failed: {e}")
    print("🔧 You may need to install missing dependencies manually")
    
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 GameCraft Environment Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "1. Activate environment: source activate_gamecraft.sh"
echo "2. Test integration: gamecraft-test"
echo "3. Show presets: gamecraft-demo --show-presets"
echo "4. Generate world: python3 demo_gamecraft.py --show-examples"
echo ""
echo "🛠️ Available tools:"
echo "  - GameCraft world generation"
echo "  - Video processing and analysis"
echo "  - Metal-accelerated PyTorch"
echo ""
echo "📚 Documentation:"
echo "  - Integration guide: GAMECRAFT_INTEGRATION_DESIGN.md"
echo "  - World presets: gamecraft_configs/world_presets.json"
echo "  - Action sequences: gamecraft_configs/action_sequences.json"
echo ""
echo "🆘 If you encounter issues:"
echo "  - Check virtual environment: source $VENV_DIR/bin/activate"
echo "  - Test PyTorch Metal: python3 -c 'import torch; print(torch.backends.mps.is_available())'"
echo "  - Check models: ls -la $GAMECRAFT_DIR/weights/"
echo ""
echo "🎮 Happy world building!"