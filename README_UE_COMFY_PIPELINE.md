# LevlStudio One-Click UE5 → ComfyUI Pipeline

## 🚀 Overview

This system provides a seamless one-click pipeline from Unreal Engine 5 rendering to AI-powered style transfer using ComfyUI. With a single VS Code command, you can:

1. **Spawn** a Blueprint actor in UE5
2. **Create** a Level Sequence with camera
3. **Render** via Movie Render Queue (MRQ)
4. **Transfer** the rendered video to ComfyUI
5. **Apply** AI style transfer using WAN-F'N
6. **Output** a stylized video

## 📁 Project Structure

```
/LevlStudio_Project/
├── UnrealBridge/              # File-based communication bridge
│   ├── inbox/                 # Commands from MCP to UE
│   └── outbox/                # Results from UE to MCP
├── UE_Content_Python/         # Unreal Engine Python scripts
│   └── LevlBridgeWatcherOneClick.py
├── comfy_workflows/           # ComfyUI workflow templates
│   └── wanfn_depth_pose_canny_template.json
├── refs/                      # Style reference images
│   ├── style_festive_night.png
│   ├── style_ice_crystal.png
│   └── style_magical_glow.png
├── exports/                   # UE rendered videos
├── outputs/                   # ComfyUI styled results
├── levl_ue_to_comfy_server.py   # MCP server
└── ue_to_comfy_oneclick.py      # CLI orchestrator
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd /Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project

# Create virtual environment (if not exists)
python3 -m venv .venv
source .venv/bin/activate

# Install MCP server
pip install 'mcp[server]' fastmcp

# Install ComfyUI dependencies (if needed)
pip install torch torchvision opencv-python pillow
```

### 2. Setup Unreal Engine

1. **Enable Python Plugin**:
   - Edit → Plugins → Search "Python"
   - Enable "Python Editor Script Plugin"
   - Restart Unreal Engine

2. **Copy Watcher Script**:
   ```bash
   cp UE_Content_Python/LevlBridgeWatcherOneClick.py \
      /path/to/YourUEProject/Content/Python/
   ```

3. **Create Bridge Folders in UE Project**:
   ```bash
   mkdir -p /path/to/YourUEProject/LevlStudioBridge/inbox
   mkdir -p /path/to/YourUEProject/LevlStudioBridge/outbox
   ```

### 3. Start Services

#### Terminal 1: MCP Server
```bash
cd /Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project
source .venv/bin/activate

export UE_BRIDGE="./UnrealBridge"
export COMFY_HOST="127.0.0.1"
export COMFY_PORT="8188"

python3 levl_ue_to_comfy_server.py \
  --ue_bridge "$UE_BRIDGE" \
  --comfy_host 127.0.0.1 \
  --comfy_port 8188
```

#### Terminal 2: ComfyUI
```bash
cd /path/to/ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```

### 4. Configure VS Code

The tasks are already configured in `.vscode/tasks.json`. Available tasks:
- **UE → Comfy: One-Click Build+Render+Style** - Main pipeline
- **Start MCP Server** - Launch the bridge server
- **Install MCP Dependencies** - Setup Python packages
- **Test UE Bridge Connection** - Verify communication
- **Clear Bridge Queue** - Clean up queue files

## 🎬 Usage

### One-Click Pipeline

1. **In VS Code**: 
   - Press `Cmd+Shift+P` → "Tasks: Run Task"
   - Select "UE → Comfy: One-Click Build+Render+Style"
   - Enter parameters:
     - UE Level path (e.g., `/Game/The13thNight/Maps/SantaVillage`)
     - Blueprint to spawn (e.g., `/Game/The13thNight/Blueprints/BP_Nimble`)
     - Style image (select from dropdown)
     - Shot name (e.g., `Shot01`)
     - Spawn location/rotation
     - Resolution and FPS

2. **In Unreal Engine**:
   - Menu → Levl Bridge → Run Once
   - Or: Start Auto-Poll (polls every 2 seconds)

3. **Results**:
   - UE render appears in `exports/`
   - Styled video appears in `outputs/`

### Manual CLI Usage

```bash
python3 ue_to_comfy_oneclick.py \
  --level "/Game/The13thNight/Maps/SantaVillage" \
  --bp_path "/Game/The13thNight/Blueprints/BP_Nimble" \
  --movie_out "./exports/nimble_test.mp4" \
  --style_img "./refs/style_festive_night.png" \
  --location "0,0,100" \
  --rotation "0,0,0" \
  --resolution "1920x1080" \
  --fps 24
```

