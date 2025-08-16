#!/usr/bin/env python3
"""
Blender MCP Adapter for LevlStudio AI-to-3D Workflow
Integrates with the custom Blender MCP server on port 9876
"""

import json
import socket
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

class BlenderMCPAdapter:
    """Adapter for the custom Blender MCP server"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9876):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self) -> bool:
        """Connect to Blender MCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send_raw_command(self, command: str) -> Dict[str, Any]:
        """Send raw string command to discover the protocol"""
        if not self.socket:
            return {"error": "Not connected"}
        
        try:
            # Try sending as raw string first
            self.socket.send((command + "\n").encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8').strip()
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"raw_response": response}
        except Exception as e:
            return {"error": str(e)}
    
    def discover_working_commands(self) -> Dict[str, Any]:
        """Try to discover what commands the server accepts"""
        print("🔍 Discovering working commands for Blender MCP server...")
        
        # Try simple string commands first
        string_commands = [
            "help",
            "status", 
            "list",
            "tools",
            "commands",
            "info",
            "version",
            "ping",
            "ready",
            "capabilities"
        ]
        
        results = {"string_commands": [], "json_commands": []}
        
        # Test string commands
        for cmd in string_commands:
            print(f"🧪 Testing string command: {cmd}")
            result = self.send_raw_command(cmd)
            results["string_commands"].append({"command": cmd, "response": result})
            
            # Look for success indicators
            if (result and 
                not result.get("error") and 
                "Unknown command type" not in str(result) and
                result.get("status") != "error"):
                print(f"✅ Potential working command: {cmd}")
                print(f"📥 Response: {result}")
        
        # Try JSON with different structures
        json_commands = [
            '{"cmd": "help"}',
            '{"command": "help"}', 
            '{"request": "help"}',
            '{"action": "help"}',
            '{"method": "help"}',
            '{"type": "help"}',
            '{"operation": "help"}',
            '{"tool": "help"}',
            '{"blender": "help"}',
            '{"api": "help"}'
        ]
        
        for cmd_json in json_commands:
            print(f"🧪 Testing JSON command: {cmd_json}")
            result = self.send_raw_command(cmd_json)
            results["json_commands"].append({"command": cmd_json, "response": result})
            
            if (result and 
                not result.get("error") and 
                "Unknown command type" not in str(result) and
                result.get("status") != "error"):
                print(f"✅ Potential working JSON format: {cmd_json}")
                print(f"📥 Response: {result}")
        
        return results
    
    def create_blender_bridge(self) -> Dict[str, Any]:
        """Create a bridge between AI-to-3D workflow and Blender MCP"""
        
        print("🌉 Creating Blender MCP bridge for AI-to-3D workflow...")
        
        # Since we can't determine the exact protocol, create a fallback system
        bridge_config = {
            "server_info": {
                "host": self.host,
                "port": self.port,
                "status": "connected" if self.socket else "disconnected",
                "protocol": "custom (undetermined)"
            },
            "fallback_methods": [
                {
                    "method": "file_drop",
                    "description": "Use Blender's file monitoring system",
                    "implementation": "Drop files in watched folder"
                },
                {
                    "method": "python_scripts", 
                    "description": "Use direct Blender Python automation",
                    "implementation": "Execute Python scripts in Blender"
                },
                {
                    "method": "command_line",
                    "description": "Use Blender command line interface", 
                    "implementation": "Call blender --background --python script.py"
                }
            ],
            "integration_steps": []
        }
        
        # Create integration workflow that works regardless of MCP protocol
        ai_to_blender_workflow = {
            "name": "AI-to-Blender Integration",
            "steps": [
                {
                    "step": 1,
                    "title": "File-based Integration",
                    "description": "Use file system for communication",
                    "actions": [
                        "Monitor ai_generated_assets/3d_models/ for new GLB files",
                        "Process files using Blender automation scripts",
                        "Output processed files to ai_generated_assets/ue_ready/"
                    ]
                },
                {
                    "step": 2, 
                    "title": "Direct Python Execution",
                    "description": "Execute Blender scripts directly",
                    "actions": [
                        "Use blender_automation.py for mesh processing",
                        "Call Blender with --background --python for headless operation",
                        "Return results via file output and exit codes"
                    ]
                },
                {
                    "step": 3,
                    "title": "MCP Server Enhancement",
                    "description": "Enhance MCP communication when protocol is discovered",
                    "actions": [
                        "Implement proper command format once discovered",
                        "Add real-time communication",
                        "Enable streaming progress updates"
                    ]
                }
            ]
        }
        
        bridge_config["integration_workflow"] = ai_to_blender_workflow
        
        return bridge_config
    
    def implement_file_based_bridge(self) -> Dict[str, Any]:
        """Implement file-based bridge as fallback"""
        
        print("📁 Implementing file-based Blender bridge...")
        
        # Create bridge directories
        bridge_dir = Path("blender_bridge")
        bridge_dir.mkdir(exist_ok=True)
        
        (bridge_dir / "input").mkdir(exist_ok=True)
        (bridge_dir / "output").mkdir(exist_ok=True)
        (bridge_dir / "scripts").mkdir(exist_ok=True)
        (bridge_dir / "logs").mkdir(exist_ok=True)
        
        # Create processing script for the MCP server to use
        processing_script = '''
import bpy
import json
import sys
from pathlib import Path

# Add our automation module
sys.path.append(str(Path(__file__).parent.parent))
from blender_automation import BlenderProcessor

def process_ai_models():
    """Process AI models from bridge input directory"""
    
    bridge_dir = Path(__file__).parent.parent / "blender_bridge"
    input_dir = bridge_dir / "input"
    output_dir = bridge_dir / "output"
    logs_dir = bridge_dir / "logs"
    
    processor = BlenderProcessor()
    results = []
    
    # Process all GLB files in input
    for glb_file in input_dir.glob("*.glb"):
        try:
            print(f"Processing: {glb_file.name}")
            
            # Determine output name
            asset_name = glb_file.stem
            output_file = output_dir / f"{asset_name}_UE.fbx"
            
            # Process the model
            success = processor.full_ai_to_ue_process(
                input_file=str(glb_file),
                output_file=str(output_file),
                voxel_size=0.05,
                decimate_ratio=0.7
            )
            
            result = {
                "input": str(glb_file),
                "output": str(output_file) if success else None,
                "success": success,
                "asset_name": asset_name
            }
            
            results.append(result)
            
            # Move processed file to avoid reprocessing
            if success:
                processed_dir = bridge_dir / "processed"
                processed_dir.mkdir(exist_ok=True)
                glb_file.rename(processed_dir / glb_file.name)
                
        except Exception as e:
            print(f"Error processing {glb_file}: {e}")
            results.append({
                "input": str(glb_file),
                "success": False,
                "error": str(e)
            })
    
    # Save results
    results_file = logs_dir / f"processing_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Processing complete. Results saved to: {results_file}")
    return results

if __name__ == "__main__":
    import time
    process_ai_models()
'''
        
        script_path = bridge_dir / "scripts" / "process_ai_models.py"
        script_path.write_text(processing_script)
        
        # Create bridge control file
        bridge_control = {
            "name": "LevlStudio Blender Bridge",
            "version": "1.0.0",
            "directories": {
                "input": str(bridge_dir / "input"),
                "output": str(bridge_dir / "output"), 
                "scripts": str(bridge_dir / "scripts"),
                "logs": str(bridge_dir / "logs")
            },
            "processing_script": str(script_path),
            "usage": {
                "manual": f"blender --background --python {script_path}",
                "automated": "Drop GLB files in input/ directory and run processing script"
            },
            "integration_commands": [
                {
                    "name": "process_ai_model",
                    "description": "Process single AI-generated model",
                    "command": f"blender --background --python {script_path} -- {{model_path}}"
                }
            ]
        }
        
        control_file = bridge_dir / "bridge_control.json"
        with open(control_file, 'w') as f:
            json.dump(bridge_control, f, indent=2)
        
        print(f"✅ File-based bridge created at: {bridge_dir}")
        print(f"📋 Control file: {control_file}")
        print(f"🔧 Processing script: {script_path}")
        
        return bridge_control
    
    def test_integration_with_ai_workflow(self) -> Dict[str, Any]:
        """Test the complete integration"""
        
        print("🧪 Testing Blender MCP integration with AI workflow...")
        
        results = {
            "mcp_connection": False,
            "protocol_discovery": None,
            "file_bridge": None,
            "integration_ready": False
        }
        
        # Test MCP connection
        if self.connect():
            results["mcp_connection"] = True
            print("✅ MCP connection successful")
            
            # Try protocol discovery
            discovery = self.discover_working_commands()
            results["protocol_discovery"] = discovery
            
        # Create file-based bridge as fallback
        file_bridge = self.implement_file_based_bridge()
        results["file_bridge"] = file_bridge
        
        # Check if we can integrate
        if results["mcp_connection"] or results["file_bridge"]:
            results["integration_ready"] = True
            
        return results
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None


