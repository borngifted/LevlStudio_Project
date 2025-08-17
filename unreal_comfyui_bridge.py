#!/usr/bin/env python3
"""
Unreal Engine to ComfyUI Bridge
Direct integration for seamless UE5 → ComfyUI workflow automation
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import websocket
import uuid
import threading
from queue import Queue

class UnrealComfyUIBridge:
    def __init__(self, 
                 comfyui_host="127.0.0.1", 
                 comfyui_port=8188,
                 project_root=None):
        self.comfyui_host = comfyui_host
        self.comfyui_port = comfyui_port
        self.comfyui_url = f"http://{comfyui_host}:{comfyui_port}"
        
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.workflow_path = self.project_root / "workflow_results" / "complete_ue5_to_comfy_workflow.json"
        
        # Unreal Engine integration
        self.ue_export_path = self.project_root / "UnrealBridge" / "outbox"
        self.ue_import_path = self.project_root / "UnrealBridge" / "inbox"
        self.ue_export_path.mkdir(parents=True, exist_ok=True)
        self.ue_import_path.mkdir(parents=True, exist_ok=True)
        
        # Processing queue
        self.processing_queue = Queue()
        self.is_processing = False
        
    def check_comfyui_connection(self):
        """Check if ComfyUI is running and accessible"""
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_comfyui_if_needed(self):
        """Start ComfyUI if not running"""
        if self.check_comfyui_connection():
            print("✅ ComfyUI already running")
            return True
        
        print("🎨 Starting ComfyUI...")
        
        # Find ComfyUI installation
        comfyui_paths = [
            self.project_root / "ComfyUI",
            Path.home() / "ComfyUI" / "ComfyUI",
            Path("/Users/workofficial/ComfyUI/ComfyUI"),
        ]
        
        for comfyui_path in comfyui_paths:
            if comfyui_path.exists():
                main_py = comfyui_path / "main.py"
                if main_py.exists():
                    # Start ComfyUI in background
                    subprocess.Popen([
                        sys.executable, str(main_py), 
                        "--port", str(self.comfyui_port)
                    ], cwd=comfyui_path)
                    
                    # Wait for startup
                    for _ in range(30):  # 30 second timeout
                        time.sleep(1)
                        if self.check_comfyui_connection():
                            print("✅ ComfyUI started successfully")
                            return True
                    
                    print("❌ ComfyUI failed to start")
                    return False
        
        print("❌ ComfyUI not found")
        return False
    
    def load_workflow_template(self):
        """Load the UE5 → ComfyUI workflow template"""
        try:
            with open(self.workflow_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load workflow: {e}")
            return None
    
    def update_workflow_for_sequence(self, workflow: Dict, 
                                   input_path: str, 
                                   output_prefix: str = "ue_stylized",
                                   frame_pattern: str = "frame_%05d.png"):
        """Update workflow for specific image sequence"""
        
        # Find Load Image Batch node
        for node in workflow.get("nodes", []):
            if node.get("type") == "Load Image (Batch)":
                node["widgets_values"] = [
                    input_path,
                    frame_pattern,
                    False  # index_mode
                ]
                print(f"📁 Set input path: {input_path}")
            
            # Update Save Image node
            elif node.get("type") == "Save Image":
                node["widgets_values"] = [output_prefix]
                print(f"💾 Set output prefix: {output_prefix}")
        
        return workflow
    
    def submit_workflow_to_comfyui(self, workflow: Dict):
        """Submit workflow to ComfyUI for processing"""
        try:
            # Generate unique prompt ID
            prompt_id = str(uuid.uuid4())
            
            # Submit workflow
            response = requests.post(
                f"{self.comfyui_url}/prompt",
                json={"prompt": workflow, "client_id": prompt_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get("prompt_id")
                print(f"✅ Workflow submitted: {prompt_id}")
                return prompt_id
            else:
                print(f"❌ Failed to submit workflow: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error submitting workflow: {e}")
            return None
    
    def monitor_workflow_progress(self, prompt_id: str):
        """Monitor workflow execution progress"""
        print(f"🔍 Monitoring workflow: {prompt_id}")
        
        try:
            # Connect to ComfyUI WebSocket for progress updates
            ws_url = f"ws://{self.comfyui_host}:{self.comfyui_port}/ws?clientId={prompt_id}"
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "progress":
                        progress_data = data.get("data", {})
                        value = progress_data.get("value", 0)
                        max_value = progress_data.get("max", 100)
                        percentage = (value / max_value) * 100 if max_value > 0 else 0
                        print(f"📈 Progress: {percentage:.1f}% ({value}/{max_value})")
                    
                    elif msg_type == "executed":
                        node_id = data.get("data", {}).get("node")
                        print(f"✅ Node {node_id} executed")
                    
                    elif msg_type == "execution_start":
                        print("🚀 Execution started")
                    
                    elif msg_type == "execution_success":
                        print("🎉 Execution completed successfully!")
                        ws.close()
                    
                    elif msg_type == "execution_error":
                        error_data = data.get("data", {})
                        print(f"❌ Execution error: {error_data}")
                        ws.close()
                        
                except Exception as e:
                    print(f"Error parsing message: {e}")
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print("🔌 WebSocket connection closed")
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in separate thread
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error monitoring workflow: {e}")
            return False
    
    def process_unreal_sequence(self, 
                              sequence_name: str,
                              input_folder: str,
                              frame_pattern: str = "frame_%05d.png",
                              output_prefix: str = None):
        """Process image sequence from Unreal Engine"""
        
        if not output_prefix:
            output_prefix = f"stylized_{sequence_name}"
        
        print(f"🎬 Processing Unreal sequence: {sequence_name}")
        print(f"📁 Input: {input_folder}")
        print(f"💾 Output prefix: {output_prefix}")
        
        # Load workflow template
        workflow = self.load_workflow_template()
        if not workflow:
            return False
        
        # Update workflow for this sequence
        workflow = self.update_workflow_for_sequence(
            workflow, input_folder, output_prefix, frame_pattern
        )
        
        # Submit to ComfyUI
        prompt_id = self.submit_workflow_to_comfyui(workflow)
        if not prompt_id:
            return False
        
        # Monitor progress
        self.monitor_workflow_progress(prompt_id)
        
        return True
    
    def watch_unreal_export_folder(self):
        """Watch Unreal export folder for new sequences"""
        print(f"👁️  Watching Unreal export folder: {self.ue_export_path}")
        
        processed_folders = set()
        
        while True:
            try:
                # Check for new folders
                for item in self.ue_export_path.iterdir():
                    if item.is_dir() and item.name not in processed_folders:
                        # Check if folder contains image files
                        image_files = list(item.glob("*.png")) + list(item.glob("*.jpg"))
                        
                        if image_files:
                            print(f"📁 New sequence detected: {item.name}")
                            
                            # Add to processing queue
                            self.processing_queue.put({
                                "sequence_name": item.name,
                                "input_folder": str(item),
                                "frame_pattern": "frame_%05d.png"
                            })
                            
                            processed_folders.add(item.name)
                
                # Process queue
                if not self.processing_queue.empty() and not self.is_processing:
                    self.process_queue_item()
                
                time.sleep(2)  # Check every 2 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping Unreal export watcher")
                break
            except Exception as e:
                print(f"❌ Error watching folder: {e}")
                time.sleep(5)
    
    def process_queue_item(self):
        """Process next item in queue"""
        if self.processing_queue.empty():
            return
        
        self.is_processing = True
        
        try:
            item = self.processing_queue.get()
            success = self.process_unreal_sequence(
                item["sequence_name"],
                item["input_folder"],
                item["frame_pattern"]
            )
            
            if success:
                print(f"✅ Completed processing: {item['sequence_name']}")
            else:
                print(f"❌ Failed processing: {item['sequence_name']}")
                
        finally:
            self.is_processing = False
    
    def create_unreal_python_script(self):
        """Create Unreal Engine Python script for integration"""
        ue_script = '''
import unreal
import os
from pathlib import Path

class LevlStudioUnrealBridge:
    def __init__(self):
        self.project_root = Path(r"{project_root}")
        self.export_path = self.project_root / "UnrealBridge" / "outbox"
        self.import_path = self.project_root / "UnrealBridge" / "inbox"
        
        # Ensure paths exist
        self.export_path.mkdir(parents=True, exist_ok=True)
        self.import_path.mkdir(parents=True, exist_ok=True)
    
    def export_sequence_for_comfyui(self, sequence_name, level_sequence, camera_binding=None):
        """Export level sequence as image sequence for ComfyUI processing"""
        
        # Set up export path
        export_folder = self.export_path / sequence_name
        export_folder.mkdir(exist_ok=True)
        
        # Configure movie pipeline
        movie_pipeline = unreal.MoviePipelineQueueEngineSubsystem.get_queue_subsystem()
        queue = movie_pipeline.get_queue()
        
        # Create job
        job = queue.allocate_new_job(unreal.MoviePipelinePythonHostJob)
        job.set_configuration(self.create_export_config(str(export_folder)))
        
        # Set sequence
        job.sequence = unreal.SoftObjectPath(level_sequence.get_path_name())
        
        # Execute job
        movie_pipeline.render_queue_with_executor_instance(
            unreal.MoviePipelinePythonHostExecutor
        )
        
        print(f"Exported sequence to: {{export_folder}}")
        return str(export_folder)
    
    def create_export_config(self, output_path):
        """Create movie pipeline configuration for ComfyUI export"""
        config = unreal.MoviePipelineMasterConfig()
        
        # Output settings
        output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        output_setting.output_directory = unreal.DirectoryPath(output_path)
        output_setting.file_name_format = "frame_{{frame_number:05d}}"
        
        # Image sequence settings
        image_output = config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
        image_output.set_editor_property("output_format", unreal.EImageFormat.PNG)
        
        # Camera settings
        camera_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineCameraSetting)
        camera_setting.set_editor_property("override_camera_settings", True)
        
        # Anti-aliasing (important for ComfyUI)
        aa_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        aa_setting.set_editor_property("spatial_sample_count", 1)
        aa_setting.set_editor_property("temporal_sample_count", 1)
        
        # Console variables (disable auto-exposure, motion blur)
        console_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
        console_vars = [
            {{"name": "r.DefaultFeature.AutoExposure", "value": "0"}},
            {{"name": "r.DefaultFeature.MotionBlur", "value": "0"}},
            {{"name": "r.PostProcessAAQuality", "value": "6"}},
            {{"name": "r.TemporalAA.Upsampling", "value": "0"}}
        ]
        
        for var in console_vars:
            console_setting.console_variables.add_item(
                unreal.MoviePipelineConsoleVariableEntry(var["name"], var["value"])
            )
        
        return config
    
    def import_stylized_sequence(self, sequence_name):
        """Import stylized sequence back into Unreal"""
        
        # Look for processed images
        processed_folder = self.import_path / sequence_name
        if not processed_folder.exists():
            print(f"No processed sequence found: {{sequence_name}}")
            return None
        
        # Import image sequence
        import_task = unreal.AssetImportTask()
        import_task.set_editor_property("automated", True)
        import_task.set_editor_property("destination_path", f"/Game/LevlStudio/Stylized/{{sequence_name}}")
        import_task.set_editor_property("filename", str(processed_folder))
        import_task.set_editor_property("replace_existing", True)
        import_task.set_editor_property("save", True)
        
        # Execute import
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
        
        print(f"Imported stylized sequence: {{sequence_name}}")
        return import_task.get_editor_property("imported_object_paths")

# Example usage:
# bridge = LevlStudioUnrealBridge()
# bridge.export_sequence_for_comfyui("my_sequence", my_level_sequence)
        '''.format(project_root=str(self.project_root).replace("\\", "\\\\"))
        
        ue_script_path = self.project_root / "UE_Content_Python" / "levlstudio_bridge.py"
        ue_script_path.parent.mkdir(exist_ok=True)
        
        with open(ue_script_path, 'w') as f:
            f.write(ue_script)
        
        print(f"✅ Created Unreal Python script: {ue_script_path}")
        return ue_script_path

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Unreal → ComfyUI Bridge")
    parser.add_argument("--watch", action="store_true", help="Watch for Unreal exports")
    parser.add_argument("--process", type=str, help="Process specific folder")
    parser.add_argument("--start-comfyui", action="store_true", help="Start ComfyUI if needed")
    parser.add_argument("--create-ue-script", action="store_true", help="Create Unreal Python script")
    
    args = parser.parse_args()
    
    bridge = UnrealComfyUIBridge()
    
    if args.start_comfyui:
        bridge.start_comfyui_if_needed()
    
    if args.create_ue_script:
        bridge.create_unreal_python_script()
    
    if args.process:
        bridge.process_unreal_sequence(
            Path(args.process).name,
            args.process
        )
    
    if args.watch:
        if not bridge.check_comfyui_connection():
            print("❌ ComfyUI not running. Start with --start-comfyui")
            return
        
        bridge.watch_unreal_export_folder()

if __name__ == "__main__":
    main()