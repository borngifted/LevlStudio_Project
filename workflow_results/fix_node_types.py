#!/usr/bin/env python3
"""
Fix ComfyUI workflow node types
"""
import json
import os

def fix_type(node_type):
    """Fix node type names to match actual ComfyUI nodes"""
    if node_type == "DWOpenPose_Preprocessor":
        return "DW OpenPose Preprocessor"
    if node_type == "ApplyControlNet":
        return "Apply ControlNet"  # Core ComfyUI node
    if node_type == "Apply Advanced ControlNet":
        return "Apply ControlNet"  # Fix back to core node
    if node_type == "DepthAnythingV2Preprocessor":
        return "DepthAnything V2 Preprocessor"  # Correct name from controlnet_aux
    if node_type == "CannyEdgePreprocessor":
        return "Canny Edge Preprocessor"
    if node_type == "MiDaS-DepthMapPreprocessor":
        return "DepthAnything V2 Preprocessor"  # Fix back to correct name
    return node_type

# File path
workflow_path = "/Volumes/Jul_23_2025/LevlStudio_Project/workflow_results/wan_test_single_image_fully_fixed.json"

# Backup
backup_path = workflow_path + ".bak"
if os.path.exists(workflow_path):
    with open(workflow_path, "r") as f:
        workflow_data = json.load(f)
    
    # Create backup
    with open(backup_path, "w") as f:
        json.dump(workflow_data, f, indent=2)
    print(f"✅ Backup created: {backup_path}")
    
    # Fix node types
    nodes = workflow_data.get("nodes", [])
    fixed_count = 0
    
    for node in nodes:
        if isinstance(node, dict) and "type" in node:
            original_type = node["type"]
            fixed_type = fix_type(original_type)
            if original_type != fixed_type:
                node["type"] = fixed_type
                print(f"🔧 Fixed: {original_type} → {fixed_type}")
                fixed_count += 1
    
    # Write back
    with open(workflow_path, "w") as f:
        json.dump(workflow_data, f, indent=2)
    
    print(f"✅ Patched workflow: {workflow_path}")
    print(f"📊 Fixed {fixed_count} node types")
    
else:
    print(f"❌ File not found: {workflow_path}")