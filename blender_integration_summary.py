#!/usr/bin/env python3
"""
Blender Integration Summary for LevlStudio
Provides multiple ways to integrate with Blender for the AI-to-3D workflow
"""

import json
from pathlib import Path

def create_blender_integration_options():
    """Create comprehensive Blender integration options"""
    
    integration_options = {
        "title": "LevlStudio Blender Integration Options",
        "blender_mcp_server": {
            "status": "detected_on_port_9876",
            "connection": "tcp_responsive_but_custom_protocol",
            "recommendation": "file_based_bridge_created"
        },
        "integration_methods": [
            {
                "method": "1. File-Based Bridge (RECOMMENDED)",
                "description": "Drop files, run script, get results",
                "setup": "Already created in blender_bridge/ directory",
                "usage": [
                    "1. Drop GLB files in blender_bridge/input/",
                    "2. Run: blender --background --python blender_bridge/scripts/process_ai_models.py",
                    "3. Get FBX files from blender_bridge/output/"
                ],
                "pros": ["Simple", "Reliable", "No protocol issues"],
                "status": "✅ READY"
            },
            {
                "method": "2. Direct Python Scripts",
                "description": "Use blender_automation.py directly",
                "usage": [
                    "blender --background --python blender_automation.py -- process input.glb output.fbx"
                ],
                "pros": ["Direct control", "Custom parameters"],
                "status": "✅ READY"
            },
            {
                "method": "3. MCP Server Integration", 
                "description": "Direct connection to Blender MCP on port 9876",
                "setup": "Custom protocol needs discovery",
                "usage": ["Need to determine correct command format"],
                "pros": ["Real-time", "Programmatic control"],
                "status": "⚠️ NEEDS PROTOCOL DISCOVERY"
            },
            {
                "method": "4. AI-to-3D Complete Pipeline",
                "description": "Integrated workflow with all tools",
                "usage": ["python3 complete_ai_to_3d_workflow.py"],
                "pros": ["End-to-end automation", "All steps included"],
                "status": "✅ READY"
            }
        ],
        "quick_start": {
            "for_van_example": [
                "1. Run: python3 complete_ai_to_3d_workflow.py",
                "2. Get concept images from ai_generated_assets/concept_images/",
                "3. Upload to Tripo3D/Meshy to get GLB files",
                "4. Use file-based bridge or direct scripts to process in Blender",
                "5. Import FBX to UE5 and animate",
                "6. Apply AI style transfer with ComfyUI"
            ]
        }
    }
    
    return integration_options

def main():
    """Display integration summary"""
    
    print("🎭 LevlStudio Blender Integration Summary")
    print("=" * 60)
    
    options = create_blender_integration_options()
    
    print(f"📊 Blender MCP Server Status:")
    mcp_info = options["blender_mcp_server"]
    print(f"   Port 9876: {mcp_info['status']}")
    print(f"   Connection: {mcp_info['connection']}")
    print(f"   Solution: {mcp_info['recommendation']}")
    
    print(f"\n🔧 Available Integration Methods:")
    for method in options["integration_methods"]:
        print(f"\n{method['method']} {method['status']}")
        print(f"   📝 {method['description']}")
        if 'usage' in method:
            print(f"   🚀 Usage:")
            for usage_step in method['usage']:
                print(f"      {usage_step}")
    
    print(f"\n⚡ Quick Start for Van Example:")
    for step in options["quick_start"]["for_van_example"]:
        print(f"   {step}")
    
    print(f"\n🎯 RECOMMENDED WORKFLOW:")
    print("   1. ✅ Use complete_ai_to_3d_workflow.py for full pipeline")
    print("   2. ✅ Use file-based bridge for Blender processing")
    print("   3. ✅ Use existing ComfyUI integration for style transfer")
    print("   4. 🔍 Explore MCP protocol for advanced integration")
    
    # Save integration summary
    summary_file = Path("blender_integration_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(options, f, indent=2)
    
    print(f"\n📁 Full summary saved to: {summary_file}")
    print("🎉 Blender integration ready for AI-to-3D workflow!")

if __name__ == "__main__":
    main()