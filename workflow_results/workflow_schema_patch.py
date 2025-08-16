#!/usr/bin/env python3
"""
ComfyUI workflow JSON patcher
- Adds required node keys: flags/order/mode/properties
- Converts legacy "pos" -> "position"
- Ensures ids are ints
- Normalizes widgets_values to list/dict (leave as-is if valid)
- Validates/repairs links: drops null/short links, reindexes link ids

Usage:
  python3 workflow_schema_patch.py input.json output.json
"""

import json
import sys
from copy import deepcopy

REQUIRED_NODE_KEYS = {
    "flags": dict,
    "order": int,
    "mode": int,
    "properties": dict,
}

def ensure_position(node):
    # ComfyUI expects "position": [x, y]
    if "position" not in node:
        if "pos" in node and isinstance(node["pos"], (list, tuple)) and len(node["pos"]) == 2:
            node["position"] = [float(node["pos"][0]), float(node["pos"][1])]
        else:
            node["position"] = [float(node.get("x", 0)), float(node.get("y", 0))]
    # cleanup legacy
    node.pop("pos", None)

def ensure_required_fields(node):
    for k, typ in REQUIRED_NODE_KEYS.items():
        if k not in node or node[k] is None:
            node[k] = typ() if typ is dict else (0 if typ is int else None)
    # normalize widgets_values
    if "widgets_values" in node:
        wv = node["widgets_values"]
        # some exports store dicts; both are accepted by Comfy as long as JSON-valid
        if wv is None:
            node["widgets_values"] = []
    else:
        node["widgets_values"] = []

    # inputs/outputs/properties must exist
    node.setdefault("inputs", [])
    node.setdefault("outputs", [])
    node.setdefault("properties", {})

def coerce_int(x, default=None):
    try:
        return int(x)
    except Exception:
        return default

def sanitize_link_tuple(link):
    """
    ComfyUI link format:
      [link_id, from_node_id, from_slot_index, to_node_id, to_slot_index, data_type]
    """
    if not isinstance(link, (list, tuple)) or len(link) < 6:
        return None
    l_id, src_id, src_slot, dst_id, dst_slot, dtype = link[:6]

    l_id = coerce_int(l_id)
    src_id = coerce_int(src_id)
    src_slot = coerce_int(src_slot)
    dst_id = coerce_int(dst_id)
    dst_slot = coerce_int(dst_slot)
    dtype = dtype if isinstance(dtype, str) else None

    if None in (l_id, src_id, src_slot, dst_id, dst_slot) or dtype is None:
        return None

    return [l_id, src_id, src_slot, dst_id, dst_slot, dtype]

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 workflow_schema_patch.py input.json output.json")
        sys.exit(2)

    src, dst = sys.argv[1], sys.argv[2]
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.setdefault("nodes", [])
    data.setdefault("links", [])
    data.setdefault("groups", [])
    data.setdefault("config", {})

    # Normalize nodes
    max_node_id = 0
    for n in data["nodes"]:
        # id/type required
        if "id" not in n:
            # try to synthesize; Comfy requires an id
            n["id"] = max_node_id + 1
        # coerce id to int
        n["id"] = coerce_int(n["id"], default=max_node_id + 1)
        max_node_id = max(max_node_id, n["id"])

        if "type" not in n or not isinstance(n["type"], str):
            # fallback to something loadable; user can fix in UI
            n["type"] = n.get("name", "Note")
        ensure_position(n)
        ensure_required_fields(n)

    # Normalize links
    clean_links = []
    for link in data["links"]:
        fixed = sanitize_link_tuple(link)
        if fixed:
            clean_links.append(fixed)

    # Reindex link ids to be consecutive (1..N)
    for i, l in enumerate(clean_links, start=1):
        l[0] = i

    data["links"] = clean_links

    # last ids
    data["last_node_id"] = max_node_id
    data["last_link_id"] = len(clean_links)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Patched workflow written to: {dst}")
    print(f"Nodes: {len(data['nodes'])} | Links: {len(data['links'])}")

if __name__ == "__main__":
    main()