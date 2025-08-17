# 🎨 ComfyUI Integration for LevlStudio

This directory contains the ComfyUI integration for the LevlStudio pipeline.

## 🚀 **Automatic Installation**

ComfyUI is automatically downloaded and installed when you run:

```bash
# 🪟 Windows
python install_levlstudio.py

# 🍎 macOS/Linux
python3 install_levlstudio.py
```

## 📁 **Directory Structure After Installation**

```
ComfyUI/
├── ComfyUI/                    # Main ComfyUI installation (auto-downloaded)
│   ├── main.py                # ComfyUI server
│   ├── nodes.py               # Core nodes
│   ├── models/                # AI model storage
│   │   ├── checkpoints/       # Base models (SD, SDXL)
│   │   ├── controlnet/        # ControlNet models
│   │   ├── ipadapter/         # IPAdapter models
│   │   └── clip_vision/       # CLIP vision models
│   ├── custom_nodes/          # Extensions and custom nodes
│   │   ├── comfyui_controlnet_aux/     # ControlNet preprocessors
│   │   ├── ComfyUI-Advanced-ControlNet/ # Advanced ControlNet
│   │   ├── ComfyUI_IPAdapter_plus/     # IPAdapter Plus
│   │   └── ComfyUI-Manager/           # Extension manager
│   ├── output/                # Generated images/videos
│   └── user/                  # User workflows and settings
├── WorkFlows/                 # LevlStudio workflow templates
│   ├── LevlWorkFlow.json     # Main UE5 workflow
│   └── wan_test_single_image.json # Test workflow
└── README.md                  # This file
```

## 🎬 **Ready-to-Use Workflows**

### **UE5 → Stylized Video Pipeline**
- **File**: `WorkFlows/LevlWorkFlow.json`
- **Purpose**: Convert Unreal Engine renders to stylized video
- **Features**: Triple-ControlNet (Depth + Pose + Canny)
- **Models**: WAN-FUN for frame consistency

### **Single Image Test**
- **File**: `WorkFlows/wan_test_single_image.json`
- **Purpose**: Test setup with single image
- **Features**: Quick validation of installation

## 🎨 **What Gets Installed Automatically**

### **Core ComfyUI**
- Latest ComfyUI from official repository
- Python dependencies and requirements
- Basic node library

### **Essential Extensions**
- **ComfyUI-Manager**: Extension management interface
- **comfyui_controlnet_aux**: ControlNet preprocessors
  - Depth estimation (DepthAnything V2)
  - Pose detection (DWPose)
  - Edge detection (Canny, HED)
- **ComfyUI-Advanced-ControlNet**: Enhanced ControlNet features
- **ComfyUI_IPAdapter_plus**: Image conditioning and style transfer
- **ComfyUI-VideoHelperSuite**: Video processing capabilities

### **Pre-configured Workflows**
- UE5 integration workflow
- Batch processing setups
- Test and validation workflows

## 🔧 **Manual Installation (Alternative)**

If you prefer to install ComfyUI manually:

### **1. Install ComfyUI**
```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git ComfyUI/ComfyUI
cd ComfyUI/ComfyUI

# Install requirements
pip install -r requirements.txt
```

### **2. Install Extensions**
```bash
cd custom_nodes

# ControlNet Aux
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git

# Advanced ControlNet  
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git

# IPAdapter Plus
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# Manager
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
```

### **3. Download Models**
- Place base models in `models/checkpoints/`
- Place ControlNet models in `models/controlnet/`
- Place IPAdapter models in `models/ipadapter/`

## 🚀 **Quick Start**

### **1. Start ComfyUI**
```bash
# Using LevlStudio launcher
python launcher.py --comfyui

# Or directly
cd ComfyUI/ComfyUI
python main.py
```

### **2. Access Web Interface**
Open: http://127.0.0.1:8188

### **3. Load Workflow**
1. Click the gear icon (⚙️) in ComfyUI
2. Select "Load" 
3. Choose `../WorkFlows/LevlWorkFlow.json`
4. Configure input/output paths
5. Click "Queue Prompt"

## 🎮 **Integration with Unreal Engine**

The ComfyUI installation automatically integrates with Unreal Engine:

```bash
# Start the bridge for automatic processing
python unreal_comfyui_bridge.py --start-comfyui --watch

# Export from UE5 → Auto-process → Stylized output
```

## 🔍 **Troubleshooting**

### **ComfyUI Won't Start**
```bash
# Check installation
cd ComfyUI/ComfyUI
python main.py

# Reinstall dependencies
pip install -r requirements.txt
```

### **Missing Nodes Error**
- Use ComfyUI Manager to install missing extensions
- Check `custom_nodes/` folder for proper installation

### **Model Not Found**
- Download required models to appropriate `models/` subfolders
- Check ComfyUI console for specific model paths

### **GPU Memory Issues**
- Reduce batch size in workflows
- Use FP16 models instead of FP32
- Close other GPU-intensive applications

## 📖 **Additional Resources**

- **ComfyUI Documentation**: [Official Wiki](https://github.com/comfyanonymous/ComfyUI/wiki)
- **Model Downloads**: [HuggingFace](https://huggingface.co)
- **Extension Registry**: [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- **LevlStudio Guide**: [../ONE_CLICK_SETUP.md](../ONE_CLICK_SETUP.md)

---

**🎊 ComfyUI is ready for AI-powered content creation!**