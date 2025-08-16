#!/usr/bin/env python3
"""
LevlStudio Blender Scene Builder
Create cinematic scenes using existing character and environment assets
"""

import bpy
import bmesh
import mathutils
import json
import sys
import os
from pathlib import Path
from mathutils import Vector, Euler

class LevlStudioSceneBuilder:
    """Build cinematic scenes in Blender using project assets"""
    
    def __init__(self, project_root=None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Try to find project root from current script location
            current_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
            self.project_root = current_path
        
        self.assets_dir = self.project_root / "assets"
        self.characters_dir = self.assets_dir / "characters"
        self.environments_dir = self.assets_dir / "environments"
        self.scenes_dir = self.project_root / "scenes"
        self.scenes_dir.mkdir(exist_ok=True)
        
        # Scene configuration
        self.scene_data = {
            "characters": [],
            "environment": None,
            "cameras": [],
            "lights": [],
            "animations": []
        }
        
    def clear_scene(self):
        """Clear the default Blender scene"""
        # Delete all mesh objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Clear orphan data
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        
        print("✅ Scene cleared")
    
    def discover_available_assets(self):
        """Scan and catalog available assets"""
        assets = {
            "characters": {},
            "environments": {},
            "props": {}
        }
        
        # Discover characters
        if self.characters_dir.exists():
            for char_dir in self.characters_dir.iterdir():
                if char_dir.is_dir():
                    char_name = char_dir.name
                    char_files = {
                        "fbx": list(char_dir.glob("*.fbx")),
                        "glb": list(char_dir.glob("*.glb")),
                        "blend": list(char_dir.glob("*.blend")),
                        "textures": list((char_dir / "tex").glob("*")) if (char_dir / "tex").exists() else [],
                        "reference": list((char_dir / "tex").glob("*reference*"))
                    }
                    assets["characters"][char_name] = char_files
        
        # Discover environments
        if self.environments_dir.exists():
            for env_dir in self.environments_dir.iterdir():
                if env_dir.is_dir():
                    env_name = env_dir.name
                    env_files = {
                        "blend": list(env_dir.glob("*.blend")),
                        "glb": list(env_dir.glob("*.glb")),
                        "fbx": list(env_dir.glob("*.fbx")),
                        "textures": list((env_dir / "tex").glob("*")) if (env_dir / "tex").exists() else []
                    }
                    assets["environments"][env_name] = env_files
        
        print(f"🔍 Discovered assets:")
        print(f"   Characters: {len(assets['characters'])}")
        print(f"   Environments: {len(assets['environments'])}")
        
        return assets
    
    def import_character(self, character_name, position=(0, 0, 0), rotation=(0, 0, 0), scale=1.0):
        """Import a character asset into the scene"""
        assets = self.discover_available_assets()
        
        if character_name not in assets["characters"]:
            print(f"❌ Character '{character_name}' not found")
            return None
        
        char_files = assets["characters"][character_name]
        imported_object = None
        
        # Priority: FBX > GLB > Blend
        if char_files["fbx"]:
            fbx_file = char_files["fbx"][0]
            print(f"📥 Importing FBX: {fbx_file.name}")
            bpy.ops.import_scene.fbx(filepath=str(fbx_file))
            imported_object = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
            
        elif char_files["glb"]:
            glb_file = char_files["glb"][0]
            print(f"📥 Importing GLB: {glb_file.name}")
            bpy.ops.import_scene.gltf(filepath=str(glb_file))
            imported_object = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
            
        elif char_files["blend"]:
            blend_file = char_files["blend"][0]
            print(f"📥 Importing Blend: {blend_file.name}")
            # Import objects from blend file
            with bpy.data.libraries.load(str(blend_file)) as (data_from, data_to):
                data_to.objects = data_from.objects
            
            # Link imported objects to scene
            for obj in data_to.objects:
                if obj:
                    bpy.context.collection.objects.link(obj)
                    imported_object = obj
        
        if imported_object:
            # Position the character
            imported_object.location = position
            imported_object.rotation_euler = rotation
            imported_object.scale = (scale, scale, scale)
            imported_object.name = f"{character_name}_imported"
            
            # Apply materials if textures exist
            self.apply_character_materials(imported_object, char_files["textures"])
            
            print(f"✅ Character '{character_name}' imported successfully")
            return imported_object
        
        print(f"❌ Failed to import character '{character_name}'")
        return None
    
    def import_environment(self, environment_name):
        """Import an environment asset"""
        assets = self.discover_available_assets()
        
        if environment_name not in assets["environments"]:
            print(f"❌ Environment '{environment_name}' not found")
            return None
        
        env_files = assets["environments"][environment_name]
        imported_object = None
        
        # Priority: Blend > GLB > FBX
        if env_files["blend"]:
            blend_file = env_files["blend"][0]
            print(f"🏛️ Importing environment Blend: {blend_file.name}")
            
            # Import all objects from environment
            with bpy.data.libraries.load(str(blend_file)) as (data_from, data_to):
                data_to.objects = data_from.objects
                data_to.materials = data_from.materials
                data_to.textures = data_from.textures
            
            # Link all imported objects
            for obj in data_to.objects:
                if obj:
                    bpy.context.collection.objects.link(obj)
                    if not imported_object:
                        imported_object = obj
                        
        elif env_files["glb"]:
            glb_file = env_files["glb"][0]
            print(f"🏛️ Importing environment GLB: {glb_file.name}")
            bpy.ops.import_scene.gltf(filepath=str(glb_file))
            imported_object = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
        
        if imported_object:
            print(f"✅ Environment '{environment_name}' imported successfully")
            return imported_object
        
        print(f"❌ Failed to import environment '{environment_name}'")
        return None
    
    def apply_character_materials(self, character_obj, texture_files):
        """Apply textures to character"""
        if not texture_files or not character_obj:
            return
        
        # Create material for character
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
        
        # Link BSDF to output
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Try to load textures
        for texture_file in texture_files:
            if any(keyword in texture_file.name.lower() for keyword in ['basecolor', 'diffuse', 'color']):
                # Load base color texture
                tex_image = nodes.new(type='ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(str(texture_file))
                tex_image.location = (-300, 0)
                links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
                print(f"📸 Applied base color texture: {texture_file.name}")
                break
        
        # Assign material to object
        if character_obj.data.materials:
            character_obj.data.materials[0] = material
        else:
            character_obj.data.materials.append(material)
    
    def setup_cinematic_lighting(self, lighting_style="dramatic"):
        """Set up cinematic lighting for the scene"""
        
        # Remove default light
        if "Light" in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
        
        if lighting_style == "dramatic":
            # Key light (main directional light)
            bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
            key_light = bpy.context.active_object
            key_light.name = "Key_Light"
            key_light.data.energy = 3.0
            key_light.data.color = (1.0, 0.95, 0.8)  # Warm white
            key_light.rotation_euler = (0.8, 0.2, 0.5)
            
            # Fill light (softer, cooler)
            bpy.ops.object.light_add(type='AREA', location=(-3, 2, 4))
            fill_light = bpy.context.active_object
            fill_light.name = "Fill_Light"
            fill_light.data.energy = 50.0
            fill_light.data.color = (0.7, 0.8, 1.0)  # Cool blue
            fill_light.data.size = 3.0
            
            # Rim light (backlight for character separation)
            bpy.ops.object.light_add(type='SPOT', location=(0, 5, 6))
            rim_light = bpy.context.active_object
            rim_light.name = "Rim_Light"
            rim_light.data.energy = 100.0
            rim_light.data.color = (1.0, 0.9, 0.7)
            rim_light.data.spot_size = 1.2
            rim_light.rotation_euler = (1.1, 0, 3.14)
            
        elif lighting_style == "christmas":
            # Warm key light
            bpy.ops.object.light_add(type='SUN', location=(4, -4, 6))
            key_light = bpy.context.active_object
            key_light.name = "Christmas_Key"
            key_light.data.energy = 2.5
            key_light.data.color = (1.0, 0.8, 0.6)  # Warm orange
            
            # Cool moonlight
            bpy.ops.object.light_add(type='SUN', location=(-6, 6, 8))
            moon_light = bpy.context.active_object
            moon_light.name = "Moonlight"
            moon_light.data.energy = 1.0
            moon_light.data.color = (0.6, 0.7, 1.0)  # Cool blue
            
            # Magical accent lights
            colors = [(1.0, 0.2, 0.2), (0.2, 1.0, 0.2), (0.2, 0.2, 1.0)]  # Red, Green, Blue
            for i, color in enumerate(colors):
                bpy.ops.object.light_add(type='POINT', location=((-2 + i*2), -2, 1))
                accent_light = bpy.context.active_object
                accent_light.name = f"Magic_Light_{i+1}"
                accent_light.data.energy = 25.0
                accent_light.data.color = color
        
        print(f"💡 {lighting_style.title()} lighting setup complete")
    
    def create_camera_setup(self, camera_style="cinematic"):
        """Create camera(s) for the scene"""
        
        # Remove default camera
        if "Camera" in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
        
        if camera_style == "cinematic":
            # Main camera - establishing shot
            bpy.ops.object.camera_add(location=(8, -8, 4))
            main_camera = bpy.context.active_object
            main_camera.name = "Main_Camera"
            main_camera.rotation_euler = (1.1, 0, 0.785)  # Look down and towards center
            
            # Set camera properties
            main_camera.data.lens = 35  # Wide angle for establishing shot
            main_camera.data.sensor_width = 36
            
            # Close-up camera
            bpy.ops.object.camera_add(location=(3, -3, 1.6))
            closeup_camera = bpy.context.active_object
            closeup_camera.name = "Closeup_Camera"
            closeup_camera.rotation_euler = (1.5, 0, 0.6)
            closeup_camera.data.lens = 85  # Portrait lens
            
            # Set main camera as active
            bpy.context.scene.camera = main_camera
            
        elif camera_style == "character_focus":
            # Character-focused camera
            bpy.ops.object.camera_add(location=(4, -4, 2))
            char_camera = bpy.context.active_object
            char_camera.name = "Character_Camera"
            char_camera.rotation_euler = (1.3, 0, 0.785)
            char_camera.data.lens = 50  # Standard lens
            
            bpy.context.scene.camera = char_camera
        
        print(f"📷 {camera_style.title()} camera setup complete")
    
    def create_christmas_scene(self):
        """Create a Christmas-themed scene with multiple characters"""
        print("🎄 Creating Christmas Scene...")
        
        # Clear scene
        self.clear_scene()
        
        # Import environment
        self.import_environment("env_santa_village_night")
        
        # Import multiple characters
        characters_to_add = [
            ("char_nimble", (-2, 0, 0), (0, 0, 0.3)),
            ("char_marzipan_maw", (0, 2, 0), (0, 0, 0)),
            ("char_crinkle", (2, -1, 0), (0, 0, -0.5))
        ]
        
        for char_name, position, rotation in characters_to_add:
            self.import_character(char_name, position, rotation)
        
        # Set up lighting
        self.setup_cinematic_lighting("christmas")
        
        # Set up cameras
        self.create_camera_setup("cinematic")
        
        # Configure render settings
        self.setup_render_settings()
        
        print("✅ Christmas scene created successfully!")
    
    def create_character_showcase(self):
        """Create a scene showcasing all available characters"""
        print("👥 Creating Character Showcase...")
        
        # Clear scene
        self.clear_scene()
        
        # Get available characters
        assets = self.discover_available_assets()
        characters = list(assets["characters"].keys())
        
        # Arrange characters in a circle
        import math
        num_chars = min(len(characters), 8)  # Limit to 8 characters
        radius = 4
        
        for i, char_name in enumerate(characters[:num_chars]):
            angle = (2 * math.pi * i) / num_chars
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            rotation_z = angle + math.pi/2  # Face towards center
            
            self.import_character(char_name, (x, y, 0), (0, 0, rotation_z))
        
        # Set up dramatic lighting
        self.setup_cinematic_lighting("dramatic")
        
        # Set up camera
        self.create_camera_setup("character_focus")
        
        # Add ground plane
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.1))
        ground = bpy.context.active_object
        ground.name = "Ground"
        
        # Configure render settings
        self.setup_render_settings()
        
        print(f"✅ Character showcase created with {num_chars} characters!")
    
    def setup_render_settings(self):
        """Configure render settings for high quality output"""
        scene = bpy.context.scene
        
        # Set render engine to Cycles for better quality
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'GPU' if bpy.context.preferences.addons['cycles'].preferences.has_active_device() else 'CPU'
        
        # Resolution settings
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 100
        
        # Quality settings
        scene.cycles.samples = 128  # Good balance of quality/speed
        scene.render.film_transparent = False
        
        # Output settings
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(self.scenes_dir / "render_")
        
        print("🎬 Render settings configured")
    
    def animate_scene(self, animation_type="turntable"):
        """Add animation to the scene"""
        if animation_type == "turntable":
            # Animate camera rotating around the scene
            camera = bpy.context.scene.camera
            if camera:
                # Set keyframes for rotation
                bpy.context.scene.frame_start = 1
                bpy.context.scene.frame_end = 120  # 5 seconds at 24fps
                
                # Starting position
                bpy.context.scene.frame_set(1)
                camera.rotation_euler[2] = 0
                camera.keyframe_insert(data_path="rotation_euler", index=2)
                
                # Ending position (full rotation)
                bpy.context.scene.frame_set(120)
                camera.rotation_euler[2] = 6.28318  # 2*pi radians = 360 degrees
                camera.keyframe_insert(data_path="rotation_euler", index=2)
                
                # Set interpolation to linear
                if camera.animation_data:
                    for fcurve in camera.animation_data.action.fcurves:
                        for keyframe in fcurve.keyframe_points:
                            keyframe.interpolation = 'LINEAR'
                
                print("🎬 Turntable animation added")
    
    def save_scene(self, scene_name):
        """Save the current scene"""
        scene_file = self.scenes_dir / f"{scene_name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
        print(f"💾 Scene saved as: {scene_file}")
        return scene_file
    
    def render_scene(self, output_name="render"):
        """Render the current scene"""
        output_path = self.scenes_dir / f"{output_name}.png"
        bpy.context.scene.render.filepath = str(output_path)
        bpy.ops.render.render(write_still=True)
        print(f"🖼️ Scene rendered to: {output_path}")
        return output_path


