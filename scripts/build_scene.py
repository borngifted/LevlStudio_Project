#!/usr/bin/env python3
"""
Scene Builder Script
Programmatically build scenes from JSON configuration
Can be run from VS Code or command line
"""

import bpy
import os
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def load_json_configs():
    """Load assets and scenes JSON files"""
    assets_path = PROJECT_ROOT / "json" / "assets.json"
    scenes_path = PROJECT_ROOT / "json" / "scenes.json"
    
    with open(assets_path, 'r') as f:
        assets = json.load(f)
    
    with open(scenes_path, 'r') as f:
        scenes = json.load(f)
    
    return assets, scenes

def build_scene(scene_name=None):
    """Build a specific scene or the first available one"""
    assets, scenes = load_json_configs()
    
    # Get scene data
    scene_data = None
    if scene_name:
        for scene in scenes['scenes']:
            if scene['name'] == scene_name:
                scene_data = scene
                break
    else:
        # Use first scene if no name specified
        scene_data = scenes['scenes'][0] if scenes['scenes'] else None
    
    if not scene_data:
        print(f"Scene '{scene_name}' not found")
        return False
    
    print(f"Building scene: {scene_data['name']}")
    
    # Clear existing scene
    bpy.ops.wm.read_homefile(use_empty=True)
    
    # Create main collection
    scene_collection = bpy.data.collections.new(name=f"SCENE_{scene_data['name']}")
    bpy.context.scene.collection.children.link(scene_collection)
    
    # Apply scene settings
    scene = bpy.context.scene
    settings = scene_data.get('scene_settings', {})
    
    scene.frame_start = settings.get('frame_start', 1)
    scene.frame_end = settings.get('frame_end', 250)
    scene.render.fps = settings.get('fps', 24)
    scene.render.resolution_x = settings.get('resolution_x', 1920)
    scene.render.resolution_y = settings.get('resolution_y', 1080)
    
    # Import environment
    env_id = scene_data.get('environment')
    if env_id and env_id in assets['environments']:
        env_data = assets['environments'][env_id]
        print(f"  - Loading environment: {env_id}")
        # Import logic here
    
    # Import characters
    for char_id in scene_data.get('characters', []):
        if char_id in assets['characters']:
            char_data = assets['characters'][char_id]
            print(f"  - Loading character: {char_id}")
            # Import logic here
    
    # Import props
    for prop_id in scene_data.get('props', []):
        if prop_id in assets['props']:
            prop_data = assets['props'][prop_id]
            print(f"  - Loading prop: {prop_id}")
            # Import logic here
    
    # Setup lighting
    preset_name = scene_data.get('lighting_preset', 'night_time')
    if preset_name in assets['lighting_presets']:
        preset = assets['lighting_presets'][preset_name]
        print(f"  - Applying lighting preset: {preset_name}")
        
        # Create sun light
        sun_data = bpy.data.lights.new(name=f"Sun_{preset_name}", type='SUN')
        sun_data.energy = preset.get('sun_energy', 1.0)
        sun_data.color = preset.get('sun_color', [1, 1, 1])
        
        sun_obj = bpy.data.objects.new(name=f"Sun_{preset_name}", object_data=sun_data)
        sun_obj.rotation_euler = preset.get('sun_angle', [0, 0, 0])
        scene_collection.objects.link(sun_obj)
    
    # Setup fog
    fog_density = scene_data.get('fog_density', 0.02)
    if fog_density > 0:
        print(f"  - Adding volumetric fog (density: {fog_density})")
        create_volumetric_fog(fog_density, scene_collection)
    
    # Save the scene
    output_path = PROJECT_ROOT / "scenes" / f"{scene_data['name'].replace(' ', '_')}.blend"
    output_path.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    print(f"Scene saved to: {output_path}")
    
    return True

def create_volumetric_fog(density, collection):
    """Create volumetric fog in the scene"""
    # Create cube for volume
    mesh = bpy.data.meshes.new(name="Fog_Mesh")
    obj = bpy.data.objects.new(name="VolumetricFog", object_data=mesh)
    collection.objects.link(obj)
    
    # Create mesh
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_cube_add(size=100)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create volume material
    mat = bpy.data.materials.new(name="Fog_Volume")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled_volume = nodes.new('ShaderNodeVolumePrincipled')
    
    principled_volume.inputs["Density"].default_value = density
    principled_volume.inputs["Color"].default_value = (0.8, 0.85, 1.0, 1.0)
    
    links.new(principled_volume.outputs["Volume"], output.inputs["Volume"])
    
    obj.data.materials.append(mat)

def main():
    """Main entry point"""
    # Get scene name from command line arguments if provided
    scene_name = None
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        if args:
            scene_name = " ".join(args)
    
    # Build the scene
    success = build_scene(scene_name)
    
    if success:
        print("Scene build completed successfully!")
    else:
        print("Scene build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
