#!/bin/bash
# ComfyUI Extension Installer for UE5 → ComfyUI Workflow
# Run this from your ComfyUI custom_nodes directory

echo "🔧 Installing ComfyUI Extensions for UE5 → ComfyUI Workflow"
echo "============================================================="

# Navigate to ComfyUI custom_nodes directory
# Adjust this path for your Windows setup:
COMFY_NODES_DIR="C:/Users/sonof/Music/ComfyUI_windows_portable/ComfyUI/custom_nodes"

if [ ! -d "$COMFY_NODES_DIR" ]; then
    echo "❌ ComfyUI custom_nodes directory not found at: $COMFY_NODES_DIR"
    echo "Please update the COMFY_NODES_DIR path in this script"
    exit 1
fi

cd "$COMFY_NODES_DIR"

echo "📍 Working in: $(pwd)"

# 1. ControlNet Preprocessors (Essential for Depth/DW-Pose/Canny)
echo ""
echo "1️⃣ Installing ControlNet Aux (DepthAnything V2, DW-Pose, Canny)..."
if [ -d "comfyui_controlnet_aux" ]; then
    echo "   Updating existing installation..."
    cd comfyui_controlnet_aux && git pull && cd ..
else
    echo "   Fresh installation..."
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
fi

# 2. Video Helper Suite (Frame I/O)
echo ""
echo "2️⃣ Installing Video Helper Suite..."
if [ -d "ComfyUI-VideoHelperSuite" ]; then
    echo "   Updating existing installation..."
    cd ComfyUI-VideoHelperSuite && git pull && cd ..
else
    echo "   Fresh installation..."
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
fi

# 3. Advanced ControlNet (Optional but recommended)
echo ""
echo "3️⃣ Installing Advanced ControlNet..."
if [ -d "ComfyUI-Advanced-ControlNet" ]; then
    echo "   Updating existing installation..."
    cd ComfyUI-Advanced-ControlNet && git pull && cd ..
else
    echo "   Fresh installation..."
    git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git
fi

# 4. Impact Pack (Alternative video helper)
echo ""
echo "4️⃣ Installing Impact Pack (additional tools)..."
if [ -d "ComfyUI-Impact-Pack" ]; then
    echo "   Updating existing installation..."
    cd ComfyUI-Impact-Pack && git pull && cd ..
else
    echo "   Fresh installation..."
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
fi

echo ""
echo "✅ Extension Installation Complete!"
echo ""
echo "🔄 Next Steps:"
echo "1. Restart ComfyUI: python main.py"
echo "2. Load the patched workflow: wan_test_single_image_patched.json"
echo "3. Check that all nodes are available (no red nodes)"
echo ""
echo "🎯 Required Nodes to Verify:"
echo "   - DepthAnythingV2 Preprocessor"
echo "   - DW Pose Preprocessor"
echo "   - Canny Preprocessor"
echo "   - Load ControlNet Model"
echo "   - Apply ControlNet"
echo "   - Load Video (or Load Image Batch)"
echo ""
echo "If any nodes are missing, check the ComfyUI console for error messages."