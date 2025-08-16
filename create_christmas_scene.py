#!/usr/bin/env python3
"""
Christmas Scene Creator for Blender
Run this script in Blender to create a Christmas scene with your characters
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

def import_character_models():
    """Import available character models"""
    # Get project root (parent of this script)
    script_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    assets_dir = script_path / "assets" / "characters"
    
    imported_characters = []
    
    # Characters to import (these have 3D models available)
    characters_with_models = [
        ("char_nimble", "char_nimble_v001.fbx"),
        ("char_marzipan_maw", "char_marzipan_maw_v001.fbx"),
        ("char_crinkle", "char_crinkle_v001.fbx")
    ]
    
    positions = [
        (-3, 1, 0),   # Nimble on the left
        (0, 0, 0),    # Marzipan in center
        (3, -1, 0)    # Crinkle on the right
    ]
    
    for i, (char_name, fbx_file) in enumerate(characters_with_models):
        char_dir = assets_dir / char_name
        fbx_path = char_dir / fbx_file
        
        if fbx_path.exists():
            print(f"📥 Importing {char_name}...")
            
            # Import FBX
            bpy.ops.import_scene.fbx(filepath=str(fbx_path))
            
            # Get the imported object(s)
            imported_objects = bpy.context.selected_objects
            if imported_objects:
                main_obj = imported_objects[0]
                main_obj.name = f"{char_name}_character"
                
                # Position the character
                main_obj.location = positions[i] if i < len(positions) else (i*2, 0, 0)
                main_obj.rotation_euler = (0, 0, 0)
                main_obj.scale = (1, 1, 1)
                
                imported_characters.append(main_obj)
                print(f"✅ {char_name} imported at {main_obj.location}")
                
                # Try to apply textures
                apply_character_textures(main_obj, char_dir)
        else:
            print(f"⚠️ {char_name} FBX not found at {fbx_path}")
    
    return imported_characters

def apply_character_textures(character_obj, char_dir):
    """Apply textures to character if available"""
    tex_dir = char_dir / "tex"
    if not tex_dir.exists():
        return
    
    # Look for texture files
    texture_files = list(tex_dir.glob("*.png")) + list(tex_dir.glob("*.jpg"))
    if not texture_files:
        return
    
    # Create material
    material = bpy.data.materials.new(name=f"{character_obj.name}_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    # Add output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # Link them
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Try to load a base color texture
    for texture_file in texture_files:
        if any(keyword in texture_file.name.lower() for keyword in ['basecolor', 'color', 'diffuse']):
            tex_image = nodes.new(type='ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(str(texture_file))
            tex_image.location = (-300, 0)
            links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
            print(f"📸 Applied texture: {texture_file.name}")
            break
    
    # Assign material to object
    if character_obj.data.materials:
        character_obj.data.materials[0] = material
    else:
        character_obj.data.materials.append(material)

def create_environment():
    """Create a simple Christmas environment"""
    
    # Add ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    # Create ground material
    ground_mat = bpy.data.materials.new(name="Ground_Material")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (0.9, 0.9, 1.0, 1.0)  # Snow white
        principled.inputs['Roughness'].default_value = 0.8
    ground.data.materials.append(ground_mat)
    
    # Add some Christmas trees (simple cones)
    tree_positions = [(-8, 5, 0), (8, 6, 0), (-6, -8, 0), (7, -7, 0)]
    
    for i, pos in enumerate(tree_positions):
        # Tree trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=2, location=(pos[0], pos[1], 1))
        trunk = bpy.context.active_object
        trunk.name = f"Tree_Trunk_{i+1}"
        
        # Tree foliage (cone)
        bpy.ops.mesh.primitive_cone_add(radius1=2, depth=4, location=(pos[0], pos[1], 3.5))
        foliage = bpy.context.active_object
        foliage.name = f"Tree_Foliage_{i+1}"
        
        # Tree material
        tree_mat = bpy.data.materials.new(name=f"Tree_Material_{i+1}")
        tree_mat.use_nodes = True
        nodes = tree_mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        if principled:
            principled.inputs['Base Color'].default_value = (0.1, 0.4, 0.1, 1.0)  # Dark green
        
        foliage.data.materials.append(tree_mat)
    
    print("🌲 Christmas environment created")

def setup_lighting():
    """Set up Christmas-themed lighting"""
    
    # Remove default light
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    # Main moonlight (key light)
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.name = "Moonlight"
    key_light.data.energy = 2.0
    key_light.data.color = (0.8, 0.9, 1.0)  # Cool moonlight
    key_light.rotation_euler = (0.8, 0.2, 0.5)
    
    # Warm fill light (firelight)
    bpy.ops.object.light_add(type='AREA', location=(-4, 3, 3))
    fill_light = bpy.context.active_object
    fill_light.name = "Firelight"
    fill_light.data.energy = 80.0
    fill_light.data.color = (1.0, 0.7, 0.4)  # Warm orange
    fill_light.data.size = 4.0
    
    # Christmas lights (colorful accent lights)
    christmas_colors = [
        (1.0, 0.2, 0.2),  # Red
        (0.2, 1.0, 0.2),  # Green  
        (0.2, 0.4, 1.0),  # Blue
        (1.0, 1.0, 0.2)   # Yellow
    ]
    
    for i, color in enumerate(christmas_colors):
        x = -4 + i * 2.5
        bpy.ops.object.light_add(type='POINT', location=(x, -4, 2))
        xmas_light = bpy.context.active_object
        xmas_light.name = f"Christmas_Light_{i+1}"
        xmas_light.data.energy = 15.0
        xmas_light.data.color = color
    
    print("💡 Christmas lighting setup complete")

def setup_camera():
    """Set up camera for the scene"""
    
    # Remove default camera
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    
    # Main camera - cinematic angle
    bpy.ops.object.camera_add(location=(8, -8, 5))
    camera = bpy.context.active_object
    camera.name = "Main_Camera"
    camera.rotation_euler = (1.0, 0, 0.785)  # Look down towards characters
    
    # Camera settings
    camera.data.lens = 35  # Wide angle
    camera.data.sensor_width = 36
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print("📷 Camera setup complete")

def add_animation():
    """Add simple animation to the scene"""
    camera = bpy.context.scene.camera
    if camera:
        # Set frame range
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 150  # ~6 seconds at 24fps
        
        # Animate camera orbit
        bpy.context.scene.frame_set(1)
        camera.rotation_euler[2] = 0.785  # Starting rotation
        camera.keyframe_insert(data_path="rotation_euler", index=2)
        
        bpy.context.scene.frame_set(150)
        camera.rotation_euler[2] = 0.785 + 6.28318  # Full rotation + starting position
        camera.keyframe_insert(data_path="rotation_euler", index=2)
        
        # Set interpolation to linear
        if camera.animation_data:
            for fcurve in camera.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'LINEAR'
        
        print("🎬 Camera animation added")

def setup_render_settings():
    """Configure render settings"""
    scene = bpy.context.scene
    
    # Use Cycles for better quality
    scene.render.engine = 'CYCLES'
    
    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Quality settings
    scene.cycles.samples = 64  # Reasonable quality
    
    # Output
    scene.render.image_settings.file_format = 'PNG'
    
    print("🎬 Render settings configured")

def main():
    """Main function to create the Christmas scene"""
    print("🎄 Creating LevlStudio Christmas Scene...")
    print("=" * 50)
    
    # Build the scene step by step
    clear_scene()
    characters = import_character_models()
    create_environment()
    setup_lighting()
    setup_camera()
    add_animation()
    setup_render_settings()
    
    print("\n✅ Christmas scene creation complete!")
    print(f"📋 Scene contains:")
    print(f"   - {len(characters)} characters")
    print(f"   - Christmas environment with trees")
    print(f"   - Cinematic lighting setup")
    print(f"   - Animated camera")
    print("\n🎬 Ready to render!")
    print("   Press F12 to render a still image")
    print("   Press Ctrl+F12 to render animation")

# Run the script
if __name__ == "__main__":
    main()