## 🎨 Style References

Create style images in `refs/` folder:
- **style_festive_night.png** - Christmas night atmosphere
- **style_ice_crystal.png** - Frozen/crystalline look
- **style_magical_glow.png** - Ethereal magical lighting
- **style_dark_forest.png** - Dark mysterious forest
- **style_candy_cane.png** - Candy/sweet aesthetic

Recommended: 1024x1024 or 512x512 PNG format

## 🔧 Customization

### Camera Settings
Edit spawn location and rotation in the VS Code task or modify defaults in `LevlBridgeWatcherOneClick.py`:
```python
cine = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.CineCameraActor, 
    unreal.Vector(0,-500,300),  # Camera position
    unreal.Rotator(-10,0,0)      # Camera rotation
)
```

### Sequence Duration
Modify in `LevlBridgeWatcherOneClick.py`:
```python
cut_section.set_end_frame_bounded(fps*4)  # 4 seconds
```

### ComfyUI Workflow
Edit `comfy_workflows/wanfn_depth_pose_canny_template.json`:
- Adjust `style_strength` (0-1) for style intensity
- Modify `temporal_consistency` (0-1) for frame coherence
- Change color correction values

### Output Settings
- **UE Output**: Configure in MRQ settings (PNG sequence or MP4)
- **ComfyUI Output**: Set codec, quality in workflow node 9

## 🐛 Troubleshooting

### MCP Server Not Responding
```bash
# Check if running
lsof -i :8765

# Restart with debug
python3 levl_ue_to_comfy_server.py --debug
```

### UE Not Processing Commands
1. Check bridge folders exist in UE project
2. Verify Python plugin enabled
3. Check UE console for errors (`Window → Developer Tools → Output Log`)
4. Manually run: `import LevlBridgeWatcherOneClick; LevlBridgeWatcherOneClick.run_bridge_once()`

### ComfyUI Not Receiving
1. Verify ComfyUI running on port 8188
2. Check workflow JSON exists
3. Test ComfyUI API:
   ```bash
   curl http://127.0.0.1:8188/system_stats
   ```

### File Paths Issues
- Use forward slashes in UE paths: `/Game/...`
- Use absolute paths for file system: `/Users/...`
- Check `exports/` and `outputs/` folders exist

## 📊 Performance Tips

- **Resolution**: Start with 1280x720 for testing
- **FPS**: 24fps is standard, 30fps for smoother motion
- **Batch Size**: Adjust in ComfyUI workflow (node 7)
- **GPU Memory**: Monitor with `nvidia-smi` or Activity Monitor

## 🎯 Example Workflows

### Character Turntable
```bash
--location "0,0,100" --rotation "0,0,0" --sequence "Turntable" --fps 30
```

### Environment Flythrough
```bash
--level "/Game/Environments/SantaVillage" --location "1000,0,500" --fps 24
```

### Action Sequence
```bash
--bp_path "/Game/BP/BP_EvilElf" --location "0,500,0" --rotation "0,180,0"
```

## 📚 Advanced Features

### Auto-Polling
In UE, enable auto-polling to avoid manual triggering:
```python
import LevlBridgeWatcherOneClick as LB
LB.start_auto_poll(2.0)  # Poll every 2 seconds
```

### Multiple Shots
Create a batch script:
```python
shots = [
    {"bp": "BP_Nimble", "loc": "0,0,100"},
    {"bp": "BP_Pip", "loc": "200,0,100"},
    {"bp": "BP_Jingles", "loc": "-200,0,100"}
]
for shot in shots:
    # Call ue_to_comfy_oneclick for each
```

### Custom Workflows
Create variations in `comfy_workflows/`:
- `wanfn_anime_style.json` - Anime aesthetic
- `wanfn_photorealistic.json` - Realistic rendering
- `wanfn_painterly.json` - Artistic painting style

## 🔗 Integration Points

- **Blender**: Export FBX → Import to UE as Blueprint
- **Tripo3D**: Generate → Export GLB → Convert to UE Blueprint
- **Character Pipeline**: Blender rig → UE Control Rig → Render → Style

## 📝 Notes

- The bridge uses file-based queuing for reliability
- MRQ renders PNG sequence by default (more reliable than direct MP4)
- ComfyUI workflow uses depth, pose, and edge detection for better style transfer
- Results are non-destructive - originals preserved in `exports/`

---

*LevlStudio One-Click Pipeline v1.0 - The 13th Night Project*
