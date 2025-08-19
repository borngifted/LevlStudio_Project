# 🚀 LevlStudio Complete Setup Guide

> **Professional AI-powered 3D content creation system**  
> Complete pipeline integrating Unreal Engine, ComfyUI, and Blender automation.

## **🔹 Step 1 — Install Core Prerequisites**

### **🪟 Windows Setup**

**Before ComfyUI and AI nodes will work:**

**1. Install Python 3.10.x (64-bit)**
- Download from [Python.org](https://www.python.org/downloads/)
- During install:
  - ✅ Check "Add Python to PATH"
  - ✅ Check "Install for all users"

**2. Install Git**
- Download [Git for Windows](https://git-scm.com/download/win)
- Accept defaults, ensure it adds Git Bash to PATH

**3. Install Visual Studio 2022 (Community)**
- Download [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/)
- In Visual Studio Installer, check:
  - ✅ **Desktop Development with C++**
  - ✅ **Game Development with C++** (Unreal Engine)
  - This ensures MSVC compiler, CMake, and Windows SDK

### **🍎 macOS Setup**

**1. Install Python 3.10.x**
- Download from [Python.org](https://www.python.org/downloads/) or use Homebrew:
```bash
brew install python@3.10
```

**2. Install Git**
- Already included in macOS or install via Homebrew:
```bash
brew install git
```

**3. Install Xcode Command Line Tools**
```bash
xcode-select --install
```

---

## **🔹 Step 2 — One-Click Installation**

### **Automatic Setup**
<details>
<summary>🔐 <strong>STEP 1: Enter Access Password (Ibu/ubI) to Reveal Commands</strong></summary>

```bash
# Clone the repository
git clone git@github.com:borngifted/LevlStudio_Project.git
cd LevlStudio_Project

# Windows
python install_levlstudio.py

# macOS/Linux  
python3 install_levlstudio.py
```

> ✅ **Access Granted**: Installation commands revealed.

</details>

🛑 **Access Denied**: If you cannot see installation commands above, you are not authorized.

### **Alternative Clone Methods**

<details>
<summary>🔐 <strong>Advanced Setup Options (Password: Ibu/ubI)</strong></summary>

**🪟 Windows (Multiple Options):**
```cmd
# Option 1: SSH (Recommended)
git clone git@github.com:borngifted/LevlStudio_Project.git

# Option 2: HTTPS
git clone https://github.com/borngifted/LevlStudio_Project.git

# Option 3: GitHub Desktop
# - Download GitHub Desktop from https://desktop.github.com/
# - Click "Clone from GitHub" and enter repository URL
# - Navigate to folder and run installer
```

**🍎 macOS (Multiple Options):**
```bash
# Option 1: SSH (Recommended)
git clone git@github.com:borngifted/LevlStudio_Project.git

# Option 2: HTTPS
git clone https://github.com/borngifted/LevlStudio_Project.git

# Option 3: GitHub Desktop
# - Download GitHub Desktop from https://desktop.github.com/
# - Click "Clone from GitHub" and enter repository URL
# - Navigate to folder and run installer

# Option 4: Homebrew Git
brew install git
git clone git@github.com:borngifted/LevlStudio_Project.git
```

</details>

**What it does automatically:**
- ✅ **Cross-platform setup** (Mac/Windows/Linux)
- ✅ **Python virtual environment** with all dependencies
- ✅ **ComfyUI installation** with required extensions
- ✅ **Essential custom nodes** (ControlNet, IPAdapter, Manager, etc.)
- ✅ **Blender addon** installation and configuration
- ✅ **Startup scripts** for easy launching
- ✅ **Auto-git system** for automatic pushes
- ✅ **Model folder structure** setup
- ✅ **ComfyUI workspace configuration** with optimized workflows

### **2. Launch Applications**

**🪟 Windows:**
```cmd
# Start ComfyUI
python launcher.py --comfyui

# Start Blender with addon
python launcher.py --blender

# Start auto-git watcher
python launcher.py --watcher

# Or use batch file
LevlStudio.bat --comfyui
```

**🍎 macOS:**
```bash
# Start ComfyUI
python3 launcher.py --comfyui

# Start Blender with addon
python3 launcher.py --blender

# Start auto-git watcher
python3 launcher.py --watcher

# Or use shell script
./LevlStudio.sh --comfyui
```

---

## **🔹 Step 3 — Manual ComfyUI Setup (Alternative)**

*Skip this if you used the one-click installer*

### **🪟 Windows Manual Setup**
```cmd
# Open PowerShell or Git Bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Test run
python main.py
# → Opens ComfyUI at http://127.0.0.1:8188
```

### **🍎 macOS Manual Setup**
```bash
# Open Terminal
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test run
python3 main.py
# → Opens ComfyUI at http://127.0.0.1:8188
```

### **Add Essential Custom Nodes**

For your UE → Comfy → Blender pipeline:

**🪟 Windows:**
```cmd
cd ComfyUI\custom_nodes

# ControlNet + Depth + Pose
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git

# IPAdapter (style transfer / image conditioning)
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# Extra utilities
git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# Install requirements
cd ..
venv\Scripts\activate
pip install -r custom_nodes\comfyui_controlnet_aux\requirements.txt
pip install -r custom_nodes\ComfyUI-Advanced-ControlNet\requirements.txt
pip install -r custom_nodes\ComfyUI_IPAdapter_plus\requirements.txt
```

**🍎 macOS:**
```bash
cd ComfyUI/custom_nodes

# ControlNet + Depth + Pose
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git

# IPAdapter (style transfer / image conditioning)
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# Extra utilities
git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# Install requirements
cd ..
source venv/bin/activate
pip install -r custom_nodes/comfyui_controlnet_aux/requirements.txt
pip install -r custom_nodes/ComfyUI-Advanced-ControlNet/requirements.txt
pip install -r custom_nodes/ComfyUI_IPAdapter_plus/requirements.txt
```

---

## **🔹 Step 4 — Download AI Models**

<details>
<summary>🔐 <strong>Access AI Model Documentation (Password: Ibu/ubI)</strong></summary>

### **Create Model Folders**
Make these folders inside `ComfyUI/models/`:
- `checkpoints/` → base models (SD1.5, SDXL .safetensors)
- `controlnet/` → depth, openpose, canny models
- `ipadapter/` → IP-Adapter weights
- `clip_vision/` → CLIP vision models
- `diffusers/` → diffusion models

### **Essential Model Downloads**

**1. Base Checkpoints** (Download from [HuggingFace](https://huggingface.co) → `models/checkpoints/`):
- `sdxl_base_1.0.safetensors` → SDXL base model
- `sd_xl_refiner_1.0.safetensors` → SDXL refiner
- `WAN-FUN.safetensors` → Frame consistency model

**2. ControlNet Models** (→ `models/controlnet/`):
- `depth_anything_v2_vitg_fp32.safetensors` → Depth control
- `dwpose_model.pth` → Pose detection
- `canny_edge_fp16.safetensors` → Edge detection
- `control_sd15_openpose.pth` → OpenPose control

**3. IPAdapter Models** (→ `models/ipadapter/`):
- `ip-adapter_sd15.safetensors` → Style transfer
- `ip-adapter-plus_sd15.safetensors` → Enhanced style control

**4. CLIP Vision** (→ `models/clip_vision/`):
- `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`

### **Quick Model Download Script**

**🪟 Windows:**
```cmd
# Create model directories
mkdir ComfyUI\models\checkpoints
mkdir ComfyUI\models\controlnet
mkdir ComfyUI\models\ipadapter
mkdir ComfyUI\models\clip_vision

echo Download models from HuggingFace and place in respective folders
echo See documentation for specific model links
```

**🍎 macOS:**
```bash
# Create model directories
mkdir -p ComfyUI/models/{checkpoints,controlnet,ipadapter,clip_vision}

echo "Download models from HuggingFace and place in respective folders"
echo "See documentation for specific model links"
```

---

## 🎮 **Unreal Engine → ComfyUI Integration**

### **🔹 Step 5 — Connect Unreal → ComfyUI**

**Complete Automated Workflow:**

```mermaid
graph LR
    A[UE5 Sequence] --> B[Movie Render Queue]
    B --> C[PNG/EXR Frames]
    C --> D[Watched Folder]
    D --> E[ComfyUI Processing]
    E --> F[Triple ControlNet]
    F --> G[Stylized Output]
    G --> H[UE5/Blender Import]
```

**Workflow Steps:**

**1. Render from Unreal Engine**
- Use **Movie Render Queue** for frame sequences
- Export as `.png` or `.exr` files
- Save to watched folder: `C:\ComfyPipeline\frames_in` (Windows) or `~/ComfyPipeline/frames_in` (Mac)

**2. ComfyUI Processing**
- Load your workflow graph in ComfyUI
- **Load Images** → **Depth/ControlNet Preprocessors**:
  - DWOpenPose (pose detection)
  - DepthAnything (depth mapping)
  - PyraCanny (edge detection)
- **Combine into ApplyControlNet**
- **Feed into model checkpoint** (WAN-FUN or SDXL)
- **Output to Save Images** → `frames_out` folder

**3. Re-import Processed Frames**
- Import `frames_out` sequence back into Unreal or Blender
- Use for final compositing or VFX shots

### **Automated Bridge Setup**

**1. Start the Bridge**

**🪟 Windows:**
```cmd
# Start ComfyUI automatically and watch for UE5 exports
python unreal_comfyui_bridge.py --start-comfyui --watch
```

**🍎 macOS:**
```bash
# Start ComfyUI automatically and watch for UE5 exports
python3 unreal_comfyui_bridge.py --start-comfyui --watch
```

**2. Create Unreal Python Script**

**🪟 Windows:**
```cmd
# Generate Unreal Engine integration script
python unreal_comfyui_bridge.py --create-ue-script
```

**🍎 macOS:**
```bash
# Generate Unreal Engine integration script
python3 unreal_comfyui_bridge.py --create-ue-script
```

**3. In Unreal Engine**
```python
# Use the generated script in UE5 Python console
exec(open('UE_Content_Python/levlstudio_bridge.py').read())

# Export sequence for ComfyUI processing
bridge = LevlStudioUnrealBridge()
bridge.export_sequence_for_comfyui("my_sequence", my_level_sequence)
```

### **Automatic Processing**
1. **UE5 exports** sequence to `UnrealBridge/outbox/`
2. **Bridge detects** new sequence automatically
3. **ComfyUI processes** with triple-ControlNet workflow
4. **Stylized frames** saved to ComfyUI output
5. **Optional**: Auto-import back to UE5

---

## **🔹 Step 6 — Connect Blender (Optional Polishing)**

### **Post-Processing Pipeline**
You can pipe the `frames_out` into Blender for advanced compositing:

**1. Import Processed Sequence**
- Load frames as **Image Sequence Texture** on a plane
- Use in **Compositor** for additional VFX
- Combine with 3D elements for mixed reality shots

**2. Blender Workflow**
```bash
# 🪟 Windows
python launcher.py --blender

# 🍎 macOS
python3 launcher.py --blender
```

**3. Compositor Setup**
- **Input → Image Sequence** (load your `frames_out`)
- **Add nodes:** Color Correction, Blur, Glare, etc.
- **Output → File Output** for final render

---

## **🔹 Step 7 — Automations & Workflow Management**

### **ComfyUI Manager**
- Use **ComfyUI Manager** (in UI under "Manager" tab)
- Install/update nodes automatically
- Browse and install community workflows

### **Workflow JSON Scripting**
- Use Claude + ChatGPT to generate workflow JSON graphs
- Save as `.json` files and drag into ComfyUI
- Version control workflows with Git

### **Auto-Processing Setup**

**🪟 Windows:**
```cmd
# Start auto-watcher for continuous processing
python launcher.py --watcher

# Or start all services
LevlStudio.bat --all
```

**🍎 macOS:**
```bash
# Start auto-watcher for continuous processing
python3 launcher.py --watcher

# Or start all services
./LevlStudio.sh --all
```

### **File Organization**
```
ComfyPipeline/
├── frames_in/          # UE5 exports here
│   ├── sequence_001/
│   └── sequence_002/
├── frames_out/         # ComfyUI outputs here
│   ├── stylized_001/
│   └── stylized_002/
└── workflows/          # JSON workflow files
    ├── ue5_stylize.json
    └── depth_control.json
```

---

## **✅ Complete Pipeline Verification**

### **Full Workflow Test: UE5 → Stylized Video**

**1. Export from UE5**
- Use **Movie Render Queue**
- Export to `ComfyPipeline/frames_in/test_sequence/`
- Fixed frame rate, no auto-exposure, high quality

**2. Process in ComfyUI**
- Load workflow: `workflow_results/complete_ue5_to_comfy_workflow.json`
- Set input path: `/path/to/frames_in/test_sequence/`
- Models: depth, pose, canny ControlNets
- Checkpoint: WAN-FUN.safetensors
- Run workflow

**3. Output Verification**
- Check `ComfyUI/output/` for stylized frames
- Verify frame consistency and quality
- Import back to UE5 or Blender

### **Alternative Workflows**

**AI → 3D → UE5:**
```bash
# 🪟 Windows
python ai_to_3d_pipeline.py --prompt "your description" --name "asset_name"
python blender_automation.py --model path\to\model.glb --cleanup

# 🍎 macOS
python3 ai_to_3d_pipeline.py --prompt "your description" --name "asset_name"
python3 blender_automation.py --model path/to/model.glb --cleanup
```

**JSON → Blender → Render:**
```bash
# Edit scene in json/scenes.json, then:
# 🪟 Windows
python batch_process.py --scene 0 --export "output.glb"

# 🍎 macOS  
python3 batch_process.py --scene 0 --export "output.glb"
```

---

## 🎨 **ComfyUI Workflow Features**

### **Triple-ControlNet Pipeline**
- **Depth Control** (0.7): Structure preservation
- **Pose Control** (0.6): Character consistency  
- **Canny Control** (0.45): Edge preservation
- **WAN-FUN Model**: Frame-to-frame consistency
- **Fixed Seed**: Temporal stability

### **Optimized Settings**
- **22 Steps**: Quality/speed balance
- **CFG 5.5**: Optimal guidance
- **Denoise 0.45**: Perfect img2img strength
- **DPM++ 2M Karras**: Best scheduler

### **Batch Processing**
- **Automatic frame detection**
- **Sequential processing**
- **Progress monitoring**
- **Error handling**

---

## 🎭 **Blender Integration**

### **JSON-Driven Scene Building**
```bash
# Build scene from JSON configuration
python launcher.py --blender
# In Blender: Load JSON → Build Scene → Export
```

### **Asset Management**
- **33 3D Assets**: Characters, props, environments
- **7 Scene Presets**: Pre-configured compositions
- **Material Library**: Snow, ice, brass, wood
- **Lighting Presets**: Day, night, magical

### **MCP Server Control**
```bash
# Start Blender MCP server
python levl_mcp_server.py \
    --blender "/Applications/Blender.app/Contents/MacOS/Blender" \
    --addon "./levlstudio_scene_builder_addon.py" \
    --assets "./json/assets.json" \
    --scenes "./json/scenes.json"
```

---

## 🤖 **AI-to-3D Pipeline**

### **Text → 3D Asset Generation**
```bash
# Generate 3D asset from text
python ai_to_3d_pipeline.py --prompt "futuristic vehicle" --name "sci_fi_car"

# Quick start AI workflow
python quick_start_ai_to_3d.py
```

### **Supported Services**
- **OpenAI GPT-4**: Concept generation
- **Tripo3D**: Text/image to 3D
- **Meshy**: Alternative 3D service
- **Hunyuan 3D**: Advanced modeling

### **Full Pipeline**
1. **Text prompt** → AI concept image
2. **Concept image** → 3D model (online service)
3. **3D model** → Blender cleanup
4. **Cleaned model** → UE5 import

---

## 🔄 **Auto-Git System**

### **Automatic Commits & Pushes**
```bash
# Start file watcher (commits changes every 30 seconds)
python auto_git_watcher.py

# Or use manual commits (still auto-pushes)
git add .
git commit -m "Your changes"
# → Automatically pushes to GitHub!
```

### **What Gets Auto-Committed**
- ✅ **New workflows** in ComfyUI
- ✅ **Asset changes** in Blender
- ✅ **Config updates** in JSON files
- ✅ **New 3D models** and textures
- ✅ **Documentation updates**

---

## 📁 **Project Structure (Updated)**

```
LevlStudio_Project/
├── 🚀 One-Click Setup
│   ├── install_levlstudio.py      # Cross-platform installer
│   ├── launcher.py                # Universal launcher
│   ├── LevlStudio.bat            # Windows launcher
│   └── LevlStudio.sh             # Mac/Linux launcher
├── 🎮 Unreal Integration
│   ├── unreal_comfyui_bridge.py  # UE5 ↔ ComfyUI bridge
│   ├── UE_Content_Python/        # UE5 Python scripts
│   ├── UnrealBridge/
│   │   ├── outbox/               # UE5 exports here
│   │   └── inbox/                # Processed results here
│   └── LevlStudio.uproject       # UE5 project
├── 🎨 ComfyUI Integration
│   ├── ComfyUI/                  # Local ComfyUI installation
│   ├── workflow_results/         # Ready-to-use workflows
│   └── comfy_workflows/          # Additional workflows
├── 🎭 Blender Pipeline
│   ├── levlstudio_scene_builder_addon.py # Main addon
│   ├── assets/                   # 3D asset library
│   ├── json/                     # Scene configurations
│   └── blender_mcp_server.py     # MCP server
├── 🤖 AI Integration
│   ├── ai_to_3d_pipeline.py      # Text → 3D pipeline
│   ├── ai_workflows/             # AI configurations
│   └── ai_generated_assets/      # AI outputs
├── 🔄 Automation
│   ├── auto_git_watcher.py       # Auto-commit system
│   ├── batch_process.py          # Batch operations
│   └── quick_start.py            # Project tester
└── 📖 Documentation
    ├── ONE_CLICK_SETUP.md        # This guide
    ├── COMPLETE_PROJECT_GUIDE.md # Full documentation
    └── SETUP_INSTRUCTIONS.md    # Detailed setup
```

---

## **🔹 Step 8 — Monitoring & Maintenance**

### **Project Health Check**

**🪟 Windows:**
```cmd
# Test all components
python quick_start.py          # Blender integration
python test_mcp_server.py      # MCP functionality
# Check ComfyUI at http://127.0.0.1:8188/
```

**🍎 macOS:**
```bash
# Test all components
python3 quick_start.py          # Blender integration
python3 test_mcp_server.py      # MCP functionality
# Check ComfyUI at http://127.0.0.1:8188/
```

### **Performance Tips**
- **GPU Memory:** Monitor VRAM usage in ComfyUI
- **Batch Size:** Adjust based on available GPU memory
- **Model Selection:** Use FP16 models for faster processing
- **Disk Space:** Clean up processed frames regularly

---

## 🔧 **Platform-Specific Notes**

### **🪟 Windows**
- **Python**: Use `python` for commands (ensure Python 3.10.x)
- **Blender**: `C:\Program Files\Blender Foundation\Blender 4.4\blender.exe`
- **Launcher**: `LevlStudio.bat` or `python launcher.py`
- **Virtual Environment**: `venv\Scripts\activate`
- **Path Separators**: Use `\\` in scripts, `/` works in most contexts
- **Visual Studio**: Required for building custom nodes

### **🍎 macOS**
- **Python**: Use `python3` for commands (built-in or Homebrew)
- **Blender**: `/Applications/Blender.app/Contents/MacOS/Blender`
- **Launcher**: `./LevlStudio.sh` or `python3 launcher.py`
- **Virtual Environment**: `source venv/bin/activate`
- **Xcode**: Command Line Tools required
- **Permissions**: May need to allow apps in Security & Privacy

### **🐧 Linux**
- **Python**: Use `python3` for commands
- **Blender**: `blender` (system PATH) or `/usr/bin/blender`
- **Launcher**: `./LevlStudio.sh` or `python3 launcher.py`
- **Dependencies**: Install build-essential, cmake, git

---

## **✅ Success Checklist**

After running the installer, verify these work:

### **🪟 Windows Verification**
- [ ] **Python 3.10.x installed**: `python --version`
- [ ] **Git available**: `git --version`
- [ ] **Visual Studio C++**: Check in Add/Remove Programs
- [ ] **ComfyUI starts**: `python launcher.py --comfyui`
- [ ] **ComfyUI accessible**: Navigate to `http://127.0.0.1:8188`
- [ ] **Custom nodes loaded**: Check Manager tab in ComfyUI
- [ ] **Models downloaded**: Check `ComfyUI/models/` folders
- [ ] **Blender with addon**: `python launcher.py --blender`
- [ ] **UE5 bridge**: `python unreal_comfyui_bridge.py --watch`
- [ ] **Auto-git works**: Make file change, watch auto-commit

### **🍎 macOS Verification**
- [ ] **Python 3.10.x installed**: `python3 --version`
- [ ] **Xcode CLI tools**: `xcode-select -p`
- [ ] **ComfyUI starts**: `python3 launcher.py --comfyui`
- [ ] **ComfyUI accessible**: Navigate to `http://127.0.0.1:8188`
- [ ] **Custom nodes loaded**: Check Manager tab in ComfyUI
- [ ] **Models downloaded**: Check `ComfyUI/models/` folders
- [ ] **Blender with addon**: `python3 launcher.py --blender`
- [ ] **UE5 bridge**: `python3 unreal_comfyui_bridge.py --watch`
- [ ] **Auto-git works**: Make file change, watch auto-commit

---

## 🎯 **Quick Workflow Examples**

### **UE5 → Stylized Video**

**🪟 Windows:**
```cmd
# 1. Start bridge
python unreal_comfyui_bridge.py --start-comfyui --watch

# 2. In UE5: Export sequence to UnrealBridge\outbox\
# 3. Bridge auto-processes with ComfyUI
# 4. Get stylized frames from ComfyUI\output\
```

**🍎 macOS:**
```bash
# 1. Start bridge
python3 unreal_comfyui_bridge.py --start-comfyui --watch

# 2. In UE5: Export sequence to UnrealBridge/outbox/
# 3. Bridge auto-processes with ComfyUI
# 4. Get stylized frames from ComfyUI/output/
```

### **Text → 3D → UE5**

**🪟 Windows:**
```cmd
# 1. Generate 3D asset
python ai_to_3d_pipeline.py --prompt "medieval sword" --name "sword_01"

# 2. Process in Blender
python launcher.py --blender
# Load → Clean → Export FBX

# 3. Import to UE5
# Use UE5 import pipeline
```

**🍎 macOS:**
```bash
# 1. Generate 3D asset
python3 ai_to_3d_pipeline.py --prompt "medieval sword" --name "sword_01"

# 2. Process in Blender
python3 launcher.py --blender
# Load → Clean → Export FBX

# 3. Import to UE5
# Use UE5 import pipeline
```

### **JSON → Blender → Render**

**🪟 Windows:**
```cmd
# 1. Edit scene in json\scenes.json
# 2. Build in Blender
python launcher.py --blender
# Load JSON → Build Scene → Render

# 3. Export for UE5
# GLB/FBX export ready
```

**🍎 macOS:**
```bash
# 1. Edit scene in json/scenes.json
# 2. Build in Blender
python3 launcher.py --blender
# Load JSON → Build Scene → Render

# 3. Export for UE5
# GLB/FBX export ready
```

---

## 🚨 **Troubleshooting**

### **Installation Issues**

**🪟 Windows:**
```cmd
# Re-run installer
python install_levlstudio.py

# Check Python version (need 3.10.x)
python --version

# Check Git
git --version

# Check Visual Studio
# Go to Add/Remove Programs → Visual Studio Community 2022
```

**🍎 macOS:**
```bash
# Re-run installer
python3 install_levlstudio.py

# Check Python version (need 3.10.x)
python3 --version

# Check Git
git --version

# Check Xcode CLI tools
xcode-select -p
```

### **ComfyUI Issues**

**🪟 Windows:**
```cmd
# Manual ComfyUI start
cd ComfyUI
venv\Scripts\activate
python main.py

# Install missing extensions
cd custom_nodes
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
```

**🍎 macOS:**
```bash
# Manual ComfyUI start
cd ComfyUI
source venv/bin/activate
python3 main.py

# Install missing extensions
cd custom_nodes
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
```

### **Blender Issues**

**🪟 Windows:**
```cmd
# Check Blender path
where blender

# Manual addon installation
# Blender → Edit → Preferences → Add-ons → Install → Select levlstudio_scene_builder_addon.py
```

**🍎 macOS:**
```bash
# Check Blender path
which blender

# Manual addon installation
# Blender → Preferences → Add-ons → Install → Select levlstudio_scene_builder_addon.py
```

### **Auto-Git Issues**

**🪟 Windows:**
```cmd
# Check git hooks
dir .git\hooks\post-commit

# Restart watcher
python auto_git_watcher.py
```

**🍎 macOS:**
```bash
# Check git hooks
ls -la .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# Restart watcher
python3 auto_git_watcher.py
```

### **Model Download Issues**
- **Slow downloads**: Use HuggingFace CLI or git-lfs
- **Storage space**: Models require ~10-50GB total
- **Missing models**: Check ComfyUI console for specific model paths
- **CUDA errors**: Ensure GPU drivers are updated

---

## 🎉 **Success Checklist**

After running the installer, verify these work:

- [ ] **ComfyUI starts**: `python launcher.py --comfyui`
- [ ] **Blender with addon**: `python launcher.py --blender`
- [ ] **Auto-git works**: Make a file change and watch it auto-commit
- [ ] **UE5 bridge**: `python unreal_comfyui_bridge.py --watch`
- [ ] **AI pipeline**: `python quick_start_ai_to_3d.py`

---

## **🎬 Ready to Create AI-Powered 3D Content!**

### **✅ After completing this setup, you'll have:**
- **Complete AI pipeline**: Unreal renders → ComfyUI stylization → Blender compositing → Final output
- **Cross-platform support**: Works on Windows, macOS, and Linux
- **Automated workflows**: File watchers, auto-git, and batch processing
- **Professional tools**: Industry-standard software integration
- **Community resources**: Access to ComfyUI Manager and workflow library

### **🚀 Next Steps:**
1. **Create your first workflow** using the UE5 → ComfyUI bridge
2. **Download AI models** for your specific artistic style
3. **Experiment with ControlNet** combinations for different effects
4. **Share your workflows** with the community via auto-git system

### **📖 Additional Resources:**
- **Complete Guide**: `COMPLETE_PROJECT_GUIDE.md`
- **Setup Details**: `SETUP_INSTRUCTIONS.md`
- **Project Structure**: `README.md`
- **Community**: GitHub Issues for support and feature requests

**🎊 Welcome to the future of AI-powered 3D content creation!**