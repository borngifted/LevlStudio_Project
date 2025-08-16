#!/usr/bin/env python3
"""
Create and Save Scene - Creates the scene and saves it as a .blend file
"""

import bpy
import bmesh
import mathutils
import sys
from pathlib import Path
from mathutils import Vector, Euler
import math

def clear_scene():
    """Clear the default Blender scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    print("✅ Scene cleared")

def discover_character_references():
    """Find character reference images"""
    script_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    assets_dir = script_path / "assets" / "characters"
    
    characters = []
    
    if assets_dir.exists():
        for char_dir in assets_dir.iterdir():
            if char_dir.is_dir():
                char_name = char_dir.name
                tex_dir = char_dir / "tex"
                
                if tex_dir.exists():
                    ref_images = (list(tex_dir.glob("*reference*")) + 
                                list(tex_dir.glob("*.png")) + 
                                list(tex_dir.glob("*.jpg")) + 
                                list(tex_dir.glob("*.jpeg")))
                    
                    if ref_images:
                        characters.append({
                            "name": char_name,
                            "dir": char_dir,
                            "reference": ref_images[0]
                        })
                        print(f"🔍 Found character: {char_name}")
    
    return characters

def create_character_proxy(char_info, position=(0, 0, 0), scale=1.0):
    """Create a proxy character using a plane with character reference image"""
    char_name = char_info["name"]
    reference_image = char_info["reference"]
    
    bpy.ops.mesh.primitive_plane_add(size=2*scale, location=position)
    char_plane = bpy.context.active_object
    char_plane.name = f"{char_name}_proxy"
    char_plane.rotation_euler = (1.5708, 0, 0)
    
    material = bpy.data.materials.new(name=f"{char_name}_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 0)
    
    try:
        tex_image.image = bpy.data.images.load(str(reference_image))
        links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
        print(f"📸 Loaded: {char_name}")
    except Exception as e:
        principled.inputs['Base Color'].default_value = (0.5, 0.7, 1.0, 1.0)
        print(f"⚠️ Used default color for {char_name}")
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    char_plane.data.materials.append(material)
    
    return char_plane

def create_scene():
    """Create the complete scene"""
    
    clear_scene()
    characters = discover_character_references()
    
    # Ground
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    # Characters in circle
    radius = 4
    num_chars = len(characters)
    for i, char in enumerate(characters):
        angle = (2 * math.pi * i) / num_chars
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 1
        create_character_proxy(char, (x, y, z), 1.0)
    
    # Lighting
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 5.0
    
    bpy.ops.object.light_add(type='AREA', location=(-3, 3, 5))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 80.0
    
    # Camera
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    
    bpy.ops.object.camera_add(location=(8, -8, 5))
    camera = bpy.context.active_object
    camera.name = "Main_Camera"
    camera.rotation_euler = (1.0, 0, 0.785)
    bpy.context.scene.camera = camera
    
    # Animation
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    
    bpy.context.scene.frame_set(1)
    camera.rotation_euler[2] = 0.785
    camera.keyframe_insert(data_path="rotation_euler", index=2)
    
    bpy.context.scene.frame_set(120)
    camera.rotation_euler[2] = 0.785 + 6.28318
    camera.keyframe_insert(data_path="rotation_euler", index=2)
    
    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    if hasattr(scene, 'cycles'):
        scene.cycles.samples = 64
    
    print(f"✅ Scene with {len(characters)} characters created!")

def save_scene():
    """Save the scene"""
    script_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    scenes_dir = script_path / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    
    scene_file = scenes_dir / "levlstudio_character_showcase.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    print(f"💾 Scene saved as: {scene_file}")
    
    return scene_file

def main():
    """Main function"""
    print("✨ Creating and Saving LevlStudio Character Scene...")
    print("=" * 60)
    
    try:
        create_scene()
        scene_file = save_scene()
        
        print(f"\n🎉 SUCCESS!")
        print(f"📁 Scene saved: {scene_file}")
        print(f"🎬 To open: blender {scene_file}")
        print(f"💡 Or double-click the .blend file")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()