#!/usr/bin/env python3
"""
Batch processing script for LevlStudio Scene Builder
Run with: blender -b --python batch_process.py
"""

import bpy
import sys
import os
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Import and register the addon
import levlstudio_scene_builder_addon
levlstudio_scene_builder_addon.register()

def setup_scene():
    """Basic scene setup"""
    # Clear default scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Set render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Set output format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

def build_scene_from_json(scene_index=0):
    """Build a specific scene from JSON files"""
    props = bpy.context.scene.levlstudio_props
    
    # Set JSON file paths
    props.assets_json_path = str(project_dir / "json" / "assets.json")
    props.scenes_json_path = str(project_dir / "json" / "scenes.json")
    
    # Load JSON files
    bpy.ops.levlstudio.load_json()
    
    # Select and build scene
    props.selected_scene = str(scene_index)
    bpy.ops.levlstudio.build_scene()
    
    print(f"Built scene index {scene_index}")

def export_scene(output_path, format='GLB'):
    """Export the current scene"""
    output_file = Path(output_path)
    
    if format == 'FBX':
        bpy.ops.export_scene.fbx(filepath=str(output_file))
    elif format in ['GLB', 'GLTF']:
        bpy.ops.export_scene.gltf(filepath=str(output_file))
    
    print(f"Exported to {output_file}")

def render_scene(output_path):
    """Render the current scene"""
    bpy.context.scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered to {output_path}")

def batch_process_all_scenes():
    """Process all scenes defined in scenes.json"""
    import json
    
    # Load scenes.json to get scene count
    scenes_json_path = project_dir / "json" / "scenes.json"
    with open(scenes_json_path, 'r') as f:
        data = json.load(f)
        scenes = data.get('scenes', [])
    
    for i, scene_data in enumerate(scenes):
        print(f"\nProcessing scene {i}: {scene_data.get('name', 'Unknown')}")
        
        # Clear scene
        setup_scene()
        
        # Build scene
        build_scene_from_json(i)
        
        # Export
        export_dir = project_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        
        scene_name = scene_data.get('name', f'scene_{i}').replace(' ', '_')
        export_path = export_dir / f"{scene_name}.glb"
        export_scene(export_path, 'GLB')
        
        # Render
        render_dir = project_dir / "renders"
        render_dir.mkdir(exist_ok=True)
        
        render_path = render_dir / f"{scene_name}.png"
        render_scene(render_path)
    
    print("\nBatch processing complete!")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LevlStudio Batch Processor')
    parser.add_argument('--scene', type=int, default=0, help='Scene index to build')
    parser.add_argument('--export', type=str, help='Export path')
    parser.add_argument('--render', type=str, help='Render output path')
    parser.add_argument('--batch', action='store_true', help='Process all scenes')
    
    # Parse args from sys.argv (skip Blender's args)
    blender_args_end = sys.argv.index('--') if '--' in sys.argv else len(sys.argv)
    args = parser.parse_args(sys.argv[blender_args_end + 1:])
    
    if args.batch:
        batch_process_all_scenes()
    else:
        setup_scene()
        build_scene_from_json(args.scene)
        
        if args.export:
            export_scene(args.export)
        
        if args.render:
            render_scene(args.render)

if __name__ == "__main__":
    main()
