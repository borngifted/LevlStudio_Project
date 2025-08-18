#!/bin/bash
# Setup Hunyuan-GameCraft-1.0 Environment
# This script sets up the GameCraft environment and downloads models

PROJECT_ROOT="/Volumes/Jul_23_2025/LevlStudio_Project"
GAMECRAFT_DIR="$PROJECT_ROOT/Hunyuan-GameCraft-1.0"

echo "🎮 Setting up Hunyuan-GameCraft-1.0 Environment..."

cd "$PROJECT_ROOT"

# Check if GameCraft is already cloned
if [ ! -d "$GAMECRAFT_DIR" ]; then
    echo "❌ GameCraft directory not found. Please run this from LevlStudio project root."
    exit 1
fi

echo "📁 Found GameCraft directory: $GAMECRAFT_DIR"

# Create conda environment for GameCraft
echo "🐍 Creating conda environment: HYGameCraft..."
conda create -n HYGameCraft python=3.10 -y

# Activate environment
echo "⚡ Activating HYGameCraft environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate HYGameCraft

# Install PyTorch with CUDA support
echo "🔥 Installing PyTorch with CUDA 12.4..."
conda install pytorch==2.5.1 torchvision==0.20.0 torchaudio==2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia -y

# Install requirements
echo "📦 Installing Python dependencies..."
cd "$GAMECRAFT_DIR"
python -m pip install -r requirements.txt

# Install Flash Attention for acceleration
echo "⚡ Installing Flash Attention v2..."
python -m pip install ninja
python -m pip install "git+https://github.com/Dao-AILab/flash-attention.git@v2.6.3"

# Install additional dependencies for LevlStudio integration
echo "🔧 Installing additional dependencies for LevlStudio integration..."
python -m pip install opencv-python-headless
python -m pip install mediapipe
python -m pip install open3d
python -m pip install trimesh
python -m pip install scikit-image

# Check if weights directory exists
WEIGHTS_DIR="$GAMECRAFT_DIR/weights"
if [ ! -d "$WEIGHTS_DIR" ]; then
    echo "📥 Creating weights directory..."
    mkdir -p "$WEIGHTS_DIR"
fi

# Download models if not present
MODEL_FILE="$WEIGHTS_DIR/gamecraft_models/mp_rank_00_model_states.pt"
if [ ! -f "$MODEL_FILE" ]; then
    echo "📥 Downloading GameCraft models (this may take a while)..."
    
    # Install huggingface-cli if not present
    python -m pip install "huggingface_hub[cli]"
    
    cd "$WEIGHTS_DIR"
    echo "🚀 Downloading from HuggingFace (10 minutes to 1 hour depending on connection)..."
    huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./
    
    if [ $? -eq 0 ]; then
        echo "✅ Models downloaded successfully!"
    else
        echo "❌ Model download failed. You may need to download manually."
        echo "Run: cd weights && huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./"
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
CONDA_ENV=HYGameCraft
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

# GPU settings
CUDA_VISIBLE_DEVICES=0
USE_FP8=true
USE_DISTILL=false
EOF

# Create activation script
echo "📝 Creating GameCraft activation script..."
cat > activate_gamecraft.sh << 'EOF'
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
EOF

chmod +x activate_gamecraft.sh

# Test installation
echo "🧪 Testing GameCraft installation..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate HYGameCraft

python << 'EOF'
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"✅ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    
    import transformers
    print(f"✅ Transformers: {transformers.__version__}")
    
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
    
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
    
    # Test GameCraft integration
    import sys
    sys.path.append('/Volumes/Jul_23_2025/LevlStudio_Project')
    from gamecraft_integration import GameCraftRunner
    print("✅ GameCraft integration imported successfully")
    
    print("\n🎉 GameCraft environment setup complete!")
    
except Exception as e:
    print(f"❌ Setup test failed: {e}")
    
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 GameCraft Environment Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "1. Activate environment: source activate_gamecraft.sh"
echo "2. Test integration: gamecraft-test"
echo "3. Run pipeline: gamecraft-pipeline --help"
echo ""
echo "🛠️ Available tools:"
echo "  - GameCraft world generation"
echo "  - Video processing and analysis"
echo "  - 3D scene reconstruction (coming soon)"
echo "  - Unreal Engine export (coming soon)"
echo ""
echo "📚 Documentation:"
echo "  - Integration guide: GAMECRAFT_INTEGRATION_DESIGN.md"
echo "  - World presets: gamecraft_configs/world_presets.json"
echo "  - Action sequences: gamecraft_configs/action_sequences.json"
echo ""
echo "🆘 If you encounter issues:"
echo "  - Check conda environment: conda info --envs"
echo "  - Verify GPU: nvidia-smi"
echo "  - Check models: ls -la $GAMECRAFT_DIR/weights/"
echo ""
echo "🎮 Happy world building!"