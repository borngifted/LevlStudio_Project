#!/usr/bin/env python3
"""
Simple Scene Creator for Blender
Creates a scene using basic geometry and your character reference images as materials
This works without needing FBX files and showcases your characters
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
                    # Look for reference images
                    ref_images = list(tex_dir.glob("*reference*")) + list(tex_dir.glob("*.png")) + list(tex_dir.glob("*.jpg"))
                    
                    if ref_images:
                        characters.append({
                            "name": char_name,
                            "dir": char_dir,
                            "reference": ref_images[0]  # Use first available image
                        })
                        print(f"🔍 Found character: {char_name} with reference: {ref_images[0].name}")
    
    print(f"📊 Total characters with references: {len(characters)}")
    return characters

def create_character_proxy(char_info, position=(0, 0, 0), scale=1.0):
    """Create a proxy character using a plane with character reference image"""
    char_name = char_info["name"]
    reference_image = char_info["reference"]
    
    # Create a plane for the character
    bpy.ops.mesh.primitive_plane_add(size=2*scale, location=position)
    char_plane = bpy.context.active_object
    char_plane.name = f"{char_name}_proxy"
    
    # Rotate to stand upright
    char_plane.rotation_euler = (1.5708, 0, 0)  # 90 degrees around X axis
    
    # Create material with character reference
    material = bpy.data.materials.new(name=f"{char_name}_Material")
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
    
    # Add image texture
    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 0)
    
    # Load the character reference image
    try:
        tex_image.image = bpy.data.images.load(str(reference_image))
        print(f"📸 Loaded reference image: {reference_image.name}")
    except Exception as e:
        print(f"⚠️ Could not load image {reference_image}: {e}")
        # Use a solid color instead
        principled.inputs['Base Color'].default_value = (0.5, 0.7, 1.0, 1.0)  # Light blue
    
    # Connect nodes
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Make material transparent for better character display
    material.blend_method = 'BLEND'
    principled.inputs['Alpha'].default_value = 0.9
    
    if tex_image.image:
        links.new(tex_image.outputs['Alpha'], principled.inputs['Alpha'])
    
    # Assign material
    char_plane.data.materials.append(material)
    
    print(f"✅ Created proxy for {char_name}")
    return char_plane

def create_scene_environment():
    """Create a simple but attractive environment"""
    
    # Ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    # Ground material - snowy/magical
    ground_mat = bpy.data.materials.new(name="Ground_Material")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (0.9, 0.9, 1.0, 1.0)  # Snow white with blue tint
        principled.inputs['Roughness'].default_value = 0.3
        principled.inputs['Metallic'].default_value = 0.1
    ground.data.materials.append(ground_mat)
    
    # Add some simple background elements
    # Crystal formations (using scaled cubes)
    crystal_positions = [(-8, 6, 1), (8, 5, 1.5), (-6, -7, 0.8), (7, -6, 1.2)]
    
    for i, pos in enumerate(crystal_positions):
        bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
        crystal = bpy.context.active_object
        crystal.name = f"Crystal_{i+1}"
        crystal.scale = (0.5, 0.5, 2 + i*0.3)  # Tall crystal shape
        crystal.rotation_euler = (0, 0, i * 0.5)  # Slight rotation
        
        # Crystal material
        crystal_mat = bpy.data.materials.new(name=f"Crystal_Material_{i+1}")
        crystal_mat.use_nodes = True
        nodes = crystal_mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        if principled:
            # Make crystals translucent and colorful
            colors = [(0.8, 0.9, 1.0, 0.7), (1.0, 0.8, 0.9, 0.7), (0.9, 1.0, 0.8, 0.7), (1.0, 0.9, 0.8, 0.7)]
            color = colors[i % len(colors)]
            principled.inputs['Base Color'].default_value = color
            principled.inputs['Metallic'].default_value = 0.0
            principled.inputs['Roughness'].default_value = 0.1
            principled.inputs['Alpha'].default_value = 0.7
            
        crystal_mat.blend_method = 'BLEND'
        crystal.data.materials.append(crystal_mat)
    
    print("🏔️ Scene environment created")

def setup_magical_lighting():
    """Set up magical/fantasy lighting"""
    
    # Remove default light
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    # Main key light (magical white)
    bpy.ops.object.light_add(type='SUN', location=(8, -6, 12))
    key_light = bpy.context.active_object
    key_light.name = "Magical_Key_Light"
    key_light.data.energy = 4.0
    key_light.data.color = (1.0, 0.95, 0.9)  # Warm white
    key_light.rotation_euler = (0.6, 0.2, 0.6)
    
    # Soft fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, 4, 6))
    fill_light = bpy.context.active_object
    fill_light.name = "Soft_Fill"
    fill_light.data.energy = 100.0
    fill_light.data.color = (0.8, 0.9, 1.0)  # Cool blue
    fill_light.data.size = 6.0
    
    # Magical accent lights (colored points)
    magical_colors = [
        (1.0, 0.4, 0.6),  # Pink
        (0.4, 1.0, 0.6),  # Green
        (0.6, 0.4, 1.0),  # Purple
        (1.0, 0.8, 0.4)   # Gold
    ]
    
    magical_positions = [(6, 6, 3), (-6, 6, 2.5), (6, -6, 3.5), (-6, -6, 2)]
    
    for i, (pos, color) in enumerate(zip(magical_positions, magical_colors)):
        bpy.ops.object.light_add(type='POINT', location=pos)
        magical_light = bpy.context.active_object
        magical_light.name = f"Magical_Light_{i+1}"
        magical_light.data.energy = 30.0
        magical_light.data.color = color
    
    print("✨ Magical lighting setup complete")

def setup_camera():
    """Set up camera for the scene"""
    
    # Remove default camera
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    
    # Main camera - elevated cinematic view
    bpy.ops.object.camera_add(location=(10, -10, 6))
    camera = bpy.context.active_object
    camera.name = "Main_Camera"
    camera.rotation_euler = (1.0, 0, 0.785)
    
    # Camera settings
    camera.data.lens = 35  # Wide angle for dramatic effect
    camera.data.sensor_width = 36
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print("📷 Camera setup complete")

def add_camera_animation():
    """Add smooth camera movement"""
    camera = bpy.context.scene.camera
    if camera:
        # Set frame range
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 200  # ~8 seconds at 24fps
        
        # Store original position
        original_location = camera.location.copy()
        radius = math.sqrt(original_location.x**2 + original_location.y**2)
        height = original_location.z
        
        # Keyframe circular motion
        for frame in range(1, 201, 20):  # Every 20 frames
            angle = (frame - 1) / 200 * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = height + math.sin(angle * 2) * 1  # Slight height variation
            
            bpy.context.scene.frame_set(frame)
            camera.location = (x, y, z)
            camera.keyframe_insert(data_path="location")
            
            # Point camera towards center with slight upward angle
            direction = mathutils.Vector((0, 0, 1)) - camera.location
            rot_quat = direction.to_track_quat('-Z', 'Y')
            camera.rotation_euler = rot_quat.to_euler()
            camera.keyframe_insert(data_path="rotation_euler")
        
        # Set interpolation to linear for smooth motion
        if camera.animation_data:
            for fcurve in camera.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'LINEAR'
        
        print("🎬 Camera animation added")

def setup_render_settings():
    """Configure render settings"""
    scene = bpy.context.scene
    
    # Use Eevee for faster preview (good quality, faster than Cycles)
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # Enable transparency and better effects in Eevee
    scene.eevee.use_bloom = True
    scene.eevee.bloom_intensity = 0.1
    scene.eevee.use_ssr = True  # Screen space reflections
    
    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Output
    scene.render.image_settings.file_format = 'PNG'
    
    print("🎬 Render settings configured (Eevee engine)")

def main():
    """Main function to create the scene"""
    print("✨ Creating LevlStudio Character Reference Scene...")
    print("=" * 60)
    
    # Build the scene
    clear_scene()
    
    # Discover characters
    characters = discover_character_references()
    
    if not characters:
        print("❌ No character references found!")
        print("   Looking for images in assets/characters/*/tex/")
        return
    
    # Create environment first
    create_scene_environment()
    
    # Create character proxies in a nice arrangement
    if len(characters) == 1:
        # Single character in center
        create_character_proxy(characters[0], (0, 0, 1), 1.5)
    elif len(characters) <= 3:
        # Line arrangement
        positions = [(-3, 0, 1), (0, 0, 1), (3, 0, 1)]
        for i, char in enumerate(characters):
            pos = positions[i] if i < len(positions) else (i*2-2, 0, 1)
            create_character_proxy(char, pos, 1.2)
    else:
        # Circular arrangement for more characters
        radius = 4
        num_chars = min(len(characters), 8)  # Limit to 8
        for i, char in enumerate(characters[:num_chars]):
            angle = (2 * math.pi * i) / num_chars
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 1
            create_character_proxy(char, (x, y, z), 1.0)
    
    # Set up lighting and camera
    setup_magical_lighting()
    setup_camera()
    add_camera_animation()
    setup_render_settings()
    
    print(f"\n✅ Scene creation complete!")
    print(f"📋 Scene contains:")
    print(f"   - {len(characters)} character references")
    print(f"   - Magical crystal environment")
    print(f"   - Cinematic lighting with 8 lights")
    print(f"   - Smooth camera animation")
    print("\n🎬 Ready to render!")
    print("   Press F12 to render a still image")
    print("   Press Ctrl+F12 to render animation")
    print("\n💡 Note: Using character reference images as materials")
    print("   This showcases your characters without needing 3D models")

# Run the script
if __name__ == "__main__":
    main()