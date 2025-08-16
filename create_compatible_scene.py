#!/usr/bin/env python3
"""
Compatible Scene Creator for Blender
Creates a scene using basic geometry and character reference images
Works with all Blender versions
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
    
    print(f"📊 Total characters: {len(characters)}")
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
    
    # Create material
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
        print(f"📸 Loaded: {char_name}")
    except Exception as e:
        print(f"⚠️ Could not load image for {char_name}: {e}")
        # Use a solid color instead
        principled.inputs['Base Color'].default_value = (0.5, 0.7, 1.0, 1.0)
    
    # Connect nodes
    if tex_image.image:
        links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material
    char_plane.data.materials.append(material)
    
    print(f"✅ Created proxy for {char_name}")
    return char_plane

def create_simple_environment():
    """Create a simple environment"""
    
    # Ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    # Ground material
    ground_mat = bpy.data.materials.new(name="Ground_Material")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (0.9, 0.9, 1.0, 1.0)  # Light blue
        if 'Roughness' in principled.inputs:
            principled.inputs['Roughness'].default_value = 0.8
    ground.data.materials.append(ground_mat)
    
    # Add some background cubes
    positions = [(-6, 6, 1), (6, 6, 1), (-6, -6, 1), (6, -6, 1)]
    colors = [(1.0, 0.8, 0.8, 1.0), (0.8, 1.0, 0.8, 1.0), (0.8, 0.8, 1.0, 1.0), (1.0, 1.0, 0.8, 1.0)]
    
    for i, (pos, color) in enumerate(zip(positions, colors)):
        bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
        cube = bpy.context.active_object
        cube.name = f"Backdrop_Cube_{i+1}"
        
        # Cube material
        cube_mat = bpy.data.materials.new(name=f"Cube_Material_{i+1}")
        cube_mat.use_nodes = True
        nodes = cube_mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        if principled:
            principled.inputs['Base Color'].default_value = color
        cube.data.materials.append(cube_mat)
    
    print("🏗️ Simple environment created")

def setup_basic_lighting():
    """Set up basic but effective lighting"""
    
    # Remove default light if it exists
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    # Main key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 5.0
    key_light.rotation_euler = (0.6, 0.2, 0.6)
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-3, 3, 5))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 80.0
    fill_light.data.size = 5.0
    
    # Accent light
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 8))
    accent_light = bpy.context.active_object
    accent_light.name = "Accent_Light"
    accent_light.data.energy = 100.0
    
    print("💡 Basic lighting setup complete")

def setup_camera():
    """Set up camera for the scene"""
    
    # Remove default camera if it exists
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    
    # Main camera
    bpy.ops.object.camera_add(location=(8, -8, 5))
    camera = bpy.context.active_object
    camera.name = "Main_Camera"
    camera.rotation_euler = (1.0, 0, 0.785)
    
    # Camera settings
    camera.data.lens = 35
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print("📷 Camera setup complete")

def add_simple_animation():
    """Add simple camera animation"""
    camera = bpy.context.scene.camera
    if camera:
        # Set frame range
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 120  # 5 seconds at 24fps
        
        # Simple rotation animation
        bpy.context.scene.frame_set(1)
        camera.rotation_euler[2] = 0.785
        camera.keyframe_insert(data_path="rotation_euler", index=2)
        
        bpy.context.scene.frame_set(120)
        camera.rotation_euler[2] = 0.785 + 6.28318  # Full rotation
        camera.keyframe_insert(data_path="rotation_euler", index=2)
        
        print("🎬 Animation added")

def setup_render_settings():
    """Configure basic render settings"""
    scene = bpy.context.scene
    
    # Use Cycles for compatibility
    scene.render.engine = 'CYCLES'
    
    # Basic settings
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Set samples if available
    if hasattr(scene, 'cycles'):
        scene.cycles.samples = 64
    
    # Output format
    scene.render.image_settings.file_format = 'PNG'
    
    print("🎬 Render settings configured")

def main():
    """Main function to create the scene"""
    print("✨ Creating Compatible LevlStudio Scene...")
    print("=" * 50)
    
    try:
        # Build the scene
        clear_scene()
        
        # Discover characters
        characters = discover_character_references()
        
        if not characters:
            print("❌ No character references found!")
            return
        
        # Create environment
        create_simple_environment()
        
        # Create character proxies
        if len(characters) <= 3:
            # Line arrangement
            positions = [(-3, 0, 1), (0, 0, 1), (3, 0, 1)]
            for i, char in enumerate(characters):
                pos = positions[i] if i < len(positions) else (i*2-3, 0, 1)
                create_character_proxy(char, pos, 1.2)
        else:
            # Circular arrangement
            radius = 4
            num_chars = min(len(characters), 8)
            for i, char in enumerate(characters[:num_chars]):
                angle = (2 * math.pi * i) / num_chars
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                z = 1
                create_character_proxy(char, (x, y, z), 1.0)
        
        # Set up lighting and camera
        setup_basic_lighting()
        setup_camera()
        add_simple_animation()
        setup_render_settings()
        
        print(f"\n✅ Scene creation complete!")
        print(f"📋 Scene contains:")
        print(f"   - {len(characters)} character references")
        print(f"   - Simple environment with colored cubes")
        print(f"   - Basic 3-point lighting")
        print(f"   - Rotating camera animation")
        print("\n🎬 Ready to render!")
        print("   Press F12 to render a still image")
        print("   Press Ctrl+F12 to render animation")
        
    except Exception as e:
        print(f"❌ Error creating scene: {e}")
        import traceback
        traceback.print_exc()

# Run the script
if __name__ == "__main__":
    main()