# 🚀 LevlStudio - Quick Setup Instructions

## **1. Auto-Push System Setup**

### **Start Auto File Watcher**
```bash
# Navigate to project
cd /Volumes/Jul_23_2025/LevlStudio_Project

# Start the auto-watcher (runs continuously)
python3 auto_git_watcher.py
```

**What it does**:
- ✅ Monitors all files every 30 seconds
- ✅ Auto-commits changes with timestamps
- ✅ Auto-pushes to GitHub immediately
- ✅ Runs in background continuously

### **Manual Git Usage** (Still Auto-Pushes)
```bash
# Add files and commit (will auto-push)
git add .
git commit -m "Your changes"
# → Automatically pushes to GitHub!
```

---

## **2. Project Components Setup**

### **A. ComfyUI Integration**
```bash
# Install required extensions
cd /Users/workofficial/ComfyUI/ComfyUI/custom_nodes
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

# Restart ComfyUI
cd /Users/workofficial/ComfyUI/ComfyUI
python3 main.py
```

**Load Workflow**:
1. Go to `http://127.0.0.1:8188/`
2. Click ☰ menu → Load
3. Load: `workflow_results/complete_ue5_to_comfy_workflow.json`

### **B. Blender MCP Server**
```bash
# Test Blender integration
python3 quick_start.py

# Or start MCP server manually
python3 levl_mcp_server.py \
    --blender "/Applications/Blender.app/Contents/MacOS/Blender" \
    --addon "./levlstudio_scene_builder_addon.py" \
    --assets "./json/assets.json" \
    --scenes "./json/scenes.json" \
    --project "."
```

### **C. AI-to-3D Pipeline**
```bash
# Set up AI integration
python3 setup_ai_to_3d_workflow.py

# Optional: Add API keys
export OPENAI_API_KEY='your-key-here'
export GOOGLE_API_KEY='your-key-here'

# Test AI pipeline
python3 quick_start_ai_to_3d.py
```

### **D. UE5 Integration**
1. Open `LevlStudio.uproject` in UE5
2. Configure render settings:
   - Fixed frame rate
   - No auto-exposure
   - High quality export
3. Use Python bridge: `UE_Content_Python/LevlBridgeWatcherOneClick.py`

---

## **3. Complete Workflow Test**

### **UE5 → ComfyUI → Stylized Video**
```bash
# 1. Export frames from UE5
# 2. Load ComfyUI workflow
# 3. Set paths:
#    - Input: /path/to/ue5/frames/
#    - Models: depth, pose, canny ControlNets
#    - Checkpoint: WAN-FUN.safetensors
# 4. Run workflow
# 5. Output: Stylized video frames
```

### **AI → 3D → Blender → UE5**
```bash
# 1. Generate concept with AI
python3 ai_to_3d_pipeline.py --prompt "your description" --name "asset_name"

# 2. Process in Blender
python3 blender_automation.py --model path/to/model.glb --cleanup

# 3. Import to UE5
# Use automated import scripts
```

### **JSON → Blender Scene → Render**
```bash
# 1. Edit scene in json/scenes.json
# 2. Build scene in Blender
python3 batch_process.py --scene 0 --export "output.glb"

# 3. Import to UE5 or render directly
```

---

## **4. Monitoring & Maintenance**

### **Check Auto-Push Status**
```bash
# View recent commits
git log --oneline -10

# Check remote status
git remote -v

# Force push if needed
git push origin main --force
```

### **File Watcher Logs**
- Monitor console output from `auto_git_watcher.py`
- Check for commit/push confirmations
- Restart if needed

### **Project Health Check**
```bash
# Test all components
python3 quick_start.py          # Blender integration
python3 test_mcp_server.py      # MCP functionality
# Check ComfyUI at http://127.0.0.1:8188/
```

---

## **5. Daily Usage**

### **Adding New Files**
1. **Just save files** - Auto-watcher handles the rest!
2. Or manually: `git add . && git commit -m "message"`
3. **No git push needed** - automatically handled

### **Working on Assets**
1. Edit assets in `assets/` folder
2. Update JSON configs in `json/`
3. Test in Blender or ComfyUI
4. Changes auto-commit and push

### **Creating Workflows**
1. Build workflow in ComfyUI
2. Export JSON to `workflow_results/`
3. Test and document
4. Auto-pushed to repository

---

## **6. Troubleshooting**

### **Auto-Push Not Working**
```bash
# Check git hooks
ls -la .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# Test manual push
git push origin main
```

### **File Watcher Issues**
```bash
# Restart watcher
pkill -f auto_git_watcher.py
python3 auto_git_watcher.py
```

### **ComfyUI Node Errors**
```bash
# Reinstall extensions
cd /Users/workofficial/ComfyUI/ComfyUI/custom_nodes
rm -rf comfyui_controlnet_aux
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
```

---

## **🎯 Quick Start Checklist**

- [ ] **Clone repository** from GitHub
- [ ] **Install Python dependencies** (`pip install -r requirements.txt`)
- [ ] **Start auto-watcher** (`python3 auto_git_watcher.py`)
- [ ] **Install ComfyUI extensions** (controlnet_aux, video helper)
- [ ] **Load Blender addon** (`levlstudio_scene_builder_addon.py`)
- [ ] **Test UE5 project** (`LevlStudio.uproject`)
- [ ] **Verify auto-push** (make a test file change)

**🎉 You're ready to create AI-powered 3D content!**

---

*For complete documentation, see: `COMPLETE_PROJECT_GUIDE.md`*