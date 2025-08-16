# LevlStudio Pipeline Rules for Void AI Agent

## 🎬 Core Pipeline Overview
This is a **LevlStudio One-Click Pipeline** that creates AI-styled videos from Unreal Engine renders using ComfyUI. The workflow is: UE5 → MCP Bridge → ComfyUI → Styled Output.

## 🔧 System Architecture
- **MCP Server**: http://127.0.0.1:8765 (bridges UE and ComfyUI)
- **ComfyUI**: http://127.0.0.1:8188 (AI style transfer)
- **UE Bridge**: `./UnrealBridge/inbox` and `./UnrealBridge/outbox`
- **Exports**: `./exports/` (UE renders)
- **Outputs**: `./outputs/` (final styled videos)

## 🎯 Default Settings & Preferences

### Unreal Engine Defaults
- **Level**: `/Game/Levl/Maps/Empty`
- **Blueprint**: `/Game/The13thNight/Blueprints/BP_Nimble`
- **Spawn Location**: `0,0,100` (X,Y,Z coordinates)
- **Resolution**: `1280x720` (good for testing, use 1920x1080 for final)
- **FPS**: `24` (cinematic standard)
- **Duration**: 4 seconds (96 frames at 24fps)

### ComfyUI Workflow Settings
- **Workflow**: `comfy_workflows/wanfn_depth_pose_canny_template.json`
- **Style Strength**: 0.8 (balance between style and original)
- **Control Weights**:
  - Depth: 0.4 (spatial understanding)
  - Pose: 0.35 (character preservation) 
  - Canny: 0.25 (edge preservation)

### Available Characters
- `BP_Nimble` - Main character, elf helper
- `BP_Pip` - Small character
- `BP_Jingles` - Holiday character
- `BP_Fenn` - Forest character
- `BP_Jax` - Action character
- `BP_Santa` - Holiday character

### Available Styles
- `style_festive_night.png` - Christmas/holiday atmosphere
- `style_ice_crystal.png` - Frozen/winter theme
- `style_magical_glow.png` - Ethereal/fantasy lighting
- `style_dark_forest.png` - Mysterious/dramatic
- `style_candy_cane.png` - Sweet/colorful theme

## 🚀 Command Preferences

### For Quick Tests
Always prefer `ue:oneclick` command with these settings:
- Level: `/Game/Levl/Maps/Empty`
- Resolution: `1280x720`
- FPS: `24`
- Location: `0,0,100`

### For Final Renders
Use higher quality settings:
- Resolution: `1920x1080` or `2560x1440`
- Consider FPS: `30` for smoother motion

## 🎨 Style Application Guidelines

### Style Strength Recommendations
- **Light styling**: 0.6-0.7 (preserves more original)
- **Balanced styling**: 0.8 (recommended default)
- **Heavy styling**: 0.9-1.0 (strong artistic effect)

### Character-Specific Recommendations
- **BP_Nimble**: Works well with `magical_glow` and `festive_night`
- **BP_Santa**: Perfect with `festive_night` and `ice_crystal`
- **BP_Jax**: Good with `dark_forest` for dramatic effect

## 🔄 Workflow Commands

### Start Services
1. Always check status first: `mcp:status`
2. If ComfyUI not running: `comfy:start`
3. If MCP not running: `mcp:start`

### Main Pipeline
- Use `ue:oneclick` for end-to-end workflow
- For direct ComfyUI only: `comfy:direct`

### Troubleshooting
- Test UE connection: `ue:bridge:test`
- Clean queue: `pipeline:clean`
- Check results: `results:open`

## 🎭 Scene Composition Rules

### Camera Positioning
- Default camera is positioned relative to spawned actor
- Camera offset: `(actor.x, actor.y - 500, actor.z + 200)`
- Camera angle: `-10°` downward tilt for cinematic look

### Lighting
- Scenes use default UE lighting
- Style transfer handles lighting mood
- Consider time-of-day for outdoor scenes

## 🚨 Important Constraints

### File Paths
- Always use forward slashes in UE paths: `/Game/...`
- Use relative paths for project files: `./exports/`, `./refs/`
- Avoid spaces in file names

### Timing
- UE renders take 30s-5min depending on complexity
- ComfyUI processing takes 1-3min for 4-second clips
- Always wait for one step to complete before next

### Error Handling
- If UE bridge fails, check that Python plugin is enabled in UE
- If ComfyUI fails, verify workflow JSON exists
- If MCP fails, check port 8765 is available

## 🎯 Agent Behavior Guidelines

### When User Asks for Renders
1. **Check status** first with `mcp:status`
2. **Use defaults** unless user specifies otherwise
3. **Prefer one-click** pipeline over manual steps
4. **Show progress** and explain what's happening

### When User Wants Style Changes
1. **List available styles** from the options above
2. **Suggest combinations** based on character/mood
3. **Use direct ComfyUI** if they have existing video

### When User Wants Batch Processing
1. **Use batch commands** for multiple characters/styles
2. **Warn about time** - batch jobs take longer
3. **Suggest overnight** for large batches

### Communication Style
- Use **emojis** to match the command categories
- **Explain steps** in pipeline when running commands
- **Provide estimates** for render times
- **Suggest optimizations** for faster iteration

## 🔧 Advanced Customization

### Workflow Modifications
- Edit `comfy_workflows/wanfn_depth_pose_canny_template.json` for:
  - Style strength adjustments
  - Control weight changes
  - Output format/quality settings

### UE Customization
- Modify `UE_Content_Python/LevlBridgeWatcherOneClick.py` for:
  - Camera positioning
  - Sequence duration
  - Render settings

### Pipeline Extensions
- Add new styles to `refs/` folder
- Create new characters in UE and reference as `BP_YourCharacter`
- Extend MCP server with custom tools

Remember: This is a **creative pipeline** - encourage experimentation while maintaining reliable defaults!