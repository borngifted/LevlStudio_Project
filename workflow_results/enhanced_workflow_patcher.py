#!/usr/bin/env python3
"""
Enhanced ComfyUI workflow JSON patcher
- Fixes ALL schema issues including null links
- Adds missing required fields to ALL nodes
- Removes invalid links entirely
- Creates clean, loadable workflow

Usage:
  python3 enhanced_workflow_patcher.py input.json output.json
"""

import json
import sys
from copy import deepcopy

def ensure_node_schema(node):
    """Ensure node has all required schema fields"""
    # Required fields that must exist
    required_fields = {
        "flags": {},
        "order": 0,
        "mode": 0,
        "properties": {},
        "inputs": [],
        "outputs": []
    }
    
    for field, default_value in required_fields.items():
        if field not in node or node[field] is None:
            node[field] = default_value
    
    # Ensure position exists (legacy pos -> position)
    if "position" not in node:
        if "pos" in node and isinstance(node["pos"], (list, tuple)) and len(node["pos"]) >= 2:
            node["position"] = [float(node["pos"][0]), float(node["pos"][1])]
        else:
            node["position"] = [0.0, 0.0]
    
    # Remove legacy pos field
    node.pop("pos", None)
    
    # Ensure widgets_values is valid
    if "widgets_values" not in node or node["widgets_values"] is None:
        node["widgets_values"] = []
    
    # Ensure id is integer
    if "id" in node:
        try:
            node["id"] = int(node["id"])
        except (ValueError, TypeError):
            pass
    
    # Ensure type is string
    if "type" not in node or not isinstance(node["type"], str):
        node["type"] = "Note"

def clean_links(links):
    """Remove all invalid/null links entirely"""
    clean_links = []
    
    for link in links:
        # Skip if not a list/tuple or wrong length
        if not isinstance(link, (list, tuple)) or len(link) < 6:
            continue
        
        # Check for null values in critical positions
        link_id, src_node, src_slot, dst_node, dst_slot, data_type = link[:6]
        
        # Skip if any critical field is null
        if any(x is None for x in [link_id, src_node, src_slot, dst_node, dst_slot, data_type]):
            continue
        
        # Try to convert to proper types
        try:
            clean_link = [
                int(link_id),
                int(src_node),
                int(src_slot),
                int(dst_node),
                int(dst_slot),
                str(data_type)
            ]
            clean_links.append(clean_link)
        except (ValueError, TypeError):
            # Skip invalid links
            continue
    
    # Renumber link IDs consecutively
    for i, link in enumerate(clean_links, start=1):
        link[0] = i
    
    return clean_links

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 enhanced_workflow_patcher.py input.json output.json")
        sys.exit(2)
    
    src, dst = sys.argv[1], sys.argv[2]
    
    try:
        with open(src, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {src}: {e}")
        sys.exit(1)
    
    # Ensure top-level structure
    data.setdefault("nodes", [])
    data.setdefault("links", [])
    data.setdefault("groups", [])
    data.setdefault("config", {})
    
    # Fix all nodes
    max_node_id = 0
    for i, node in enumerate(data["nodes"]):
        # Ensure node has ID
        if "id" not in node:
            node["id"] = i + 1
        
        try:
            node_id = int(node["id"])
            max_node_id = max(max_node_id, node_id)
        except (ValueError, TypeError):
            node["id"] = i + 1
            max_node_id = max(max_node_id, i + 1)
        
        # Apply all schema fixes
        ensure_node_schema(node)
    
    # Clean links (remove all invalid/null links)
    data["links"] = clean_links(data["links"])
    
    # Update metadata
    data["last_node_id"] = max_node_id
    data["last_link_id"] = len(data["links"])
    
    # Write fixed workflow
    try:
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Enhanced patched workflow written to: {dst}")
        print(f"📊 Nodes: {len(data['nodes'])} | Valid Links: {len(data['links'])}")
        print("🔗 Note: Invalid/null links were removed - you may need to reconnect some nodes in ComfyUI")
        
    except Exception as e:
        print(f"Error writing {dst}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()