# Command line interface for running outside Blender
def create_blender_script(scene_type="christmas", project_root=None):
    """Create a Blender script file that can be executed"""
    
    script_content = f'''
# LevlStudio Scene Builder Script
import sys
from pathlib import Path

# Add project root to path
project_root = Path("{project_root or Path.cwd()}")
sys.path.append(str(project_root))

try:
    from blender_scene_builder import LevlStudioSceneBuilder
    
    # Create scene builder
    builder = LevlStudioSceneBuilder(str(project_root))
    
    # Build the scene
    if "{scene_type}" == "christmas":
        builder.create_christmas_scene()
        builder.animate_scene("turntable")
        builder.save_scene("christmas_scene")
        builder.render_scene("christmas_render")
        
    elif "{scene_type}" == "showcase":
        builder.create_character_showcase()
        builder.animate_scene("turntable")
        builder.save_scene("character_showcase")
        builder.render_scene("showcase_render")
        
    print("✅ Scene building complete!")
    
except Exception as e:
    print(f"❌ Error: {{e}}")
    import traceback
    traceback.print_exc()
'''
    
    script_path = Path(project_root or Path.cwd()) / f"blender_scene_{scene_type}.py"
    script_path.write_text(script_content)
    
    return script_path


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LevlStudio Blender Scene Builder")
    parser.add_argument("--scene-type", choices=["christmas", "showcase"], default="christmas",
                       help="Type of scene to create")
    parser.add_argument("--project-root", help="Path to LevlStudio project root")
    
    args = parser.parse_args()
    
    # If running in Blender
    if 'bpy' in globals():
        builder = LevlStudioSceneBuilder(args.project_root)
        
        if args.scene_type == "christmas":
            builder.create_christmas_scene()
        elif args.scene_type == "showcase":
            builder.create_character_showcase()
        
    else:
        # Create script for Blender to execute
        script_path = create_blender_script(args.scene_type, args.project_root)
        print(f"📝 Blender script created: {script_path}")
        print(f"🚀 Run with: blender --background --python {script_path}")


if __name__ == "__main__":
    main()