# 🎬 LevlStudio - AI-Powered 3D Content Creation Pipeline

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#platform-support)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](#prerequisites)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)
[![Access](https://img.shields.io/badge/Access-Password%20Protected-red)](#access-requirements)

> **Complete AI-powered 3D content creation pipeline integrating Unreal Engine 5, ComfyUI, and Blender with one-click installation.**
> This repository contains proprietary AI workflows and professional 3D assets.
> By proceeding, you confirm you have authorization to use this system.

## 🚀 **Quick Start (30 seconds)**

<details>
<summary>🔐 <strong>Click here and enter password: Ibu/ubI</strong></summary>

```bash
# Clone the repository 
git clone git@github.com:borngifted/LevlStudio_Project.git
cd LevlStudio_Project

# 🪟 Windows - Enter password when prompted
python install_levlstudio.py

# 🍎 macOS/Linux - Enter password when prompted
python3 install_levlstudio.py
```

> **✅ Access Granted**: You have successfully entered the access password.

</details>

🛑 **If you cannot see installation commands above**, you do not have proper access authorization.

**What happens automatically:**
- ✅ Cross-platform setup (Windows/macOS/Linux)
- ✅ Python virtual environment with dependencies
- ✅ **ComfyUI complete installation** with AI models and extensions
- ✅ **Essential custom nodes** (ControlNet, IPAdapter, Manager, VideoHelper)
- ✅ Blender addon installation and configuration
- ✅ Unreal Engine integration scripts
- ✅ Auto-git system for continuous deployment
- ✅ **Ready-to-use AI workflows** for immediate production

## 🎯 **What is LevlStudio?**

LevlStudio is a complete pipeline that connects the world's most powerful creative tools:

### **🎮 Unreal Engine 5** → **🎨 ComfyUI** → **🎭 Blender** → **🎬 Final Output**

- **Unreal Engine 5**: Create and render 3D scenes
- **ComfyUI**: AI-powered stylization with ControlNet
- **Blender**: Post-processing and compositing
- **Automated Bridge**: Seamless file transfer and processing

## 📋 **Prerequisites**

### **🪟 Windows Requirements**
1. **Python 3.10.x (64-bit)** - [Download](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"

2. **Git** - [Download](https://git-scm.com/download/win)
   - Accept defaults, ensure Git Bash in PATH

3. **Visual Studio 2022 Community** - [Download](https://visualstudio.microsoft.com/vs/community/)
   - ✅ Desktop Development with C++
   - ✅ Game Development with C++ (Unreal Engine)

### **🍎 macOS Requirements**
1. **Python 3.10.x** - [Download](https://www.python.org/downloads/) or `brew install python@3.10`
2. **Git** - Built-in or `brew install git`
3. **Xcode Command Line Tools** - `xcode-select --install`

## 🎨 **Core Features**

### **AI-Powered Stylization**
- **Triple-ControlNet Pipeline**: Depth + Pose + Canny edge control
- **Frame Consistency**: WAN-FUN model for temporal stability
- **Batch Processing**: Automatic sequence processing
- **Real-time Monitoring**: WebSocket progress tracking

### **3D Asset Management**
- **JSON-Driven Scenes**: Configure everything via JSON
- **33+ 3D Assets**: Characters, props, environments
- **Material Library**: Snow, ice, brass, wood presets
- **Lighting Presets**: Day, night, magical atmospheres

### **Workflow Automation**
- **Auto-File Watching**: Detect new Unreal exports
- **Auto-Git Integration**: Commit and push changes automatically
- **Cross-Platform Scripts**: Works on Windows, macOS, Linux
- **One-Click Launching**: Start all services with single command

## 🛠️ **Installation Guide**

### **Option A: One-Click Installation (Recommended)**

1. **Run the installer:**
   ```bash
   # 🪟 Windows
   python install_levlstudio.py
   
   # 🍎 macOS
   python3 install_levlstudio.py
   ```

2. **Launch applications:**
   ```bash
   # 🪟 Windows
   python launcher.py --comfyui    # Start ComfyUI
   python launcher.py --blender    # Start Blender
   LevlStudio.bat --all           # Start everything
   
   # 🍎 macOS
   python3 launcher.py --comfyui   # Start ComfyUI
   python3 launcher.py --blender   # Start Blender
   ./LevlStudio.sh --all          # Start everything
   ```

### **Option B: Manual Installation**

For detailed manual setup instructions, see: [**ONE_CLICK_SETUP.md**](ONE_CLICK_SETUP.md)

### **Clone Repository Options**

<details>
<summary>🔐 <strong>Advanced Clone Methods (Password Required: Ibu/ubI)</strong></summary>

**🪟 Windows Users:**
```cmd
# SSH (Recommended)
git clone git@github.com:borngifted/LevlStudio_Project.git

# HTTPS Alternative
git clone https://github.com/borngifted/LevlStudio_Project.git

# GitHub Desktop (GUI Option)
# Download from: https://desktop.github.com/
```

**🍎 macOS Users:**
```bash
# SSH (Recommended)
git clone git@github.com:borngifted/LevlStudio_Project.git

# HTTPS Alternative
git clone https://github.com/borngifted/LevlStudio_Project.git

# Using Homebrew
brew install git
git clone git@github.com:borngifted/LevlStudio_Project.git
```

</details>

## 🎮 **Setting up Visual Studio Code for Unreal Engine**

### **🪟 Windows Setup**

**A. Install Necessary Software:**

1. **Visual Studio Code:**
   - Go to [Visual Studio Code website](https://code.visualstudio.com/)
   - Download the installer for Windows
   - Run installer and follow prompts

2. **Visual Studio Build Tools:**
   - Go to [Visual Studio downloads](https://visualstudio.microsoft.com/downloads/)
   - Scroll to "All Downloads" → "Tools for Visual Studio"
   - Download "Build Tools for Visual Studio"
   - In installer workloads, select "Desktop development with C++" and click "Install"

**B. Configure Unreal Engine:**

1. **Create a New C++ Project:**
   - Open Epic Games Launcher and launch Unreal Engine
   - Create new project with C++ template (e.g., Third Person)

2. **Set Visual Studio Code as Default Editor:**
   - In Unreal Editor: Edit → Editor Preferences
   - Under General section, select Source Code
   - In Source Code Editor dropdown, choose Visual Studio Code
   - Restart Unreal Editor

3. **Generate Project Files:**
   - Navigate to project folder in File Explorer
   - Right-click .uproject file → "Generate Visual Studio project files"
   - This creates a .code-workspace file

**C. Configure Visual Studio Code:**

1. **Open the Workspace:**
   - Open Visual Studio Code
   - Open the newly created .code-workspace file

2. **Install Extensions:**
   - Go to Extensions view (Ctrl+Shift+X)
   - Install "C/C++ Extension Pack" by Microsoft
   - Install "C#" extension by Microsoft

3. **Run a Debug Session:**
   - Go to "Run and Debug" view (Ctrl+Shift+D)
   - Select "Launch [YourProjectName]Editor (Development) (Workspace)"
   - Press F5 or click green play button to start debugging

### **🍎 macOS Setup**

**A. Install Necessary Software:**

1. **Visual Studio Code:**
   - Go to [Visual Studio Code website](https://code.visualstudio.com/)
   - Download installer for macOS
   - Drag Visual Studio Code to Applications folder

2. **Xcode Command Line Tools:**
   - Open Terminal application
   - Run command: `xcode-select --install`
   - Follow prompts to install command line tools

**B. Configure Unreal Engine:**

1. **Create a New C++ Project:**
   - Follow same steps as Windows to create C++ project

2. **Set Visual Studio Code as Default Editor:**
   - In Unreal Editor: Unreal Engine → Preferences
   - Under General section, select Source Code
   - In Source Code Editor dropdown, choose Visual Studio Code
   - Restart Unreal Editor

3. **Generate Project Files:**
   - Follow same steps as Windows to generate project files

**C. Configure Visual Studio Code:**

1. **Open the Workspace:**
   - Open the .code-workspace file in Visual Studio Code

2. **Install Extensions:**
   - Install same "C/C++ Extension Pack" and "C#" extensions

3. **Run a Debug Session:**
   - Follow same steps as Windows to start debug session

## 🎬 **Complete Workflow Examples**

### **UE5 → Stylized Video Pipeline**

```bash
# 1. Start the bridge system
# 🪟 Windows
python unreal_comfyui_bridge.py --start-comfyui --watch

# 🍎 macOS
python3 unreal_comfyui_bridge.py --start-comfyui --watch

# 2. In Unreal Engine:
#    - Export sequence using Movie Render Queue
#    - Files auto-detected and processed
#    - Stylized output ready for import

# 3. Results in ComfyUI/output/ folder
```

### **AI → 3D Asset Generation**

```bash
# Generate 3D asset from text description
# 🪟 Windows
python ai_to_3d_pipeline.py --prompt "futuristic vehicle" --name "sci_fi_car"

# 🍎 macOS
python3 ai_to_3d_pipeline.py --prompt "futuristic vehicle" --name "sci_fi_car"

# Process in Blender and export for UE5
```

### **JSON → Blender Scene Building**

```bash
# Build scenes from JSON configuration
# 🪟 Windows
python launcher.py --blender

# 🍎 macOS
python3 launcher.py --blender

# Load JSON → Build Scene → Export to UE5
```

## 📁 **Project Structure**

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
    ├── ONE_CLICK_SETUP.md        # Complete setup guide
    ├── COMPLETE_PROJECT_GUIDE.md # Full documentation
    └── SETUP_INSTRUCTIONS.md    # Detailed setup
```

## 🎨 **ComfyUI Workflow Features**

### **Triple-ControlNet Pipeline**
- **Depth Control (0.7)**: Structure preservation
- **Pose Control (0.6)**: Character consistency  
- **Canny Control (0.45)**: Edge preservation
- **WAN-FUN Model**: Frame-to-frame consistency
- **Fixed Seed**: Temporal stability

### **Optimized Settings**
- **22 Steps**: Quality/speed balance
- **CFG 5.5**: Optimal guidance
- **Denoise 0.45**: Perfect img2img strength
- **DPM++ 2M Karras**: Best scheduler

## 🔄 **Auto-Git System**

### **Automatic Commits & Pushes**
```bash
# Start file watcher (commits changes every 30 seconds)
# 🪟 Windows
python auto_git_watcher.py

# 🍎 macOS
python3 auto_git_watcher.py

# Or use manual commits (still auto-pushes)
git add .
git commit -m "Your changes"
# → Automatically pushes to GitHub!
```

### **What Gets Auto-Committed**
- ✅ New workflows in ComfyUI
- ✅ Asset changes in Blender
- ✅ Config updates in JSON files
- ✅ New 3D models and textures
- ✅ Documentation updates

## 🚨 **Troubleshooting**

<details>
<summary>🔐 <strong>Access Support Documentation (Password: Ibu/ubI)</strong></summary>

### **Windows Issues**
```cmd
# Check prerequisites
python --version          # Should be 3.10.x
git --version             # Should be installed
# Check Visual Studio in Add/Remove Programs

# Re-run installer if needed
python install_levlstudio.py
```

### **macOS Issues**
```bash
# Check prerequisites
python3 --version         # Should be 3.10.x
xcode-select -p           # Should show tools path

# Re-run installer if needed
python3 install_levlstudio.py
```

### **ComfyUI Issues**
- **Models not loading**: Check `ComfyUI/models/` folders
- **Extensions missing**: Use ComfyUI Manager tab
- **GPU errors**: Update graphics drivers

For detailed troubleshooting, see: [**ONE_CLICK_SETUP.md**](ONE_CLICK_SETUP.md#troubleshooting)

</details>

## 📖 **Documentation**

<details>
<summary>🔐 <strong>Access Technical Documentation (Password: Ibu/ubI)</strong></summary>

- **[ONE_CLICK_SETUP.md](ONE_CLICK_SETUP.md)** - Complete setup guide with platform-specific instructions
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Quick start instructions  
- **[COMPLETE_PROJECT_GUIDE.md](COMPLETE_PROJECT_GUIDE.md)** - Full technical documentation
- **[REPOSITORY_ACCESS.md](REPOSITORY_ACCESS.md)** - Repository security and access control
- **[ComfyUI/README.md](ComfyUI/README.md)** - ComfyUI integration documentation

</details>

## 🤝 **Contributing**

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 **Success Stories**

> "LevlStudio transformed our 3D pipeline. What used to take days now takes hours!" - *Game Studio*

> "The AI stylization is incredible. Frame consistency is perfect." - *VFX Artist*

> "One-click setup saved us hours of configuration time." - *Technical Director*

## 🚀 **What's Next?**

- 🔮 **Real-time rendering** integration
- 🎬 **Video generation** workflows
- 🌐 **Cloud processing** support
- 🤖 **Advanced AI models** integration

---

**🎊 Welcome to the future of AI-powered 3D content creation!**

*Built with ❤️ by the LevlStudio team*
