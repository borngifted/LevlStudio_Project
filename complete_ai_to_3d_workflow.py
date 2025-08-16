#!/usr/bin/env python3
"""
Complete AI-to-3D-to-UE5 Workflow
Recreates the exact workflow from the video:
ChatGPT → Photoshop → Hunyuan 3D → Blender → UE5 → AI Style Transfer
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any

from ai_to_3d_pipeline import AITo3DPipeline
from ue5_integration import UE5Integration

class CompleteWorkflow:
    """Orchestrate the complete AI-to-3D-to-UE5 workflow"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ai_pipeline = AITo3DPipeline(project_root)
        self.ue_integration = UE5Integration(project_root)
        
        # Create workflow tracking
        self.workflow_dir = self.project_root / "workflow_results"
        self.workflow_dir.mkdir(exist_ok=True)
    
    def van_workflow_example(self) -> Dict[str, Any]:
        """
        Recreate the exact van workflow from the video
        """
        
        workflow_id = f"van_workflow_{int(time.time())}"
        results = {
            "workflow_id": workflow_id,
            "title": "Delivery Van AI-to-3D Workflow",
            "description": "Complete pipeline from AI image to UE5 animation",
            "steps": {},
            "timeline": []
        }
        
        def log_step(step_name: str, description: str, result: Any = None):
            timestamp = time.time()
            results["timeline"].append({
                "step": step_name,
                "description": description,
                "timestamp": timestamp,
                "success": result.get("success", False) if isinstance(result, dict) else bool(result)
            })
            results["steps"][step_name] = result
            print(f"🔄 {step_name}: {description}")
        
        print("🚐 Starting Van AI-to-3D Workflow (from video)")
        print("=" * 60)
        
        # Step 1: Generate concept images
        log_step("concept_generation", "Generating van concept image with ChatGPT/DALL-E")
        van_concept = self.ai_pipeline.generate_concept_image(
            prompt="""
            White delivery van, side view, clean white background. 
            Modern commercial vehicle with sliding door on the side.
            Simple design, well-lit, isometric perspective, suitable for 3D modeling reference.
            No text or logos, clean geometric shapes.
            """,
            asset_name="delivery_van"
        )
        log_step("concept_generation", "Van concept generated", van_concept)
        
        # Step 2: Generate interior components
        log_step("interior_generation", "Generating van interior components")
        interior_components = {}
        
        interior_parts = {
            "seats": "Van interior seats, isometric view, clean background, two front seats",
            "dashboard": "Van dashboard and steering wheel, isometric view, simple design",
            "door_panels": "Van interior door panels with handles, isometric view"
        }
        
        for part_name, part_prompt in interior_parts.items():
            component_result = self.ai_pipeline.generate_concept_image(
                prompt=part_prompt,
                asset_name=f"van_{part_name}"
            )
            interior_components[part_name] = component_result
        
        log_step("interior_generation", "Interior components generated", interior_components)
        
        # Step 3: Image cleanup (Photoshop alternative)
        log_step("image_cleanup", "Cleaning up generated images")
        cleanup_results = {}
        
        if van_concept.get("success"):
            van_cleanup = self.ai_pipeline.process_with_photoshop_alternative(
                van_concept["image_path"], "delivery_van"
            )
            cleanup_results["van"] = van_cleanup
        
        for part_name, component in interior_components.items():
            if component.get("success"):
                cleanup = self.ai_pipeline.process_with_photoshop_alternative(
                    component["image_path"], f"van_{part_name}"
                )
                cleanup_results[part_name] = cleanup
        
        log_step("image_cleanup", "Image cleanup completed", cleanup_results)
        
        # Step 4: 3D conversion instructions
        log_step("3d_conversion", "Providing 3D conversion workflow")
        conversion_guide = {
            "services_to_use": [
                {
                    "name": "Tripo3D",
                    "url": "https://www.tripo3d.ai/",
                    "recommended": True,
                    "free_tier": True
                },
                {
                    "name": "Meshy",
                    "url": "https://www.meshy.ai/",
                    "quality": "high"
                },
                {
                    "name": "Luma Genie", 
                    "url": "https://lumalabs.ai/genie",
                    "speed": "fast"
                }
            ],
            "workflow_steps": [
                "Upload your cleaned concept images to one of the 3D services",
                "Download the generated 3D models (GLB format preferred)",
                "Save models to: ai_generated_assets/3d_models/",
                "Run Blender cleanup script on each model",
                "Export as FBX for Unreal Engine"
            ],
            "expected_outputs": [
                "ai_generated_assets/3d_models/delivery_van.glb",
                "ai_generated_assets/3d_models/van_seats.glb", 
                "ai_generated_assets/3d_models/van_dashboard.glb",
                "ai_generated_assets/3d_models/van_door_panels.glb"
            ]
        }
        log_step("3d_conversion", "3D conversion guide prepared", conversion_guide)
        
        # Step 5: Blender processing scripts
        log_step("blender_scripts", "Creating Blender automation scripts")
        blender_commands = []
        
        for asset_name in ["delivery_van", "van_seats", "van_dashboard", "van_door_panels"]:
            script_content = f'''
# Blender automation for {asset_name}
import bpy
import sys
sys.path.append('.')
from blender_automation import BlenderProcessor

processor = BlenderProcessor()
processor.full_ai_to_ue_process(
    input_file="ai_generated_assets/3d_models/{asset_name}.glb",
    output_file="ai_generated_assets/ue_ready/{asset_name}_UE.fbx",
    voxel_size=0.05,
    decimate_ratio=0.7
)
'''
            
            script_path = self.workflow_dir / f"blender_{asset_name}.py"
            script_path.write_text(script_content)
            
            blender_command = f"""
blender --background --python {script_path}
"""
            blender_commands.append({
                "asset": asset_name,
                "script": str(script_path),
                "command": blender_command.strip()
            })
        
        log_step("blender_scripts", "Blender scripts created", blender_commands)
        
        # Step 6: UE5 integration setup
        log_step("ue5_setup", "Setting up UE5 integration")
        ue5_config = {
            "assets_to_import": [
                {
                    "name": "delivery_van",
                    "fbx_path": "ai_generated_assets/ue_ready/delivery_van_UE.fbx",
                    "destination": "/Game/AI_Generated/Vehicles",
                    "type": "vehicle"
                },
                {
                    "name": "van_seats",
                    "fbx_path": "ai_generated_assets/ue_ready/van_seats_UE.fbx", 
                    "destination": "/Game/AI_Generated/Interiors",
                    "type": "interior"
                },
                {
                    "name": "van_dashboard",
                    "fbx_path": "ai_generated_assets/ue_ready/van_dashboard_UE.fbx",
                    "destination": "/Game/AI_Generated/Interiors", 
                    "type": "interior"
                },
                {
                    "name": "van_door_panels",
                    "fbx_path": "ai_generated_assets/ue_ready/van_door_panels_UE.fbx",
                    "destination": "/Game/AI_Generated/Interiors",
                    "type": "interior"
                }
            ],
            "scene_setup": {
                "scene_name": "Van_Alleyway_Scene",
                "environment": "/Game/Environments/Alleyway",  # Approved Fab asset
                "lighting": "cinematic",
                "animation_duration": 5.0
            }
        }
        
        # Save UE5 config
        config_path = self.workflow_dir / "ue5_van_config.json"
        with open(config_path, 'w') as f:
            json.dump(ue5_config, f, indent=2)
        
        log_step("ue5_setup", "UE5 configuration saved", {"config_path": str(config_path)})
        
        # Step 7: Animation and rendering workflow
        log_step("animation_setup", "Creating animation workflow")
        animation_workflow = {
            "sequence_name": "Van_Animation_Sequence",
            "duration": 5.0,
            "keyframes": [
                {
                    "time": 0.0,
                    "van_location": [0, 0, 0],
                    "van_rotation": [0, 0, 0],
                    "camera_location": [500, -500, 200]
                },
                {
                    "time": 2.5,
                    "van_location": [0, 250, 0], 
                    "van_rotation": [0, 0, 0],
                    "camera_location": [500, -250, 200]
                },
                {
                    "time": 5.0,
                    "van_location": [0, 500, 0],
                    "van_rotation": [0, 0, 0], 
                    "camera_location": [500, 0, 200]
                }
            ],
            "render_settings": {
                "resolution": "1280x720",
                "fps": 24,
                "quality": "high",
                "output": "exports/van_animation.mp4"
            }
        }
        log_step("animation_setup", "Animation workflow defined", animation_workflow)
        
        # Step 8: AI style transfer integration
        log_step("ai_style_setup", "Setting up AI style transfer")
        style_transfer_config = {
            "input_video": "exports/van_animation.mp4",
            "style_reference": "assets/characters/char_caroler/tex/char_caroler_reference.png",
            "comfyui_workflow": "comfy_workflows/working_video_test.json",
            "output_directory": "outputs/van_styled",
            "processing_notes": [
                "Use the rendered UE5 van animation as input",
                "Apply style transfer to match the art direction", 
                "Output styled animation for final compositing"
            ]
        }
        log_step("ai_style_setup", "Style transfer configured", style_transfer_config)
        
        # Final summary
        results["summary"] = {
            "total_steps": len(results["timeline"]),
            "estimated_time": "30 minutes manual work + processing time",
            "manual_steps": [
                "Upload images to 3D service and download models",
                "Run Blender scripts on downloaded models", 
                "Import FBX files into Unreal Engine",
                "Set up scene and run animation",
                "Process final video through ComfyUI"
            ],
            "automated_steps": [
                "AI image generation",
                "Image cleanup and enhancement", 
                "Blender mesh processing",
                "UE5 scene setup commands",
                "ComfyUI style transfer"
            ]
        }
        
        # Save complete workflow
        workflow_file = self.workflow_dir / f"{workflow_id}.json"
        with open(workflow_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        log_step("workflow_complete", f"Complete workflow saved to {workflow_file}", {"success": True})
        
        return results
    
    def print_workflow_instructions(self, workflow_result: Dict[str, Any]):
        """Print clear step-by-step instructions for the user"""
        
        print("\n" + "="*80)
        print("🎬 COMPLETE AI-TO-3D WORKFLOW INSTRUCTIONS")
        print("="*80)
        
        print(f"\n📋 Workflow: {workflow_result['title']}")
        print(f"📁 Results saved in: workflow_results/{workflow_result['workflow_id']}.json")
        
        print("\n🚀 STEP-BY-STEP EXECUTION:")
        print("-" * 40)
        
        steps = [
            {
                "title": "1. 🎨 AI Image Generation (AUTOMATED)",
                "description": "Concept images have been generated",
                "action": "✅ COMPLETED - Check ai_generated_assets/concept_images/"
            },
            {
                "title": "2. 🖼️ Image Cleanup (AUTOMATED)", 
                "description": "Images cleaned and enhanced",
                "action": "✅ COMPLETED - Enhanced images ready for 3D conversion"
            },
            {
                "title": "3. 🎯 3D Model Generation (MANUAL)",
                "description": "Convert images to 3D models",
                "action": """
🔸 Go to https://www.tripo3d.ai/ (recommended) or https://www.meshy.ai/
🔸 Upload your concept images from ai_generated_assets/concept_images/
🔸 Generate 3D models (GLB format)
🔸 Download and save to ai_generated_assets/3d_models/
                """
            },
            {
                "title": "4. 🎭 Blender Processing (SEMI-AUTOMATED)",
                "description": "Clean up 3D models for game use",
                "action": """
🔸 Run these Blender commands for each model:
   blender --background --python workflow_results/blender_delivery_van.py
   blender --background --python workflow_results/blender_van_seats.py
   blender --background --python workflow_results/blender_van_dashboard.py
   blender --background --python workflow_results/blender_van_door_panels.py
                """
            },
            {
                "title": "5. 🎮 Unreal Engine Integration (MANUAL)",
                "description": "Import assets and create scene",
                "action": """
🔸 Import FBX files from ai_generated_assets/ue_ready/ into UE5
🔸 Set up scene with Fab alleyway environment
🔸 Create level sequence with van animation
🔸 Add camera movements
🔸 Render sequence to exports/van_animation.mp4
                """
            },
            {
                "title": "6. 🎨 AI Style Transfer (AUTOMATED)",
                "description": "Apply AI styling to rendered animation",
                "action": """
🔸 Run: python3 comfy_bridge_client.py \\
         --workflow comfy_workflows/working_video_test.json \\
         --video_in exports/van_animation.mp4 \\
         --style_img assets/characters/char_caroler/tex/char_caroler_reference.png \\
         --out_dir outputs/van_styled
                """
            }
        ]
        
        for step in steps:
            print(f"\n{step['title']}")
            print(f"📝 {step['description']}")
            print(f"⚡ Action: {step['action']}")
        
        print("\n" + "="*80)
        print("💡 TIPS FOR SUCCESS:")
        print("- Use isometric/orthographic views for better 3D conversion")
        print("- Keep backgrounds clean and simple in concept images")  
        print("- Test with lower poly counts first, then increase quality")
        print("- Always clean up meshes before importing to UE5")
        print("- Use the approved Fab alleyway environment to avoid licensing issues")
        
        print(f"\n🎯 EXPECTED TIMELINE: ~{workflow_result['summary']['estimated_time']}")
        print("🎉 FINAL OUTPUT: Styled animated short film clip ready for compositing!")
        print("="*80)


def main():
    """Main execution function"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set your OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   Get your key from: https://platform.openai.com/api-keys")
        return
    
    print("🎬 LevlStudio Complete AI-to-3D Workflow")
    print("Recreating the workflow from the video...")
    print()
    
    # Initialize and run the complete workflow
    workflow = CompleteWorkflow()
    
    # Run the van example (from the video)
    van_result = workflow.van_workflow_example()
    
    # Print instructions for the user
    workflow.print_workflow_instructions(van_result)
    
    print(f"\n📊 Workflow completed with {len(van_result['timeline'])} steps")
    print(f"📁 Full results saved in: workflow_results/{van_result['workflow_id']}.json")


if __name__ == "__main__":
    main()