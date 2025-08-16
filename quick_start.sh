#!/bin/bash
# Quick start script for LevlStudio Scene Builder

echo "🎬 LevlStudio Scene Builder - Quick Start"
echo "========================================="

# Check if Blender is installed
if command -v blender &> /dev/null; then
    echo "✅ Blender found"
    BLENDER_PATH=$(which blender)
else
    echo "❌ Blender not found. Please install Blender first."
    echo "   Download from: https://www.blender.org/download/"
    exit 1
fi

# Get Blender version
BLENDER_VERSION=$($BLENDER_PATH --version | grep "Blender" | cut -d' ' -f2)
echo "   Version: $BLENDER_VERSION"

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."

# Try to install debugpy for VS Code debugging
echo "   Installing debugpy for VS Code debugging..."
$BLENDER_PATH --background --python-expr "import subprocess; subprocess.call(['pip', 'install', 'debugpy'])" 2>/dev/null

# Main menu
echo ""
echo "🚀 What would you like to do?"
echo ""
echo "1) Open Blender with the addon"
echo "2) Install addon to Blender's addon folder"
echo "3) Run batch processing (all scenes)"
echo "4) Build specific scene (headless)"
echo "5) Install Python dependencies"
echo "6) Open VS Code in project"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo "Opening Blender with LevlStudio addon..."
        $BLENDER_PATH --python levlstudio_scene_builder_addon.py
        ;;
    
    2)
        echo "Installing addon to Blender..."
        ADDON_DIR="$HOME/Library/Application Support/Blender/${BLENDER_VERSION%.*}/scripts/addons"
        mkdir -p "$ADDON_DIR"
        cp levlstudio_scene_builder_addon.py "$ADDON_DIR/"
        echo "✅ Addon installed to: $ADDON_DIR"
        echo "   Enable it in Blender: Edit → Preferences → Add-ons → Search 'LevlStudio'"
        ;;
    
    3)
        echo "Running batch processing..."
        $BLENDER_PATH -b --python batch_process.py -- --batch
        ;;
    
    4)
        read -p "Enter scene index (0-2): " scene_idx
        echo "Building scene $scene_idx..."
        $BLENDER_PATH -b --python batch_process.py -- --scene $scene_idx \
            --export "exports/scene_${scene_idx}.glb" \
            --render "renders/scene_${scene_idx}.png"
        ;;
    
    5)
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
        echo "✅ Dependencies installed"
        ;;
    
    6)
        if command -v code &> /dev/null; then
            echo "Opening VS Code..."
            code .
        else
            echo "❌ VS Code not found. Install from: https://code.visualstudio.com/"
        fi
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✨ Done! Check the README.md for detailed instructions."
