# LevlStudio Scene Builder - The 13th Night Project

## Overview
A comprehensive Blender pipeline for managing 3D assets with JSON-driven scene assembly, VS Code integration, and AI assistance capabilities.

## Features
- **JSON-Driven Asset Management**: Define all assets and scenes in JSON files with transform defaults
- **VS Code Integration**: Debug Blender addons directly from VS Code
- **Resolve Reporting**: Track which assets loaded successfully and which need attention
- **Transform Defaults**: Automatically position, rotate, and scale assets on import
- **Material Presets**: Pre-configured snow, ice, brass, and wood materials
- **Lighting Presets**: Multiple time-of-day lighting configurations
- **AI Integration Stub**: Ready for OpenAI/Gemini API integration

## Installation

### 1. Install the Blender Addon
1. Open Blender
2. Go to Edit → Preferences → Add-ons
3. Click "Install..." and navigate to `levlstudio_scene_builder_addon.py`
4. Enable "LevlStudio Scene Builder Enhanced"

### 2. Set Up VS Code Debugging (Optional)
1. Install the Blender Development extension in VS Code
2. Install debugpy in Blender's Python:
   ```bash
   # Mac/Linux
   /Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10 -m pip install debugpy
   
   # Windows
   "C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin\python.exe" -m pip install debugpy
   ```
3. Open the project folder in VS Code
4. Use the provided `.vscode/launch.json` configuration

## Project Structure
```
/LevlStudio_Project/
├── /assets/                      # All 3D assets organized by type
│   ├── /characters/              # Character models and rigs
│   ├── /props/                   # Props and objects
│   ├── /environments/            # Environment scenes
│   ├── /fx/                      # Effects and particles
│   ├── /materials/               # Material presets
│   └── /cameras/                 # Camera rigs
├── /tripo_exports/               # Raw exports from Tripo3D
├── /json/                        # Configuration files
│   ├── assets.json              # Asset definitions with transforms
│   └── scenes.json              # Scene compositions
├── /renders/                     # Output renders
├── /exports/                     # Final FBX/GLB exports
└── levlstudio_scene_builder_addon.py

```

## Usage

### Basic Workflow
1. **Load JSON Files**: 
   - In Blender's 3D Viewport, open the N-panel (press N)
   - Go to the "LevlStudio" tab
   - Browse to select `assets.json` and `scenes.json`
   - Click "Load JSON Files"

2. **Build a Scene**:
   - Select a scene from the dropdown
   - Optionally override camera and lighting
   - Click "Build Scene"
   - Check the Resolve Report to see what loaded

3. **Export**:
   - Click "Export Scene"
   - Choose FBX, GLB, or GLTF format
   - Select destination

### JSON Structure

#### assets.json
```json
{
  "assets": {
    "props": {
      "prop_glowing_book": {
        "type": "prop",
        "tags": ["magical", "runes"],
        "filepath": "//assets/props/prop_glowing_book/prop_glowing_book_v002.glb",
        "import_type": "import",
        "location": [0.0, 0.0, 0.5],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.2, 1.2, 1.2]
      }
    }
  }
}
```

#### scenes.json
```json
{
  "scenes": [
    {
      "name": "Santa Village Night Scene",
      "environment": "env_santa_village_night",
      "characters": ["char_nimble", "char_pip"],
      "props": ["prop_glowing_book"],
      "default_camera": "cam_fpv_drone_swoop",
      "lighting_preset": "night_snow"
    }
  ]
}
```

### Transform Defaults
Each asset can specify default transforms:
- `location`: [X, Y, Z] in Blender units
- `rotation`: [X, Y, Z] in radians
- `scale`: [X, Y, Z] scale factors

### Import Types
- `import`: Import the file (copies data)
- `link`: Link the file (references external data)
- `append`: Append from .blend file
- `link_or_import`: Try linking first, fall back to import

## VS Code Integration

### Debugging
1. In Blender's LevlStudio panel, click "Attach VS Code Debugger"
2. In VS Code, run the "Python: Attach to Blender" configuration
3. Set breakpoints in your addon code
4. Trigger addon functions in Blender

### Running Tasks
VS Code tasks are configured for:
- Installing the addon
- Running Blender with the addon
- Building test scenes
- Linting Python files

Access tasks with Cmd+Shift+P → "Tasks: Run Task"

## Resolve Report
The Resolve Report shows how each asset was handled:
- ✓ **SUCCESS**: Asset loaded correctly
- ⚠️ **PROCEDURAL**: Placeholder created (file missing)
- ❌ **ERROR**: Failed to load

Toggle "Show Resolve Report" to see details for troubleshooting.

## AI Integration
The AI Assistant button is a stub for future integration:
1. Replace the stub in `LEVLSTUDIO_OT_ai_assist` with your API calls
2. Use environment tags to generate contextual suggestions
3. Example services: OpenAI GPT-4, Google Gemini, local LLMs

## Material Presets
Pre-configured materials:
- **Snow**: White with subsurface scattering
- **Ice**: Transparent with refraction
- **Brass**: Metallic gold/bronze
- **Wood**: Organic brown with roughness

## Lighting Presets
Available lighting configurations:
- **night_snow**: Cool blue moonlight with fog
- **dark_interior**: Minimal ambient light
- **magical_glow**: Warm magical atmosphere
- **dawn**: Orange/pink sunrise
- **midday**: Bright neutral daylight

## Troubleshooting

### Assets Not Loading
1. Check file paths in assets.json
2. Ensure paths use "//" prefix for relative paths
3. Check Resolve Report for specific errors

### VS Code Debugging Not Working
1. Ensure debugpy is installed in Blender's Python
2. Check firewall isn't blocking port 5678
3. Verify VS Code Python extension is installed

### Placeholders Instead of Assets
- This means the file path couldn't be found
- Update the filepath in assets.json
- Ensure the file exists at the specified location

## Advanced Features

### Custom Material Node Groups
Create reusable material setups:
1. Create materials with node groups in .blend files
2. Reference them in assets.json with `node_group` property
3. Use `import_type: "append"` to bring them in

### Batch Processing
Use the headless Blender task to process multiple scenes:
```bash
blender -b --python batch_process.py
```

### LLM Integration Examples
```python
# In the AI assist operator
import openai

def get_lighting_suggestions(tags):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a 3D lighting expert"},
            {"role": "user", "content": f"Suggest lighting for: {tags}"}
        ]
    )
    return response.choices[0].message.content
```

## Best Practices
1. **Version Control**: Use Git to track JSON changes
2. **Naming Convention**: Use descriptive names with version suffixes (_v001, _v002)
3. **Collections**: Organize .blend files with named collections for linking
4. **Transform Origins**: Set object origins before exporting
5. **Scale**: Apply scale in Blender before exporting to avoid issues

## Support
For issues or questions:
1. Check the Resolve Report first
2. Enable Debug Mode for detailed logging
3. Use VS Code debugger to step through code
4. Review Blender's console for Python errors

---

*LevlStudio Scene Builder v2.0.0 - Built for The 13th Night Project*