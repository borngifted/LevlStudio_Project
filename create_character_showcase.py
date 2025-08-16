#!/usr/bin/env python3
"""
Character Showcase Creator for Blender
Displays all available characters in a circular arrangement
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

def discover_character_models():
    """Find all available character models"""
    script_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    assets_dir = script_path / "assets" / "characters"
    
    available_characters = []
    
    if assets_dir.exists():
        for char_dir in assets_dir.iterdir():
            if char_dir.is_dir():
                char_name = char_dir.name
                
                # Look for 3D model files
                fbx_files = list(char_dir.glob("*.fbx"))
                glb_files = list(char_dir.glob("*.glb"))
                blend_files = list(char_dir.glob("*.blend"))
                
                if fbx_files or glb_files or blend_files:
                    model_info = {
                        "name": char_name,
                        "dir": char_dir,
                        "fbx": fbx_files,
                        "glb": glb_files,
                        "blend": blend_files
                    }
                    available_characters.append(model_info)
                    print(f"🔍 Found character: {char_name}")
    
    print(f"📊 Total characters available: {len(available_characters)}")
    return available_characters

def import_character(char_info, position=(0, 0, 0), rotation=(0, 0, 0)):
    """Import a single character"""
    char_name = char_info["name"]
    char_dir = char_info["dir"]
    
    imported_object = None
    
    # Try FBX first, then GLB, then Blend
    if char_info["fbx"]:
        fbx_file = char_info["fbx"][0]
        print(f"📥 Importing FBX: {char_name}")
        bpy.ops.import_scene.fbx(filepath=str(fbx_file))
        if bpy.context.selected_objects:
            imported_object = bpy.context.selected_objects[0]
            
    elif char_info["glb"]:
        glb_file = char_info["glb"][0]
        print(f"📥 Importing GLB: {char_name}")
        bpy.ops.import_scene.gltf(filepath=str(glb_file))
        if bpy.context.selected_objects:
            imported_object = bpy.context.selected_objects[0]
            
    elif char_info["blend"]:
        blend_file = char_info["blend"][0]
        print(f"📥 Importing Blend: {char_name}")
        # Import objects from blend file
        with bpy.data.libraries.load(str(blend_file)) as (data_from, data_to):
            data_to.objects = data_from.objects[:1]  # Import first object
        
        if data_to.objects:
            obj = data_to.objects[0]
            bpy.context.collection.objects.link(obj)
            imported_object = obj
    
    if imported_object:
        # Position and name the character
        imported_object.location = position
        imported_object.rotation_euler = rotation
        imported_object.name = f"{char_name}_showcase"
        
        # Try to apply textures
        apply_character_materials(imported_object, char_dir)
        
        print(f"✅ {char_name} imported successfully")
        return imported_object
    
    print(f"❌ Failed to import {char_name}")
    return None

def apply_character_materials(character_obj, char_dir):
    """Apply materials and textures to character"""
    tex_dir = char_dir / "tex"
    if not tex_dir.exists():
        return
    
    # Find texture files
    texture_files = list(tex_dir.glob("*.png")) + list(tex_dir.glob("*.jpg")) + list(tex_dir.glob("*.jpeg"))
    
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
    
    # Look for base color texture
    base_color_texture = None
    for texture_file in texture_files:
        name_lower = texture_file.name.lower()
        if any(keyword in name_lower for keyword in ['basecolor', 'color', 'diffuse', 'base']):
            base_color_texture = texture_file
            break
    
    # If no specific base color found, use first available texture
    if not base_color_texture and texture_files:
        base_color_texture = texture_files[0]
    
    if base_color_texture:
        tex_image = nodes.new(type='ShaderNodeTexImage')
        tex_image.image = bpy.data.images.load(str(base_color_texture))
        tex_image.location = (-300, 0)
        links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
        print(f"📸 Applied texture: {base_color_texture.name}")
    
    # Assign material to object
    if character_obj.data and hasattr(character_obj.data, 'materials'):
        if character_obj.data.materials:
            character_obj.data.materials[0] = material
        else:
            character_obj.data.materials.append(material)

def create_showcase_environment():
    """Create a showcase environment"""
    
    # Add large ground plane
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Showcase_Ground"
    
    # Ground material
    ground_mat = bpy.data.materials.new(name="Showcase_Ground_Material")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (0.2, 0.2, 0.3, 1.0)  # Dark blue-gray
        principled.inputs['Metallic'].default_value = 0.0
        principled.inputs['Roughness'].default_value = 0.8
    ground.data.materials.append(ground_mat)
    
    # Add backdrop cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=20, depth=40, location=(0, 0, 20))
    backdrop = bpy.context.active_object
    backdrop.name = "Backdrop"
    
    # Backdrop material
    backdrop_mat = bpy.data.materials.new(name="Backdrop_Material")
    backdrop_mat.use_nodes = True
    nodes = backdrop_mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (0.1, 0.1, 0.2, 1.0)  # Very dark blue
        principled.inputs['Roughness'].default_value = 1.0
    backdrop.data.materials.append(backdrop_mat)
    
    print("🏛️ Showcase environment created")

def setup_showcase_lighting():
    """Set up dramatic lighting for character showcase"""
    
    # Remove default light
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    # Key light (main directional)
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 5.0
    key_light.data.color = (1.0, 0.95, 0.8)  # Warm white
    key_light.rotation_euler = (0.6, 0.3, 0.8)
    
    # Fill light (area light)
    bpy.ops.object.light_add(type='AREA', location=(-8, 5, 8))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 200.0
    fill_light.data.color = (0.7, 0.8, 1.0)  # Cool blue
    fill_light.data.size = 8.0
    
    # Rim light (back light)
    bpy.ops.object.light_add(type='SPOT', location=(0, 15, 10))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 300.0
    rim_light.data.color = (1.0, 0.9, 0.7)  # Warm rim
    rim_light.data.spot_size = 2.0
    rim_light.rotation_euler = (0.7, 0, 3.14)
    
    # Accent lights around the circle
    accent_positions = [(12, 0, 3), (0, 12, 3), (-12, 0, 3), (0, -12, 3)]
    accent_colors = [(1.0, 0.3, 0.3), (0.3, 1.0, 0.3), (0.3, 0.3, 1.0), (1.0, 1.0, 0.3)]
    
    for i, (pos, color) in enumerate(zip(accent_positions, accent_colors)):
        bpy.ops.object.light_add(type='POINT', location=pos)
        accent_light = bpy.context.active_object
        accent_light.name = f"Accent_Light_{i+1}"
        accent_light.data.energy = 50.0
        accent_light.data.color = color
    
    print("💡 Showcase lighting setup complete")

def setup_showcase_camera():
    """Set up camera for character showcase"""
    
    # Remove default camera
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    
    # Main camera - elevated view
    bpy.ops.object.camera_add(location=(12, -12, 8))
    camera = bpy.context.active_object
    camera.name = "Showcase_Camera"
    camera.rotation_euler = (1.1, 0, 0.785)
    
    # Camera settings
    camera.data.lens = 50  # Standard lens
    camera.data.sensor_width = 36
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print("📷 Showcase camera setup complete")

def add_showcase_animation():
    """Add rotating camera animation"""
    camera = bpy.context.scene.camera
    if camera:
        # Set frame range for 8 second loop at 24fps
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 192
        
        # Store original position
        original_location = camera.location.copy()
        
        # Calculate radius from center
        radius = math.sqrt(original_location.x**2 + original_location.y**2)
        height = original_location.z
        
        # Add location keyframes for circular motion
        for frame in range(1, 193, 8):  # Every 8 frames
            angle = (frame - 1) / 192 * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = height
            
            bpy.context.scene.frame_set(frame)
            camera.location = (x, y, z)
            camera.keyframe_insert(data_path="location")
            
            # Point camera towards center
            direction = mathutils.Vector((0, 0, 1)) - camera.location
            rot_quat = direction.to_track_quat('-Z', 'Y')
            camera.rotation_euler = rot_quat.to_euler()
            camera.keyframe_insert(data_path="rotation_euler")
        
        # Set interpolation to linear
        if camera.animation_data:
            for fcurve in camera.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'LINEAR'
        
        print("🎬 Showcase camera animation added")

def setup_render_settings():
    """Configure render settings for showcase"""
    scene = bpy.context.scene
    
    # Use Cycles for better quality
    scene.render.engine = 'CYCLES'
    
    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Quality settings
    scene.cycles.samples = 128  # Higher quality for showcase
    
    # Output
    scene.render.image_settings.file_format = 'PNG'
    
    print("🎬 Render settings configured")

def main():
    """Main function to create character showcase"""
    print("👥 Creating LevlStudio Character Showcase...")
    print("=" * 50)
    
    # Clear scene
    clear_scene()
    
    # Discover available characters
    characters = discover_character_models()
    
    if not characters:
        print("❌ No character models found!")
        print("   Make sure you have FBX, GLB, or Blend files in assets/characters/")
        return
    
    # Limit to 8 characters for better showcase
    showcase_characters = characters[:8]
    
    # Arrange characters in a circle
    radius = 6
    num_chars = len(showcase_characters)
    
    imported_count = 0
    for i, char_info in enumerate(showcase_characters):
        # Calculate position
        angle = (2 * math.pi * i) / num_chars
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 0
        
        # Calculate rotation to face center
        rotation_z = angle + math.pi/2
        
        # Import character
        imported_obj = import_character(
            char_info, 
            position=(x, y, z), 
            rotation=(0, 0, rotation_z)
        )
        
        if imported_obj:
            imported_count += 1
    
    # Create environment and setup
    create_showcase_environment()
    setup_showcase_lighting()
    setup_showcase_camera()
    add_showcase_animation()
    setup_render_settings()
    
    print(f"\n✅ Character showcase creation complete!")
    print(f"📋 Showcase contains:")
    print(f"   - {imported_count} characters arranged in circle")
    print(f"   - Dramatic lighting setup")
    print(f"   - Rotating camera animation")
    print(f"   - Professional backdrop")
    print("\n🎬 Ready to render!")
    print("   Press F12 to render a still image")
    print("   Press Ctrl+F12 to render animation")

# Run the script
if __name__ == "__main__":
    main()