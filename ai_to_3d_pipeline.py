#!/usr/bin/env python3
"""
AI-to-3D Pipeline for LevlStudio
Recreates the workflow from the video: ChatGPT → Hunyuan 3D → Blender → UE5
"""

import os
import json
import subprocess
import urllib.request
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any

class AITo3DPipeline:
    """Complete AI-to-3D asset generation pipeline"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.assets_dir = self.project_root / "ai_generated_assets"
        self.assets_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.assets_dir / "concept_images").mkdir(exist_ok=True)
        (self.assets_dir / "3d_models").mkdir(exist_ok=True)
        (self.assets_dir / "cleaned_models").mkdir(exist_ok=True)
        (self.assets_dir / "ue_ready").mkdir(exist_ok=True)
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    def generate_concept_image(self, prompt: str, asset_name: str) -> Dict[str, Any]:
        """
        Step 1: Generate concept image using OpenAI DALL-E
        Replaces: ChatGPT image generation
        """
        if not self.openai_api_key:
            return {"error": "OPENAI_API_KEY not set in environment"}
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            # Enhanced prompt for better 3D conversion
            enhanced_prompt = f"""
            {prompt}
            
            Style: Clean, isometric view, single object on white background,
            well-lit, high contrast, minimal shadows, suitable for 3D modeling reference.
            Make sure the object is complete and fully visible from this angle.
            """
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )
            
            # Download and save image
            image_url = response.data[0].url
            image_path = self.assets_dir / "concept_images" / f"{asset_name}.png"
            
            urllib.request.urlretrieve(image_url, image_path)
            
            return {
                "success": True,
                "image_path": str(image_path),
                "prompt_used": enhanced_prompt,
                "url": image_url
            }
            
        except ImportError:
            return {"error": "OpenAI library not installed. Run: pip install openai"}
        except Exception as e:
            return {"error": f"Image generation failed: {str(e)}"}
    
    def process_with_photoshop_alternative(self, image_path: str, asset_name: str) -> Dict[str, Any]:
        """
        Step 2: Clean up image (Photoshop alternative using Python)
        Replaces: Photoshop generative fill
        """
        try:
            import cv2
            import numpy as np
            from PIL import Image, ImageFilter
            
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return {"error": f"Could not load image: {image_path}"}
            
            # Basic cleanup operations
            # 1. Remove noise
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            
            # 2. Enhance contrast
            lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # 3. Save cleaned image
            cleaned_path = self.assets_dir / "concept_images" / f"{asset_name}_cleaned.png"
            cv2.imwrite(str(cleaned_path), enhanced)
            
            return {
                "success": True,
                "cleaned_image_path": str(cleaned_path),
                "original_path": image_path
            }
            
        except ImportError:
            return {"error": "OpenCV not installed. Run: pip install opencv-python pillow"}
        except Exception as e:
            return {"error": f"Image processing failed: {str(e)}"}
    
    def convert_to_3d_hunyuan(self, image_path: str, asset_name: str) -> Dict[str, Any]:
        """
        Step 3: Convert image to 3D using Hunyuan 3D
        Replaces: Hunyuan 3D with Pinocchio installer
        """
        # Note: This would require Hunyuan 3D to be installed locally
        # For now, we'll create a placeholder that shows the integration point
        
        output_path = self.assets_dir / "3d_models" / f"{asset_name}.glb"
        
        # Check if Hunyuan 3D is available
        hunyuan_command = self._find_hunyuan_command()
        
        if not hunyuan_command:
            return {
                "error": "Hunyuan 3D not found. Please install using Pinocchio or manual setup",
                "install_instructions": [
                    "1. Download Pinocchio installer from GitHub",
                    "2. Install Hunyuan 3D through Pinocchio",
                    "3. Or use online service: https://www.tripo3d.ai/",
                    "4. Or use alternative: https://huggingface.co/spaces/dylanebert/3dgs"
                ]
            }
        
        try:
            # Run Hunyuan 3D command
            cmd = [
                hunyuan_command,
                "--input", image_path,
                "--output", str(output_path),
                "--quality", "high"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "model_path": str(output_path),
                    "format": "GLB"
                }
            else:
                return {"error": f"Hunyuan 3D failed: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            return {"error": "Hunyuan 3D conversion timed out (5 minutes)"}
        except Exception as e:
            return {"error": f"3D conversion failed: {str(e)}"}
    
    def alternative_3d_services(self, image_path: str, asset_name: str) -> Dict[str, Any]:
        """
        Alternative 3D generation services
        """
        alternatives = {
            "tripo3d": "https://www.tripo3d.ai/",
            "luma_genie": "https://lumalabs.ai/genie",
            "meshy": "https://www.meshy.ai/",
            "csm": "https://cube.eleutherai.org/",
            "huggingface_3dgs": "https://huggingface.co/spaces/dylanebert/3dgs"
        }
        
        return {
            "message": "Use one of these online services to convert your image to 3D:",
            "services": alternatives,
            "instructions": [
                f"1. Upload your image: {image_path}",
                "2. Download the 3D model (preferably GLB format)",
                f"3. Save to: {self.assets_dir / '3d_models' / f'{asset_name}.glb'}",
                "4. Run cleanup_3d_model() on the downloaded file"
            ]
        }
    
    def cleanup_3d_model(self, model_path: str, asset_name: str) -> Dict[str, Any]:
        """
        Step 4: Clean up 3D model in Blender
        Replaces: Blender mesh cleanup
        """
        output_path = self.assets_dir / "cleaned_models" / f"{asset_name}_cleaned.blend"
        
        # Create Blender cleanup script
        cleanup_script = f'''
import bpy
import bmesh

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import the model
bpy.ops.import_scene.gltf(filepath="{model_path}")

# Select the imported object
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

# Enter edit mode and clean up
bpy.ops.object.mode_set(mode='EDIT')

# Select all vertices
bpy.ops.mesh.select_all(action='SELECT')

# Remove doubles
bpy.ops.mesh.remove_doubles(threshold=0.001)

# Recalculate normals
bpy.ops.mesh.normals_make_consistent(inside=False)

# Smooth shading
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()

# Save the cleaned model
bpy.ops.wm.save_as_mainfile(filepath="{output_path}")

print("Model cleaned and saved successfully")
'''
        
        script_path = self.assets_dir / f"cleanup_{asset_name}.py"
        script_path.write_text(cleanup_script)
        
        # Check if Blender is available
        blender_path = self._find_blender_path()
        
        if not blender_path:
            return {
                "error": "Blender not found",
                "script_created": str(script_path),
                "manual_instructions": [
                    "1. Open Blender",
                    f"2. Run the script: {script_path}",
                    "3. Or manually clean up the mesh:",
                    "   - Import GLB file",
                    "   - Remove doubles",
                    "   - Recalculate normals",
                    "   - Apply smooth shading"
                ]
            }
        
        try:
            # Run Blender with cleanup script
            cmd = [blender_path, "--background", "--python", str(script_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "cleaned_model": str(output_path),
                    "script_used": str(script_path)
                }
            else:
                return {"error": f"Blender cleanup failed: {result.stderr}"}
                
        except Exception as e:
            return {"error": f"Blender processing failed: {str(e)}"}
    
    def prepare_for_unreal(self, model_path: str, asset_name: str) -> Dict[str, Any]:
        """
        Step 5: Prepare model for Unreal Engine
        """
        ue_path = self.assets_dir / "ue_ready" / f"{asset_name}_UE.fbx"
        
        # Create Blender export script
        export_script = f'''
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import cleaned model
bpy.ops.wm.open_mainfile(filepath="{model_path}")

# Export as FBX for Unreal Engine
bpy.ops.export_scene.fbx(
    filepath="{ue_path}",
    use_selection=False,
    use_active_collection=False,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    bake_space_transform=False,
    object_types={{'MESH', 'ARMATURE'}},
    use_mesh_modifiers=True,
    use_custom_props=False,
    add_leaf_bones=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    use_armature_deform_only=True,
    armature_nodetype='NULL',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=1.0,
    path_mode='AUTO',
    embed_textures=False,
    batch_mode='OFF',
    use_batch_own_dir=True,
    use_metadata=True
)

print("Model exported for Unreal Engine")
'''
        
        script_path = self.assets_dir / f"export_{asset_name}.py"
        script_path.write_text(export_script)
        
        return {
            "export_script": str(script_path),
            "output_path": str(ue_path),
            "instructions": [
                "1. Run the export script in Blender",
                "2. Import the FBX file into Unreal Engine",
                "3. Set up materials and collision",
                "4. Create animation blueprints if needed"
            ]
        }
    
    def full_pipeline(self, prompt: str, asset_name: str) -> Dict[str, Any]:
        """
        Run the complete pipeline: Image → 3D → Cleanup → UE Ready
        """
        results = {
            "asset_name": asset_name,
            "prompt": prompt,
            "steps": {}
        }
        
        print(f"🎨 Starting AI-to-3D pipeline for: {asset_name}")
        
        # Step 1: Generate concept image
        print("1. Generating concept image...")
        img_result = self.generate_concept_image(prompt, asset_name)
        results["steps"]["1_concept_image"] = img_result
        
        if not img_result.get("success"):
            return results
        
        # Step 2: Clean up image
        print("2. Cleaning up image...")
        cleanup_result = self.process_with_photoshop_alternative(
            img_result["image_path"], asset_name
        )
        results["steps"]["2_image_cleanup"] = cleanup_result
        
        # Step 3: Alternative 3D services (since Hunyuan needs manual setup)
        print("3. Providing 3D conversion options...")
        conversion_result = self.alternative_3d_services(
            cleanup_result.get("cleaned_image_path", img_result["image_path"]), 
            asset_name
        )
        results["steps"]["3_3d_conversion"] = conversion_result
        
        # Step 4: Provide cleanup instructions
        print("4. Preparing cleanup workflow...")
        # This step waits for manual 3D model placement
        model_path = self.assets_dir / "3d_models" / f"{asset_name}.glb"
        if model_path.exists():
            cleanup_result = self.cleanup_3d_model(str(model_path), asset_name)
            results["steps"]["4_cleanup"] = cleanup_result
        else:
            results["steps"]["4_cleanup"] = {
                "waiting": f"Place your 3D model at: {model_path}",
                "then_run": f"pipeline.cleanup_3d_model('{model_path}', '{asset_name}')"
            }
        
        return results
    
    def _find_hunyuan_command(self) -> Optional[str]:
        """Find Hunyuan 3D executable"""
        possible_paths = [
            "hunyuan3d",
            "/usr/local/bin/hunyuan3d",
            str(Path.home() / "hunyuan3d" / "hunyuan3d"),
            "python -m hunyuan3d"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--help"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def _find_blender_path(self) -> Optional[str]:
        """Find Blender executable"""
        possible_paths = [
            "blender",
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/usr/local/bin/blender",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists() or self._command_exists(path):
                return path
        
        return None
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        try:
            subprocess.run([command, "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False


# CLI Interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-to-3D Pipeline for LevlStudio")
    parser.add_argument("--prompt", required=True, help="Description of the 3D asset to generate")
    parser.add_argument("--name", required=True, help="Asset name (e.g., 'van', 'van_interior')")
    parser.add_argument("--step", help="Run specific step: concept|cleanup|export")
    parser.add_argument("--model-path", help="Path to 3D model file for cleanup/export steps")
    
    args = parser.parse_args()
    
    pipeline = AITo3DPipeline()
    
    if args.step == "concept":
        result = pipeline.generate_concept_image(args.prompt, args.name)
    elif args.step == "cleanup" and args.model_path:
        result = pipeline.cleanup_3d_model(args.model_path, args.name)
    elif args.step == "export" and args.model_path:
        result = pipeline.prepare_for_unreal(args.model_path, args.name)
    else:
        result = pipeline.full_pipeline(args.prompt, args.name)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()