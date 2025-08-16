#!/usr/bin/env python3
"""
LevlStudio MCP Server - UE5 to ComfyUI Bridge
Provides tools for one-click Unreal Engine rendering and ComfyUI style transfer
"""

import argparse, json, os, subprocess, uuid, time, pathlib, sys
from typing import Any, Dict, Optional, List

try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    print("Missing MCP server lib. Install with: pip install 'mcp[server]'")
    raise

# ---------------- Bridge queue helpers ----------------
def _ue_paths(root: str):
    base = pathlib.Path(root)
    inbox = base / "inbox"
    outbox = base / "outbox"
    inbox.mkdir(parents=True, exist_ok=True)
    outbox.mkdir(parents=True, exist_ok=True)
    return inbox, outbox

def _ue_enqueue(bridge_root: str, action: str, payload: dict) -> dict:
    inbox, _ = _ue_paths(bridge_root)
    cmd_id = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
    cmd = {"id": cmd_id, "action": action, "payload": payload, "ts": time.time()}
    path = inbox / f"{cmd_id}.json"
    path.write_text(json.dumps(cmd, indent=2), encoding="utf-8")
    return {"ok": True, "id": cmd_id, "queued": str(path)}

def _ue_fetch(bridge_root: str, cmd_id: str) -> dict:
    _, outbox = _ue_paths(bridge_root)
    res_path = outbox / f"{cmd_id}.json"
    if not res_path.exists():
        return {"ok": False, "pending": True}
    try:
        return json.loads(res_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ---------------- Comfy client helper -----------------
def _submit_to_comfy(host: str, port: int, workflow_path: str, video: str, style: str, out_dir: str) -> dict:
    import urllib.request
    wf = json.loads(pathlib.Path(workflow_path).read_text(encoding='utf-8'))
    meta = wf.get("meta", {})
    dyn = meta.get("dynamic_overrides", {})
    if video: dyn["video_path"] = video
    if style: dyn["style_image_path"] = style
    if out_dir: dyn["output_dir"] = out_dir
    meta["dynamic_overrides"] = dyn
    wf["meta"] = meta
    data = json.dumps(wf).encode('utf-8')
    url = f"http://{host}:{port}/prompt"
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        return {"ok": True, "response": body}

# ---------------- Main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--ue_bridge', default='./UnrealBridge', help='Path to UnrealBridge folder with inbox/outbox')
    ap.add_argument('--comfy_host', default='127.0.0.1')
    ap.add_argument('--comfy_port', type=int, default=8188)
    ap.add_argument('--default_workflow', default='./comfy_workflows/wanfn_depth_pose_canny_template.json')
    
    args = ap.parse_args()
    server = FastMCP('levl-ue-to-comfy')

    # 1) Build + Render (Unreal side, via file-queue to watcher)
    @server.tool()
    def ue_build_and_render(level_path: str = "/Game/Levl/Maps/Empty",
                            bp_path: str = "/Game/Levl/BP/BP_MyCone",
                            spawn_location: str = "0,0,300",
                            spawn_rotation: str = "0,0,0",
                            sequence_name: str = "Seq_OneClick",
                            output_movie_path: str = "",
                            resolution: str = "1280x720",
                            fps: int = 24) -> dict:
        """Requests Unreal to spawn a BP, create a level sequence, add a cine camera, render via MRQ."""
        payload = {
            "level_path": level_path,
            "bp_path": bp_path,
            "spawn_location": spawn_location,
            "spawn_rotation": spawn_rotation,
            "sequence_name": sequence_name,
            "output_movie_path": output_movie_path,
            "resolution": resolution,
            "fps": fps
        }
        bridge_root = os.environ.get("UE_BRIDGE", args.ue_bridge)
        return _ue_enqueue(bridge_root, "oneclick_build_and_render", payload)

    # 2) Poll Unreal result by cmd_id
    @server.tool()
    def ue_fetch_result(cmd_id: str) -> dict:
        bridge_root = os.environ.get("UE_BRIDGE", args.ue_bridge)
        return _ue_fetch(bridge_root, cmd_id)

    # 3) One-click: build+render in UE, then submit to Comfy when done
    @server.tool()
    def ue_to_comfy_oneclick(level_path: str,
                             bp_path: str,
                             output_movie_path: str,
                             style_image_path: str,
                             comfy_workflow: str = "",
                             spawn_location: str = "0,0,300",
                             spawn_rotation: str = "0,0,0",
                             sequence_name: str = "Seq_OneClick",
                             resolution: str = "1280x720",
                             fps: int = 24,
                             poll_seconds: int = 2,
                             poll_timeout_sec: int = 600,
                             output_dir: str = "outputs") -> dict:
        """End-to-end: ask UE to render, wait, then push video to ComfyUI workflow."""
        bridge_root = os.environ.get("UE_BRIDGE", args.ue_bridge)
        # Enqueue UE job
        payload = {
            "level_path": level_path, "bp_path": bp_path,
            "spawn_location": spawn_location, "spawn_rotation": spawn_rotation,
            "sequence_name": sequence_name, "output_movie_path": output_movie_path,
            "resolution": resolution, "fps": fps
        }
        enq = _ue_enqueue(bridge_root, "oneclick_build_and_render", payload)
        cmd_id = enq["id"]
        # Poll
        start = time.time()
        result_path = ""
        while True:
            res = _ue_fetch(bridge_root, cmd_id)
            if res.get("ok") and res.get("data", {}).get("movie_path"):
                result_path = res["data"]["movie_path"]
                break
            if time.time() - start > poll_timeout_sec:
                return {"ok": False, "error": "UE render timed out", "cmd_id": cmd_id}
            time.sleep(poll_seconds)
        # Submit to Comfy
        wf = comfy_workflow or os.environ.get("COMFY_WORKFLOW", args.default_workflow)
        try:
            comfy_host = os.environ.get("COMFY_HOST", args.comfy_host)
            comfy_port = int(os.environ.get("COMFY_PORT", str(args.comfy_port)))
            resp = _submit_to_comfy(comfy_host, comfy_port, wf, result_path, style_image_path, output_dir)
        except Exception as e:
            return {"ok": False, "error": f"Comfy submission failed: {e}", "movie_path": result_path}
        return {"ok": True, "movie_path": result_path, "comfy_response": resp}

    # Run
    print(f"LevlStudio UE→Comfy MCP listening on {args.host}:{args.port}")
    print(f"Bridge: {args.ue_bridge}")
    print(f"ComfyUI: {args.comfy_host}:{args.comfy_port}")
    server.run(args.host, args.port)

if __name__ == '__main__':
    main()
