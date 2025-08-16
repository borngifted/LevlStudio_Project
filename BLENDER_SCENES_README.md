# 🎭 LevlStudio Blender Scenes

Create cinematic scenes in Blender using your existing character assets!

## 🚀 Quick Start

### Interactive Mode
```bash
python3 blender_scene_runner.py
```

### Command Line
```bash
# Christmas scene
python3 blender_scene_runner.py --scene christmas

# Character showcase
python3 blender_scene_runner.py --scene showcase

# Background mode (no Blender UI)
python3 blender_scene_runner.py --scene christmas --background
```

## 🎬 Available Scenes

### 1. Christmas Scene (`create_christmas_scene.py`)
- **Characters**: Nimble, Marzipan Maw, Crinkle
- **Environment**: Snowy ground with Christmas trees
- **Lighting**: Moonlight + warm firelight + colorful Christmas lights
- **Animation**: Rotating camera around scene
- **Duration**: ~6 seconds

### 2. Character Showcase (`create_character_showcase.py`)
- **Characters**: All available characters (up to 8)
- **Layout**: Circular arrangement facing center
- **Environment**: Professional backdrop with dramatic lighting
- **Animation**: Orbiting camera for 360° view
- **Duration**: ~8 seconds

## 📁 Your Character Assets

The scripts automatically detect and use these characters:

### Characters with 3D Models:
- **char_nimble** - Has `char_nimble_v001.fbx` + textures
- **char_marzipan_maw** - Has `char_marzipan_maw_v001.fbx` + textures  
- **char_crinkle** - Has `char_crinkle_v001.fbx`

### Characters with Reference Images:
- char_caroler, char_fenn, char_glitch, char_jax, char_pip, char_wrath_wrangler

## 🎨 Scene Features

### Automatic Asset Detection
- Scans `assets/characters/` for FBX, GLB, and Blend files
- Applies textures from `tex/` folders automatically
- Handles missing files gracefully

### Cinematic Lighting
- **Christmas**: Moonlight + firelight + colored accent lights
- **Showcase**: Key light + fill light + rim light + accent colors

### Professional Camera Work
- Multiple camera angles and movements
- Animated camera orbits
- Proper lens settings (35mm wide, 50mm standard, 85mm portrait)

### High-Quality Rendering
- Cycles render engine
- 1920x1080 resolution
- Optimized sample counts
- PNG output format

## 🔧 Manual Usage

If you want to run scripts directly in Blender:

```bash
# Open Blender and run script in Text Editor
blender --python create_christmas_scene.py

# Or run headless
blender --background --python create_christmas_scene.py
```

## 🎯 Rendering Your Scenes

Once a scene is loaded in Blender:

1. **Still Image**: Press `F12`
2. **Animation**: Press `Ctrl+F12` 
3. **View Result**: Press `F11` to see rendered image
4. **Save**: File → Export → PNG/MP4

## 🛠️ Customization

### Adding New Characters
1. Place FBX/GLB/Blend files in `assets/characters/your_character/`
2. Add textures to `assets/characters/your_character/tex/`
3. Scripts will automatically detect and import them

### Modifying Scenes
Edit the Python scripts to:
- Change character positions
- Adjust lighting colors/intensity
- Modify camera movements
- Add new environment elements

### Creating New Scenes
Use `blender_scene_builder.py` as a base class:

```python
from blender_scene_builder import LevlStudioSceneBuilder

builder = LevlStudioSceneBuilder()
builder.import_character("char_nimble", (0, 0, 0))
builder.setup_cinematic_lighting("dramatic")
builder.create_camera_setup("cinematic")
```

## 🎬 Integration with AI Workflow

These Blender scenes integrate with your complete AI-to-3D pipeline:

1. **AI Generated Images** → 3D Models
2. **Blender Processing** → Clean meshes + materials
3. **Scene Creation** → Cinematic lighting + animation  
4. **Render Output** → Ready for ComfyUI style transfer

## 📊 Scene Statistics

| Scene | Characters | Lights | Duration | Complexity |
|-------|------------|--------|----------|------------|
| Christmas | 3 | 6 | 6s | Medium |
| Showcase | 1-8 | 7 | 8s | High |

## 🎉 Ready to Create!

Your character assets are ready to star in cinematic Blender scenes. Run the scripts and watch your characters come to life!