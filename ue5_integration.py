#!/usr/bin/env python3
"""
Unreal Engine 5 Integration for AI-to-3D Pipeline
Handles asset import, animation, and AI style transfer integration
"""

import json
import subprocess
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

class UE5Integration:
    """Handle UE5 asset pipeline and integration with ComfyUI"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ue_bridge = self.project_root / "UnrealBridge"
        self.ue_assets = self.project_root / "ue_assets"
        self.ue_assets.mkdir(exist_ok=True)
        
        # Ensure bridge directories exist
        (self.ue_bridge / "inbox").mkdir(parents=True, exist_ok=True)
        (self.ue_bridge / "outbox").mkdir(parents=True, exist_ok=True)
    
    def import_ai_asset_to_ue(self, fbx_path: str, asset_name: str, 
                             destination_path: str = "/Game/AI_Generated/Props") -> Dict[str, Any]:
        """
        Import AI-generated FBX asset into Unreal Engine
        Uses the existing UE bridge system
        """
        
        command = {
            "action": "import_asset",
            "payload": {
                "source_file": str(Path(fbx_path).absolute()),
                "destination_path": destination_path,
                "asset_name": asset_name,
                "import_settings": {
                    "auto_generate_collision": True,
                    "combine_meshes": False,
                    "import_materials": True,
                    "import_textures": True,
                    "recompute_normals": False,
                    "recompute_tangents": True
                }
            }
        }
        
        return self._send_ue_command(command)
    
    def create_level_sequence(self, sequence_name: str, asset_path: str,
                             animation_duration: float = 5.0) -> Dict[str, Any]:
        """
        Create a level sequence with the AI-generated asset
        Similar to the van animation in the video
        """
        
        command = {
            "action": "create_sequence_with_asset",
            "payload": {
                "sequence_name": sequence_name,
                "asset_path": asset_path,
                "duration": animation_duration,
                "camera_setup": {
                    "create_camera": True,
                    "camera_name": f"{sequence_name}_Camera",
                    "initial_location": [500, -500, 200],
                    "look_at_target": [0, 0, 0]
                },
                "animation_keyframes": [
                    {
                        "time": 0.0,
                        "location": [0, 0, 0],
                        "rotation": [0, 0, 0]
                    },
                    {
                        "time": animation_duration,
                        "location": [0, 500, 0],  # Move forward
                        "rotation": [0, 0, 0]
                    }
                ]
            }
        }
        
        return self._send_ue_command(command)
    
    def render_sequence_for_ai(self, sequence_name: str, output_path: str,
                              resolution: str = "1280x720", fps: int = 24) -> Dict[str, Any]:
        """
        Render the sequence for AI style transfer processing
        """
        
        command = {
            "action": "render_sequence",
            "payload": {
                "sequence_name": sequence_name,
                "output_path": output_path,
                "settings": {
                    "resolution": resolution,
                    "frame_rate": fps,
                    "quality": "high",
                    "format": "mp4",
                    "anti_aliasing": "temporal"
                }
            }
        }
        
        return self._send_ue_command(command)
    
    def setup_ai_workflow_scene(self, assets: List[str], scene_name: str) -> Dict[str, Any]:
        """
        Set up a complete scene with multiple AI-generated assets
        Like the van + interior components workflow
        """
        
        command = {
            "action": "setup_ai_scene",
            "payload": {
                "scene_name": scene_name,
                "assets": assets,
                "layout": "auto",  # Automatic placement
                "lighting": "cinematic",
                "environment": "/Game/Environments/Alleyway"  # Use approved Fab environment
            }
        }
        
        return self._send_ue_command(command)
    
    def full_ai_to_render_pipeline(self, asset_configs: List[Dict[str, Any]], 
                                  scene_name: str) -> Dict[str, Any]:
        """
        Complete pipeline: Import assets → Set up scene → Animate → Render
        Recreates the workflow from the video
        """
        
        results = {
            "scene_name": scene_name,
            "steps": {},
            "assets_imported": [],
            "render_output": None
        }
        
        print(f"🎬 Starting full AI-to-render pipeline for scene: {scene_name}")
        
        # Step 1: Import all AI assets
        print("1. Importing AI-generated assets...")
        for i, asset_config in enumerate(asset_configs):
            import_result = self.import_ai_asset_to_ue(
                fbx_path=asset_config["fbx_path"],
                asset_name=asset_config["name"],
                destination_path=asset_config.get("destination", "/Game/AI_Generated/Props")
            )
            results["steps"][f"import_{i}"] = import_result
            
            if import_result.get("success"):
                results["assets_imported"].append(asset_config["name"])
        
        # Step 2: Set up scene
        print("2. Setting up scene...")
        scene_result = self.setup_ai_workflow_scene(
            assets=results["assets_imported"],
            scene_name=scene_name
        )
        results["steps"]["scene_setup"] = scene_result
        
        # Step 3: Create animation sequence
        print("3. Creating animation sequence...")
        sequence_name = f"{scene_name}_Sequence"
        sequence_result = self.create_level_sequence(
            sequence_name=sequence_name,
            asset_path=f"/Game/AI_Generated/Props/{results['assets_imported'][0]}",
            animation_duration=5.0
        )
        results["steps"]["sequence_creation"] = sequence_result
        
        # Step 4: Render for AI processing
        print("4. Rendering for AI style transfer...")
        output_path = f"exports/{scene_name}_render.mp4"
        render_result = self.render_sequence_for_ai(
            sequence_name=sequence_name,
            output_path=output_path
        )
        results["steps"]["render"] = render_result
        
        if render_result.get("success"):
            results["render_output"] = output_path
        
        return results
    
    def integrate_with_comfyui_pipeline(self, render_output: str, style_image: str,
                                       workflow: str = "comfy_workflows/working_video_test.json") -> Dict[str, Any]:
        """
        Send rendered UE5 video to ComfyUI for AI style transfer
        Completes the workflow: UE5 render → AI style transfer
        """
        
        # Use the existing ComfyUI bridge
        from comfy_bridge_client import main as submit_to_comfy
        import sys
        
        # Temporarily modify sys.argv to call comfy bridge
        original_argv = sys.argv.copy()
        
        try:
            sys.argv = [
                "comfy_bridge_client.py",
                "--workflow", workflow,
                "--video_in", render_output,
                "--style_img", style_image,
                "--out_dir", "outputs/ai_styled"
            ]
            
            result = submit_to_comfy()
            
            return {
                "success": True,
                "comfyui_result": result,
                "styled_output": "outputs/ai_styled/"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"ComfyUI integration failed: {str(e)}"
            }
        finally:
            sys.argv = original_argv
    
    def _send_ue_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to Unreal Engine via bridge system"""
        
        import uuid
        import time
        
        # Generate unique command ID
        cmd_id = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
        command["id"] = cmd_id
        command["timestamp"] = time.time()
        
        # Write command to inbox
        inbox_file = self.ue_bridge / "inbox" / f"{cmd_id}.json"
        with open(inbox_file, 'w') as f:
            json.dump(command, f, indent=2)
        
        print(f"📤 Sent UE command: {command['action']} (ID: {cmd_id})")
        
        # Wait for response (with timeout)
        timeout = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            outbox_file = self.ue_bridge / "outbox" / f"{cmd_id}.json"
            
            if outbox_file.exists():
                try:
                    with open(outbox_file, 'r') as f:
                        response = json.load(f)
                    
                    print(f"📥 UE response received for: {cmd_id}")
                    return response
                    
                except json.JSONDecodeError:
                    # File might be partially written, wait a bit more
                    time.sleep(0.5)
                    continue
            
            time.sleep(1)
        
        return {
            "success": False,
            "error": f"UE command timed out after {timeout} seconds",
            "command_id": cmd_id
        }
    
    def create_van_example_workflow(self) -> Dict[str, Any]:
        """
        Create the specific van workflow from the video
        """
        
        van_assets = [
            {
                "name": "delivery_van",
                "fbx_path": "ai_generated_assets/ue_ready/delivery_van_UE.fbx",
                "destination": "/Game/AI_Generated/Vehicles"
            },
            {
                "name": "van_seats", 
                "fbx_path": "ai_generated_assets/ue_ready/van_seats_UE.fbx",
                "destination": "/Game/AI_Generated/Interiors"
            },
            {
                "name": "van_dashboard",
                "fbx_path": "ai_generated_assets/ue_ready/van_dashboard_UE.fbx", 
                "destination": "/Game/AI_Generated/Interiors"
            }
        ]
        
        return self.full_ai_to_render_pipeline(
            asset_configs=van_assets,
            scene_name="Van_Alleyway_Scene"
        )


# CLI Interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="UE5 Integration for AI-to-3D Pipeline")
    parser.add_argument("--action", required=True, 
                       choices=["import", "sequence", "render", "full-pipeline", "van-example"],
                       help="Action to perform")
    parser.add_argument("--asset-path", help="Path to FBX asset")
    parser.add_argument("--asset-name", help="Name for the asset")
    parser.add_argument("--scene-name", help="Name for the scene")
    parser.add_argument("--config", help="JSON config file for multiple assets")
    
    args = parser.parse_args()
    
    ue_integration = UE5Integration()
    
    if args.action == "import" and args.asset_path and args.asset_name:
        result = ue_integration.import_ai_asset_to_ue(args.asset_path, args.asset_name)
        
    elif args.action == "van-example":
        result = ue_integration.create_van_example_workflow()
        
    elif args.action == "full-pipeline" and args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
        result = ue_integration.full_ai_to_render_pipeline(
            config["assets"], 
            config["scene_name"]
        )
        
    else:
        print("Invalid arguments for the specified action")
        return
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()