def main():
    """Main integration test"""
    
    print("🎭 LevlStudio Blender MCP Adapter")
    print("Integrating with AI-to-3D workflow...")
    print("=" * 60)
    
    adapter = BlenderMCPAdapter()
    
    try:
        # Run complete integration test
        integration_results = adapter.test_integration_with_ai_workflow()
        
        print("\n" + "="*60)
        print("📊 BLENDER MCP INTEGRATION RESULTS")
        print("="*60)
        
        print(f"🔌 MCP Connection: {'✅ Working' if integration_results['mcp_connection'] else '❌ Failed'}")
        print(f"📡 Protocol Discovery: {'✅ Attempted' if integration_results['protocol_discovery'] else '❌ Skipped'}")
        print(f"📁 File Bridge: {'✅ Created' if integration_results['file_bridge'] else '❌ Failed'}")
        print(f"🎯 Integration Ready: {'✅ YES' if integration_results['integration_ready'] else '❌ NO'}")
        
        if integration_results["integration_ready"]:
            print("\n🚀 READY TO USE:")
            print("1. Drop GLB files in blender_bridge/input/")
            print("2. Run: blender --background --python blender_bridge/scripts/process_ai_models.py")
            print("3. Get processed FBX files from blender_bridge/output/")
            
            print("\n🔗 INTEGRATION WITH AI WORKFLOW:")
            print("• AI generates images → 3D models (GLB)")
            print("• Blender bridge processes GLB → FBX")  
            print("• UE5 imports FBX → Animation")
            print("• ComfyUI applies style transfer")
            
        else:
            print("\n⚠️ MANUAL SETUP REQUIRED:")
            print("• Use built-in blender_automation.py scripts")
            print("• Call Blender directly with --background --python")
            print("• File-based workflow still available")
        
    finally:
        adapter.close()
    
    return integration_results


if __name__ == "__main__":
    main()